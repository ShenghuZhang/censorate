"""Attachment model for file uploads."""
from sqlalchemy import Column, String, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from .base import BaseModel, UUIDType


class Attachment(BaseModel):
    """Attachment model for storing uploaded files."""
    __tablename__ = "attachments"

    requirement_id = Column(UUIDType, ForeignKey("requirements.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100))
    file_size = Column(Integer)
    minio_object_name = Column(String(500), nullable=False)  # MinIO object path
    minio_url = Column(String(500), nullable=False)  # Public URL
    uploaded_by = Column(String(255))
    uploaded_by_name = Column(String(255))
    description = Column(Text)

    # Relationship
    requirement = relationship("Requirement", back_populates="attachments")
