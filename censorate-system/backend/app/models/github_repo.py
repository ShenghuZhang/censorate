from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from .base import UUIDType
from .base import BaseModel


class GitHubRepo(BaseModel):
    """GitHub repository for generated code projects."""
    __tablename__ = "github_repos"

    project_id = Column(UUIDType, ForeignKey("generation_projects.id"), nullable=False)
    repo_name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False)
    url = Column(String(1024), nullable=False)
    default_branch = Column(String(100), default="main")
    is_private = Column(Boolean, default=False)
    push_status = Column(String(20), default="pending")
    commit_sha = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    installation_id = Column(Integer, nullable=True)
    webhook_id = Column(Integer, nullable=True)
    last_synced_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("GenerationProject", back_populates="github_repo")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<GitHubRepo {self.owner}/{self.repo_name}>"
