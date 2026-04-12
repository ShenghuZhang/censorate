from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_type: str = Field(default="non_technical", pattern=r"^(non_technical|technical)$")


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    project_type: Optional[str] = Field(None, pattern=r"^(non_technical|technical)$")


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    project_type: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    settings: dict = Field(default_factory=dict)
    archived_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True
