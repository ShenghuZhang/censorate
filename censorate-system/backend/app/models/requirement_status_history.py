from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, UUIDType
from datetime import datetime


class RequirementStatusHistory(BaseModel):
    """Requirement status change history."""
    __tablename__ = "requirement_status_history"

    requirement_id = Column(UUIDType, ForeignKey("requirements.id"), nullable=False)
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    assigned_to = Column(String(255), nullable=True)
    assigned_to_name = Column(String(255), nullable=True)
    expected_completion_at = Column(DateTime, nullable=True)
    changed_by = Column(String(255), nullable=True)
    changed_by_name = Column(String(255), nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    note = Column(Text, nullable=True)
    is_backward = Column(Boolean, default=False, nullable=False)

    requirement = relationship("Requirement", back_populates="status_history")
