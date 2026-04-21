from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Integer, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from .base import UUIDType, BaseModel, JsonType
from app.core.security import encrypt_api_key, decrypt_api_key


class RemoteAgent(BaseModel):
    """Remote deployed AI agent (Hermes, OpenClaw, etc.)."""
    __tablename__ = "remote_agents"

    name = Column(String(255), nullable=False)
    agent_type = Column(String(50), nullable=False)  # 'hermes', 'openclaw', 'custom'
    endpoint_url = Column(String(500), nullable=False)
    health_check_path = Column(String(255), default="/health")
    _api_key = Column("api_key", String(500), nullable=True)  # Encrypted storage
    status = Column(String(20), default="offline")  # 'online', 'offline', 'error'
    last_health_check = Column(DateTime, nullable=True)
    health_check_interval = Column(Integer, default=30)  # seconds
    description = Column(String(1000), nullable=True)
    capabilities = Column(JsonType, default=list)
    config = Column(JsonType, default=dict)

    # Alert state fields
    consecutive_failures = Column(Integer, default=0)
    last_alert_sent_at = Column(DateTime, nullable=True)
    alert_acknowledged = Column(Boolean, default=False)
    alert_acknowledged_at = Column(DateTime, nullable=True)
    alert_acknowledged_by = Column(String(255), nullable=True)

    # Configurable alert thresholds
    alert_after_consecutive_failures = Column(Integer, default=3)
    alert_after_offline_minutes = Column(Integer, default=5)
    warning_latency_ms = Column(Integer, default=1000)
    critical_latency_ms = Column(Integer, default=2000)

    # Relationships
    health_history = relationship(
        "RemoteAgentHealthHistory",
        back_populates="agent",
        cascade="all, delete-orphan",
        order_by="RemoteAgentHealthHistory.checked_at.desc()"
    )

    __table_args__ = (
        {"extend_existing": True},
    )

    @hybrid_property
    def api_key(self) -> str | None:
        """Get decrypted API key."""
        return decrypt_api_key(self._api_key)

    @api_key.setter
    def api_key(self, value: str | None) -> None:
        """Set and encrypt API key."""
        self._api_key = encrypt_api_key(value)

    def __repr__(self):
        return f"<RemoteAgent {self.name} ({self.agent_type})>"


class RemoteAgentHealthHistory(BaseModel):
    """Health check history for remote agents."""
    __tablename__ = "remote_agent_health_history"

    agent_id = Column(UUIDType, ForeignKey("remote_agents.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # 'online', 'offline', 'error'
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    checked_at = Column(DateTime, nullable=False, index=True)

    # Relationships
    agent = relationship("RemoteAgent", back_populates="health_history")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<RemoteAgentHealthHistory {self.agent_id} {self.status} {self.checked_at}>"
