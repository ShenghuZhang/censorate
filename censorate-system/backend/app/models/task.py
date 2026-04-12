from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer, DateTime
from .base import UUIDType
from sqlalchemy.orm import relationship
from .base import BaseModel


class Task(BaseModel):
    """Task model."""
    __tablename__ = "tasks"

    requirement_id = Column(UUIDType, ForeignKey("requirements.id"), nullable=False)
    task_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False)
    estimate_hours = Column(Integer, nullable=True)
    github_pr_url = Column(String(500), nullable=True)

    created_by = Column(String, nullable=False)
    assigned_to = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    requirement = relationship("Requirement", back_populates="tasks")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<Task {self.task_number}: {self.title}>"
