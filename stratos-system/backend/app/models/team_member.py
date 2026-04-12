from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from .base import UUIDType
from sqlalchemy.orm import relationship
from .base import BaseModel, JsonType


class TeamMember(BaseModel):
    """Team member model for both humans and AI agents."""
    __tablename__ = "team_members"

    project_id = Column(UUIDType, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    role = Column(String(100), nullable=True)
    type = Column(String(20), default="human", nullable=False)  # 'human' or 'ai'
    avatar_url = Column(String(500), nullable=True)
    status = Column(String(20), default="active", nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # AI agent specific fields
    skills = Column(JsonType, default=list)
    memory_enabled = Column(Boolean, default=True)
    memory_document_id = Column(String(255), nullable=True)

    # DeepAgent configuration
    deepagent_config = Column(JsonType, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="team_members")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<TeamMember {self.nickname} ({self.role})>"
