from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


class AgentCreate(BaseModel):
    """Schema for creating a new AI agent."""
    name: str = Field(..., min_length=1, max_length=255)
    nickname: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=100)
    skills: List[str] = Field(default_factory=list)
    memory_enabled: bool = Field(default=True)


class AgentUpdate(BaseModel):
    """Schema for updating an AI agent."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    nickname: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None
    skills: Optional[List[str]] = None
    memory_enabled: Optional[bool] = None
    deepagent_config: Optional[dict] = None


class AgentResponse(BaseModel):
    """Schema for AI agent response."""
    id: UUID
    project_id: UUID
    name: str
    nickname: str
    email: Optional[str]
    role: Optional[str]
    type: str
    avatar_url: Optional[str]
    status: str
    joined_at: datetime
    skills: List[str]
    memory_enabled: bool
    memory_document_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class ThreadCreate(BaseModel):
    """Schema for creating a new thread."""
    initial_state: Optional[dict] = None


class AgentExecutionRequest(BaseModel):
    """Schema for agent execution request."""
    input_data: dict
    lane: Optional[str] = None


class AgentMemoryUpdate(BaseModel):
    """Schema for updating agent memory."""
    content: dict
