from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, DateTime
from .base import UUIDType
from sqlalchemy.orm import relationship
from .base import BaseModel, JsonType


class AgentExecution(BaseModel):
    """Agent execution history model."""
    __tablename__ = "agent_executions"

    requirement_id = Column(UUIDType, ForeignKey("requirements.id"), nullable=False)
    agent_type = Column(String(100), nullable=False)
    lane = Column(String(50), nullable=False)
    status = Column(String(50), default="running", nullable=False)
    input_data = Column(JsonType, nullable=True)
    output_data = Column(JsonType, nullable=True)
    error_message = Column(String, nullable=True)
    thread_id = Column(String(255), nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    requirement = relationship("Requirement", back_populates="agent_executions")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<AgentExecution {self.agent_type} - {self.status}>"
