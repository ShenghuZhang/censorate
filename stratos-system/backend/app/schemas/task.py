from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    estimate_hours: Optional[int] = None
    assigned_to: Optional[str] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = None
    estimate_hours: Optional[int] = None
    github_pr_url: Optional[str] = None
    assigned_to: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: UUID
    requirement_id: UUID
    task_number: int
    title: str
    description: Optional[str]
    status: str
    estimate_hours: Optional[int]
    github_pr_url: Optional[str]
    created_by: str
    assigned_to: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True
