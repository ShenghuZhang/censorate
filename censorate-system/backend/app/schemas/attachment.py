"""Attachment schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class AttachmentBase(BaseModel):
    """Base attachment schema."""
    filename: str = Field(..., description="Stored filename")
    original_filename: str = Field(..., description="Original filename")
    content_type: Optional[str] = Field(None, description="MIME content type")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    description: Optional[str] = Field(None, description="Optional description")


class AttachmentCreate(AttachmentBase):
    """Schema for creating an attachment."""
    requirement_id: UUID = Field(..., description="Requirement ID")
    minio_object_name: str = Field(..., description="MinIO object path")
    minio_url: str = Field(..., description="MinIO public URL")
    uploaded_by: Optional[str] = Field(None, description="User ID who uploaded")
    uploaded_by_name: Optional[str] = Field(None, description="Name of user who uploaded")


class AttachmentUpdate(BaseModel):
    """Schema for updating an attachment."""
    description: Optional[str] = Field(None, description="Optional description")


class AttachmentResponse(AttachmentBase):
    """Schema for attachment responses."""
    id: UUID
    requirement_id: UUID
    minio_object_name: str
    minio_url: str
    uploaded_by: Optional[str] = None
    uploaded_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    url: Optional[str] = Field(None, description="Public URL to access the file")

    model_config = {
        "from_attributes": True
    }
