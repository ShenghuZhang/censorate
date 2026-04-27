from datetime import datetime, timezone
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer


class CommentCreate(BaseModel):
    """Schema for creating a comment."""
    content: str = Field(..., min_length=1)
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    is_ai: bool = False
    attachments: Optional[List[Any]] = None


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""
    content: Optional[str] = Field(None, min_length=1)


class CommentResponse(BaseModel):
    """Response schema for comment."""
    id: UUID
    requirement_id: UUID
    content: str
    author_id: Optional[str]
    author_name: Optional[str]
    is_ai: bool
    attachments: Optional[List[Any]]
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Ensure datetime has timezone info and serialize as ISO."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True
