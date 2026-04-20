from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Integer
from .base import UUIDType, BaseModel, JsonType


class RemoteAgent(BaseModel):
    """Remote deployed AI agent (Hermes, OpenClaw, etc.)."""
    __tablename__ = "remote_agents"

    name = Column(String(255), nullable=False)
    agent_type = Column(String(50), nullable=False)  # 'hermes', 'openclaw', 'custom'
    endpoint_url = Column(String(500), nullable=False)
    health_check_path = Column(String(255), default="/health")
    api_key = Column(String(255), nullable=True)  # Store encrypted?
    status = Column(String(20), default="offline")  # 'online', 'offline', 'error'
    last_health_check = Column(DateTime, nullable=True)
    health_check_interval = Column(Integer, default=30)  # seconds
    description = Column(String(1000), nullable=True)
    capabilities = Column(JsonType, default=list)
    config = Column(JsonType, default=dict)

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<RemoteAgent {self.name} ({self.agent_type})>"
