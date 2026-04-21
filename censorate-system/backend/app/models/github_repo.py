from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer, DateTime
from .base import UUIDType
from sqlalchemy.orm import relationship
from .base import BaseModel


class GitHubRepo(BaseModel):
    """GitHub repository model."""
    __tablename__ = "github_repos"

    project_id = Column(UUIDType, ForeignKey("projects.id"), nullable=False)
    url = Column(String(1024), nullable=False)
    description = Column(Text, nullable=True)
    owner = Column(String(255), nullable=True)
    repo = Column(String(255), nullable=True)
    installation_id = Column(Integer, nullable=True)
    webhook_id = Column(Integer, nullable=True)
    last_synced_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="github_repos")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<GitHubRepo {self.owner}/{self.repo}>"
