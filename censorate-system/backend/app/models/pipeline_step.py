from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, UUIDType, JsonType


class PipelineStep(BaseModel):
    """Track each step of the generation pipeline."""
    __tablename__ = "pipeline_steps"

    project_id = Column(UUIDType, ForeignKey("generation_projects.id"), nullable=False)
    step_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result = Column(JsonType, nullable=True)
    error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Relationships
    project = relationship("GenerationProject", back_populates="steps")

    def __repr__(self):
        return f"<PipelineStep {self.step_type} ({self.status})>"
