from sqlalchemy import Column, String, Boolean, ForeignKey
from .base import UUIDType
from sqlalchemy.orm import relationship
from .base import BaseModel, JsonType


class LaneRole(BaseModel):
    """Lane role configuration model."""
    __tablename__ = "lane_roles"

    project_id = Column(UUIDType, ForeignKey("projects.id"), nullable=False)
    lane = Column(String(50), nullable=False)  # 'analysis', 'design', etc.
    role_name = Column(String(255), nullable=False)
    agent_type = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    config = Column(JsonType, default=dict)

    # Relationships
    project = relationship("Project", back_populates="lane_roles")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<LaneRole {self.lane}: {self.role_name}>"
