"""Test case schemas for Censorate API."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class TestCaseCreate(BaseModel):
    """Schema for creating a new test case."""
    title: str = Field(..., min_length=1, max_length=500, description="Test case title")
    description: Optional[str] = Field(None, description="Test case description")
    type: str = Field(default="manual", description="Test case type (manual, automated)")
    status: str = Field(default="pending", description="Test case status")
    github_run_url: Optional[str] = Field(None, description="GitHub run URL for test case")


class TestCaseUpdate(BaseModel):
    """Schema for updating an existing test case."""
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Test case title")
    description: Optional[str] = Field(None, description="Test case description")
    type: Optional[str] = Field(None, description="Test case type (manual, automated)")
    status: Optional[str] = Field(None, description="Test case status")
    github_run_url: Optional[str] = Field(None, description="GitHub run URL for test case")


class TestCaseResponse(BaseModel):
    """Schema for test case response."""
    id: UUID
    requirement_id: UUID
    test_number: int
    title: str
    description: Optional[str]
    type: str
    status: str
    github_run_url: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]
    archived_at: Optional[datetime]

    class Config:
        from_attributes = True
