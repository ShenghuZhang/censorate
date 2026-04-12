from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.team_member import TeamMember
from app.models.project import Project
from app.schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse,
    ThreadCreate, AgentExecutionRequest, AgentMemoryUpdate
)

router = APIRouter()


@router.get("/projects/{project_id}/agents", response_model=List[AgentResponse])
def get_agents(project_id: str, db: Session = Depends(get_db)):
    """Get all team members (humans and AI agents) for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    members = db.query(TeamMember).filter(
        TeamMember.project_id == project_id,
        TeamMember.archived_at.is_(None)
    ).all()
    return members


@router.post("/projects/{project_id}/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_ai_agent(
    project_id: str,
    data: AgentCreate,
    db: Session = Depends(get_db)
):
    """Create a new AI agent."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check if agent role already exists
    existing = db.query(TeamMember).filter(
        TeamMember.project_id == project_id,
        TeamMember.role == data.role,
        TeamMember.type == "ai",
        TeamMember.archived_at.is_(None)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent with role '{data.role}' already exists"
        )

    agent = TeamMember(
        project_id=project_id,
        name=data.name,
        nickname=data.nickname,
        role=data.role,
        type="ai",
        status="active",
        skills=data.skills,
        memory_enabled=data.memory_enabled
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.get("/agents/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get an AI agent by ID."""
    agent = db.query(TeamMember).filter(
        TeamMember.id == agent_id,
        TeamMember.type == "ai",
        TeamMember.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Agent not found"
        )
    return agent


@router.put("/agents/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: str,
    data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """Update an AI agent."""
    agent = db.query(TeamMember).filter(
        TeamMember.id == agent_id,
        TeamMember.type == "ai",
        TeamMember.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Agent not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Delete (archive) an AI agent."""
    from datetime import datetime
    agent = db.query(TeamMember).filter(
        TeamMember.id == agent_id,
        TeamMember.type == "ai"
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Agent not found"
        )
    agent.archived_at = datetime.utcnow()
    db.commit()
    return None


@router.get("/agents/{agent_id}/memory")
def get_agent_memory(agent_id: str, db: Session = Depends(get_db)):
    """Get agent memory."""
    agent = db.query(TeamMember).filter(
        TeamMember.id == agent_id,
        TeamMember.type == "ai",
        TeamMember.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Agent not found"
        )
    if not agent.memory_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Memory not enabled for this agent"
        )

    # TODO: Implement actual memory retrieval
    return {
        "agent_id": agent_id,
        "memory": {},
        "message": "Memory retrieval not yet implemented"
    }


@router.post("/agents/{agent_id}/memory")
def update_agent_memory(
    agent_id: str,
    content: AgentMemoryUpdate,
    db: Session = Depends(get_db)
):
    """Update agent memory."""
    agent = db.query(TeamMember).filter(
        TeamMember.id == agent_id,
        TeamMember.type == "ai",
        TeamMember.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Agent not found"
        )
    if not agent.memory_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Memory not enabled for this agent"
        )

    # TODO: Implement actual memory update
    return {
        "status": "success",
        "message": "Memory update not yet implemented"
    }


@router.post("/agents/{agent_id}/execute")
async def execute_agent_direct(
    agent_id: str,
    request: AgentExecutionRequest,
    db: Session = Depends(get_db)
):
    """Directly execute an AI agent."""
    agent = db.query(TeamMember).filter(
        TeamMember.id == agent_id,
        TeamMember.type == "ai",
        TeamMember.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Agent not found"
        )

    # TODO: Implement actual agent execution
    return {
        "status": "success",
        "message": "Agent execution not yet implemented",
        "agent_id": agent_id
    }


@router.post("/agents/{agent_id}/execute/stream")
async def execute_agent_stream(
    agent_id: str,
    request: AgentExecutionRequest,
    db: Session = Depends(get_db)
):
    """Execute an AI agent with streaming response."""
    from fastapi.responses import StreamingResponse
    import json

    agent = db.query(TeamMember).filter(
        TeamMember.id == agent_id,
        TeamMember.type == "ai",
        TeamMember.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Agent not found"
        )

    # TODO: Implement actual streaming execution
    async def stream_response():
        yield b'data: {"type": "status", "content": "starting"}\n\n'
        yield b'data: {"type": "status", "content": "processing"}\n\n'
        yield b'data: {"type": "text", "content": "This is a streaming response."}\n\n'
        yield b'data: {"type": "status", "content": "completed"}\n\n'
        yield b'data: [DONE]\n\n'

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream"
    )


@router.get("/requirements/{requirement_id}/transition/stream")
async def transition_with_agent_stream(
    requirement_id: str,
    to_status: str,
    thread_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Transition a requirement with agent execution and streaming response."""
    from fastapi.responses import StreamingResponse
    import json

    # TODO: Implement actual streaming transition
    async def stream_response():
        yield b'data: {"type": "status", "content": "transitioning"}}\n\n'
        yield b'data: {"type": "status", "content": "agent_executing"}]\n\n'
        yield b'data: {"type": "status", "content": "completed"}]\n\n'
        yield b'data: [DONE]\n\n'

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream"
    )
