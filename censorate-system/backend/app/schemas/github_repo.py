from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class GitHubRepoCreate(BaseModel):
    """Schema for creating a GitHub repository."""
    url: str = Field(..., min_length=1, max_length=1024)
    description: Optional[str] = None


class GitHubRepoUpdate(BaseModel):
    """Schema for updating a GitHub repository."""
    url: Optional[str] = Field(None, min_length=1, max_length=1024)
    description: Optional[str] = None


class GitHubRepoResponse(BaseModel):
    """Schema for GitHub repository response."""
    id: UUID
    project_id: UUID
    url: str
    description: Optional[str]
    owner: Optional[str]
    repo: Optional[str]
    installation_id: Optional[int]
    webhook_id: Optional[int]
    last_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True
