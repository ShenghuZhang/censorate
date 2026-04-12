from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer, DateTime
from .base import UUIDType
from sqlalchemy.orm import relationship
from .base import BaseModel


class TestCase(BaseModel):
    """Test case model."""
    __tablename__ = "test_cases"

    requirement_id = Column(UUIDType, ForeignKey("requirements.id"), nullable=False)
    test_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), default="manual", nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    github_run_url = Column(String(500), nullable=True)

    created_by = Column(String, nullable=False)

    # Relationships
    requirement = relationship("Requirement", back_populates="test_cases")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<TestCase {self.test_number}: {self.title}>"
