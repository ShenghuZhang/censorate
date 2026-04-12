from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer, Numeric, DateTime
from .base import UUIDType
from sqlalchemy.orm import relationship
from .base import BaseModel, JsonType


class Requirement(BaseModel):
    """Requirement model."""
    __tablename__ = "requirements"

    project_id = Column(UUIDType, ForeignKey("projects.id"), nullable=False)
    req_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="backlog", nullable=False)
    priority = Column(String(20), default="medium", nullable=False)

    # Lark (Feishu) integration
    source = Column(String(50), nullable=True)
    source_metadata = Column(JsonType, nullable=True)
    lark_doc_token = Column(String(255), nullable=True)
    lark_doc_url = Column(String(500), nullable=True)
    lark_editable = Column(Boolean, default=False)

    # AI analysis fields
    ai_confidence = Column(Numeric(5, 2), nullable=True)
    ai_suggestions = Column(JsonType, nullable=True)
    current_agent = Column(String(100), nullable=True)
    current_thread_id = Column(String(255), nullable=True)

    created_by = Column(String, nullable=False)
    assigned_to = Column(String, nullable=True)

    return_count = Column(Integer, default=0)
    last_returned_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="requirements")
    tasks = relationship("Task", back_populates="requirement")
    test_cases = relationship("TestCase", back_populates="requirement")
    agent_executions = relationship("AgentExecution", back_populates="requirement")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<Requirement REQ-{self.req_number}: {self.title}>"
