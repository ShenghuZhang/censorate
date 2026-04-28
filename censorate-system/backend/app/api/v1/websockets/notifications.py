"""Notification WebSocket endpoint - real-time notification delivery."""

import json
import asyncio
import logging
from typing import Set, Dict
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.notification_redis import notification_redis
from app.services.notification_service import get_notification_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Store active connections: user_id -> set of websockets
active_connections: Dict[str, Set[WebSocket]] = {}


class NotificationWebSocketManager:
    """Manage WebSocket connections for notifications."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.debug(f"WebSocket connected: user={user_id}, total={len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.debug(f"WebSocket disconnected: user={user_id}")

    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to all connections for a user."""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.debug(f"Failed to send to connection: {e}")
                    disconnected.add(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)


manager = NotificationWebSocketManager()


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(
    websocket: WebSocket,
    user_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time notifications."""
    await manager.connect(websocket, user_id)

    # Subscribe to Redis pub/sub
    try:
        # Create a separate Redis connection for pub/sub
        import redis
        from app.core.config import Settings
        settings = Settings.get()

        pubsub_client = redis.from_url(settings.NOTIFICATION_REDIS_URL)
        pubsub = pubsub_client.pubsub()
        pubsub.subscribe(f"notifications:user:{user_id}")

        # Listen for messages in background
        async def listen_for_messages():
            try:
                for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            data = json.loads(message["data"])
                            await manager.send_personal_message(data, user_id)
                        except Exception as e:
                            logger.error(f"Error processing pubsub message: {e}")
            except Exception as e:
                logger.error(f"Pubsub listener error: {e}")

        # Start listening in background
        import asyncio
        listener_task = asyncio.create_task(listen_for_messages())

        try:
            # Keep connection alive by waiting for messages from client
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            listener_task.cancel()
            manager.disconnect(websocket, user_id)
        except Exception as e:
            listener_task.cancel()
            manager.disconnect(websocket, user_id)
            logger.error(f"WebSocket error: {e}")

    except Exception as e:
        manager.disconnect(websocket, user_id)
        logger.error(f"Failed to setup WebSocket: {e}")
