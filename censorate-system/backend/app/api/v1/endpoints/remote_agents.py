from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.remote_agent import RemoteAgent
from app.schemas.remote_agent import (
    RemoteAgentCreate, RemoteAgentUpdate, RemoteAgentResponse,
    HealthCheckResponse, AgentChatRequest, AgentChatResponse,
    RemoteAgentHealthHistoryResponse, RemoteAgentWithHistoryResponse,
    AgentAcknowledgement, AgentThresholdUpdate
)
from app.services.remote_agent_service import get_remote_agent_service
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


@router.get("/remote-agents/{agent_id}/with-history", response_model=RemoteAgentWithHistoryResponse)
def get_remote_agent_with_history(
    agent_id: str,
    history_limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get a remote agent by ID with recent health history."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    service = get_remote_agent_service()
    history = service.get_health_history(db, agent_id, limit=history_limit)

    return RemoteAgentWithHistoryResponse(
        **RemoteAgentResponse.model_validate(agent).model_dump(),
        recent_health_history=history
    )


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

    service = get_remote_agent_service()
    status_str, response_time, message = await service.check_agent_health(agent)

    # Use enhanced update_agent_status that records history and manages alerts
    service.update_agent_status(db, agent, status_str, response_time, message)

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

    service = get_remote_agent_service()

    async def check_all_and_update():
        """Check all agents health in parallel and update database."""
        results = await service.check_all_agents_health(agents)
        for agent, status_str, response_time, error in results:
            # Use enhanced update that records history
            service.update_agent_status(db, agent, status_str, response_time, error)

    # Add proper background task (no lambda wrapper)
    background_tasks.add_task(check_all_and_update)

    return {"status": "started", "count": len(agents)}


# --- Health History ---


@router.get("/remote-agents/{agent_id}/health-history", response_model=List[RemoteAgentHealthHistoryResponse])
def get_agent_health_history(
    agent_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get health check history for a specific agent."""
    # Verify agent exists
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    service = get_remote_agent_service()
    history = service.get_health_history(db, agent_id, limit=limit, offset=offset)
    return history


@router.post("/remote-agents/{agent_id}/acknowledge-alert", response_model=RemoteAgentResponse)
def acknowledge_agent_alert(
    agent_id: str,
    data: AgentAcknowledgement,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert for an agent."""
    service = get_remote_agent_service()
    try:
        agent = service.acknowledge_alert(db, agent_id, data.acknowledged_by)
        return agent
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/remote-agents/{agent_id}/thresholds", response_model=RemoteAgentResponse)
def update_agent_thresholds(
    agent_id: str,
    data: AgentThresholdUpdate,
    db: Session = Depends(get_db)
):
    """Update alert thresholds for an agent."""
    service = get_remote_agent_service()
    try:
        agent = service.update_alert_thresholds(
            db,
            agent_id,
            alert_after_consecutive_failures=data.alert_after_consecutive_failures,
            alert_after_offline_minutes=data.alert_after_offline_minutes,
            warning_latency_ms=data.warning_latency_ms,
            critical_latency_ms=data.critical_latency_ms
        )
        return agent
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


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

    # Create a fresh client without http2 for better compatibility
    # (similar to health check implementation)
    try:
        timeout = httpx.Timeout(120.0, connect=5.0)
        headers = {"Content-Type": "application/json"}
        # Use the property getter which automatically decrypts
        if agent.api_key:
            headers["Authorization"] = f"Bearer {agent.api_key}"

        # Use fresh client with HTTP/2 disabled for better compatibility
        async with httpx.AsyncClient(timeout=timeout, http2=False) as client:
            # Check agent type to determine chat endpoint format
            if agent.agent_type == "hermes":
                # Hermes agent uses OpenAI compatible format
                chat_url = f"{agent.endpoint_url.rstrip('/')}/v1/chat/completions"

                # Use project_id as X-Hermes-Session-Id for continuity, fallback to thread_id
                session_id = request.project_id or request.thread_id
                if session_id:
                    headers["X-Hermes-Session-Id"] = session_id

                # Build Hermes compatible request
                hermes_request = {
                    "model": "hermes-agent",
                    "messages": [
                        {"role": "user", "content": request.message}
                    ],
                    **(request.config or {})
                }

                response = await client.post(
                    chat_url,
                    headers=headers,
                    json=hermes_request,
                    timeout=timeout
                )
                response.raise_for_status()
                result = response.json()

                # Parse OpenAI compatible response
                response_text = "No response"
                if result.get("choices") and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if choice.get("message"):
                        response_text = choice["message"].get("content", response_text)
                    elif choice.get("text"):
                        response_text = choice.get("text", response_text)

                thread_id = request.thread_id or f"thread-{agent_id}-{int(datetime.utcnow().timestamp())}"

            else:
                # Custom agent format
                chat_url = f"{agent.endpoint_url.rstrip('/')}/chat"

                response = await client.post(
                    chat_url,
                    headers=headers,
                    json={
                        "message": request.message,
                        "thread_id": request.thread_id,
                        **(request.config or {})
                    },
                    timeout=timeout
                )
                response.raise_for_status()
                result = response.json()

                response_text = result.get("response", result.get("message", "No response"))
                thread_id = result.get("thread_id", request.thread_id or f"thread-{agent_id}-{int(datetime.utcnow().timestamp())}")

            return AgentChatResponse(
                response=response_text,
                thread_id=thread_id,
                agent_id=agent.id,
                timestamp=datetime.utcnow()
            )
    except httpx.HTTPStatusError as e:
        error_detail = f"Agent returned error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            if error_data.get("error"):
                error_detail += f" - {error_data['error'].get('message', str(error_data['error']))}"
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
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
