"""Notification Redis client - dedicated Redis connection for notifications (DB 1)."""

import redis
import json
from typing import Any, Optional
from .config import Settings


class NotificationRedis:
    """Redis client for notification deduplication and pub/sub."""

    _instance: Optional["NotificationRedis"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if NotificationRedis._initialized:
            return
        self.settings = Settings.get()
        self.client = redis.from_url(
            self.settings.NOTIFICATION_REDIS_URL,
            max_connections=10
        )
        NotificationRedis._initialized = True

    # Deduplication methods
    def should_send_notification(self, key: str, ttl: int = 86400) -> bool:
        """
        Check if a notification should be sent (not a duplicate).

        Args:
            key: Unique key for the notification
            ttl: Time-to-live in seconds for the dedup key

        Returns:
            True if notification should be sent, False if duplicate
        """
        try:
            if self.client.exists(key):
                return False
            self.client.setex(key, ttl, "1")
            return True
        except Exception as e:
            print(f"Deduplication check failed: {e}")
            # Fail open - send notification if Redis is down
            return True

    def mark_notification_sent(self, key: str, ttl: int = 86400) -> None:
        """Mark a notification as sent without checking."""
        try:
            self.client.setex(key, ttl, "1")
        except Exception as e:
            print(f"Failed to mark notification sent: {e}")

    # Pub/Sub methods
    def publish_notification(self, user_id: str, notification_data: dict) -> None:
        """Publish a notification to a user's channel."""
        try:
            channel = f"notifications:user:{user_id}"
            self.client.publish(channel, json.dumps(notification_data))
        except Exception as e:
            print(f"Failed to publish notification: {e}")

    # Unread count cache
    def get_unread_count(self, user_id: str) -> Optional[int]:
        """Get cached unread count."""
        try:
            count = self.client.get(f"notifications:unread:{user_id}")
            return int(count) if count is not None else None
        except Exception as e:
            print(f"Failed to get unread count: {e}")
            return None

    def set_unread_count(self, user_id: str, count: int) -> None:
        """Cache unread count."""
        try:
            self.client.setex(f"notifications:unread:{user_id}", 3600, count)  # 1 hour TTL
        except Exception as e:
            print(f"Failed to set unread count: {e}")

    def increment_unread_count(self, user_id: str) -> Optional[int]:
        """Increment unread count and return new value."""
        try:
            key = f"notifications:unread:{user_id}"
            if self.client.exists(key):
                return self.client.incr(key)
            return None
        except Exception as e:
            print(f"Failed to increment unread count: {e}")
            return None

    def clear_unread_cache(self, user_id: str) -> None:
        """Clear cached unread count."""
        try:
            self.client.delete(f"notifications:unread:{user_id}")
        except Exception as e:
            print(f"Failed to clear unread cache: {e}")


# Singleton instance
notification_redis = NotificationRedis()
