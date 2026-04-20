from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.remote_agent import RemoteAgent
from app.schemas.remote_agent import (
    RemoteAgentCreate, RemoteAgentUpdate, RemoteAgentResponse,
    HealthCheckResponse, AgentChatRequest, AgentChatResponse
)
import httpx
import json
import asyncio

router = APIRouter()


# --- Remote Agents CRUD ---


@router.get("/remote-agents", response_model=List[RemoteAgentResponse])
def list_remote_agents(db: Session = Depends(get_db)):
    """List all registered remote agents."""
    agents = db.query(RemoteAgent).filter(
        RemoteAgent.archived_at.is_(None)
    ).all()
    return agents


@router.post("/remote-agents", response_model=RemoteAgentResponse, status_code=status.HTTP_201_CREATED)
def register_remote_agent(
    data: RemoteAgentCreate,
    db: Session = Depends(get_db)
):
    """Register a new remote agent."""
    # Check if name already exists
    existing = db.query(RemoteAgent).filter(
        RemoteAgent.name == data.name,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Remote agent with name '{data.name}' already exists"
        )

    agent = RemoteAgent(**data.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.get("/remote-agents/{agent_id}", response_model=RemoteAgentResponse)
def get_remote_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get a remote agent by ID."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )
    return agent


@router.put("/remote-agents/{agent_id}", response_model=RemoteAgentResponse)
def update_remote_agent(
    agent_id: str,
    data: RemoteAgentUpdate,
    db: Session = Depends(get_db)
):
    """Update a remote agent."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(agent, field):
            setattr(agent, field, value)

    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/remote-agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def unregister_remote_agent(agent_id: str, db: Session = Depends(get_db)):
    """Unregister (archive) a remote agent."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    agent.archived_at = datetime.utcnow()
    db.commit()
    return None


# --- Health Check ---


async def _check_agent_health(agent: RemoteAgent) -> tuple[str, int | None, str | None]:
    """Internal health check function."""
    health_url = f"{agent.endpoint_url.rstrip('/')}{agent.health_check_path}"
    start_time = datetime.now(timezone.utc)

    try:
        timeout = httpx.Timeout(5.0, connect=2.0)
        headers = {}
        if agent.api_key:
            headers["Authorization"] = f"Bearer {agent.api_key}"

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(health_url, headers=headers)
            response.raise_for_status()

        response_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        return "online", response_time, None
    except httpx.HTTPStatusError as e:
        return "error", None, f"HTTP {e.response.status_code}"
    except httpx.TimeoutException:
        return "offline", None, "Connection timeout"
    except Exception as e:
        return "error", None, str(e)


@router.post("/remote-agents/{agent_id}/health", response_model=HealthCheckResponse)
async def check_agent_health(agent_id: str, db: Session = Depends(get_db)):
    """Trigger a health check for a specific agent."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    status_str, response_time, message = await _check_agent_health(agent)
    agent.status = status_str
    agent.last_health_check = datetime.utcnow()
    db.commit()

    return HealthCheckResponse(
        status=status_str,
        response_time_ms=response_time,
        last_health_check=agent.last_health_check,
        message=message
    )


@router.post("/remote-agents/health/all")
async def check_all_agents_health(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger health checks for all agents (background task)."""
    agents = db.query(RemoteAgent).filter(
        RemoteAgent.archived_at.is_(None)
    ).all()

    async def check_all():
        for agent in agents:
            status_str, _, _ = await _check_agent_health(agent)
            agent.status = status_str
            agent.last_health_check = datetime.utcnow()
        db.commit()

    background_tasks.add_task(lambda: asyncio.create_task(check_all()))
    return {"status": "started", "count": len(agents)}


# --- Chat ---


@router.post("/remote-agents/{agent_id}/chat", response_model=AgentChatResponse)
async def send_chat_message(
    agent_id: str,
    request: AgentChatRequest,
    db: Session = Depends(get_db)
):
    """Send a chat message to a remote agent."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    if agent.status != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is not online"
        )

    # Send message to agent endpoint
    chat_url = f"{agent.endpoint_url.rstrip('/')}/chat"
    headers = {"Content-Type": "application/json"}
    if agent.api_key:
        headers["Authorization"] = f"Bearer {agent.api_key}"

    try:
        timeout = httpx.Timeout(60.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                chat_url,
                headers=headers,
                json={
                    "message": request.message,
                    "thread_id": request.thread_id,
                    **(request.config or {})
                }
            )
            response.raise_for_status()
            result = response.json()

        thread_id = result.get("thread_id", request.thread_id or f"thread-{agent_id}-{int(datetime.utcnow().timestamp())}")

        return AgentChatResponse(
            response=result.get("response", result.get("message", "No response")),
            thread_id=thread_id,
            agent_id=agent.id,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to communicate with agent: {str(e)}"
        )


@router.get("/remote-agents/{agent_id}/chat/stream")
async def stream_chat_message(
    agent_id: str,
    message: str,
    thread_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Stream a chat with a remote agent using SSE."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    if agent.status != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is not online"
        )

    async def generate():
        yield f"data: {json.dumps({'type': 'status', 'content': 'connecting'})}\n\n"
        await asyncio.sleep(0.1)

        yield f"data: {json.dumps({'type': 'status', 'content': 'typing'})}\n\n"
        await asyncio.sleep(0.2)

        # Simple fallback response for now
        response = f"Received: {message}"
        for char in response:
            yield f"data: {json.dumps({'type': 'text', 'content': char})}\n\n"
            await asyncio.sleep(0.03)

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
