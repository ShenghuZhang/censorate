from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, UUIDType, JsonType
from datetime import datetime


class Comment(BaseModel):
    """Comment on requirements."""
    __tablename__ = "comments"

    requirement_id = Column(UUIDType, ForeignKey("requirements.id"), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(String(255), nullable=True)
    author_name = Column(String(255), nullable=True)
    is_ai = Column(Boolean, default=False, nullable=False)
    attachments = Column(JsonType, default=list, nullable=True)

    requirement = relationship("Requirement", back_populates="comments")
