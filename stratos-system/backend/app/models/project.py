from sqlalchemy import Column, String, Text, Boolean, Enum
from .base import UUIDType
from sqlalchemy.orm import relationship
from .base import BaseModel, JsonType


class Project(BaseModel):
    """Project model."""
    __tablename__ = "projects"

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String(20), default="non_technical", nullable=False)
    created_by = Column(String, nullable=False)
    settings = Column(JsonType, default=dict)

    # Relationships
    requirements = relationship("Requirement", back_populates="project")
    github_repos = relationship("GitHubRepo", back_populates="project")
    team_members = relationship("TeamMember", back_populates="project")
    lane_roles = relationship("LaneRole", back_populates="project")
    automation_rules = relationship("AutomationRule", back_populates="project")

    def __repr__(self):
        return f"<Project {self.name} ({self.slug})>"
