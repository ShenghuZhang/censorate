from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, UUIDType, JsonType


class GenerationProject(BaseModel):
    """A code generation project from user requirements."""
    __tablename__ = "generation_projects"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_story = Column(Text, nullable=False)
    status = Column(String(50), default="draft", nullable=False)
    template_id = Column(UUIDType, ForeignKey("templates.id"), nullable=False)
    prd_content = Column(JsonType, nullable=True)
    architecture_design = Column(JsonType, nullable=True)
    repo_url = Column(String(1024), nullable=True)
    created_by = Column(UUIDType, ForeignKey("users.id"), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    template = relationship("Template")
    files = relationship("GeneratedFile", back_populates="project", cascade="all, delete-orphan")
    steps = relationship("PipelineStep", back_populates="project", cascade="all, delete-orphan")
    github_repo = relationship("GitHubRepo", back_populates="project", uselist=False)

    def __repr__(self):
        return f"<GenerationProject {self.name} ({self.status})>"
