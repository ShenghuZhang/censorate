from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID


class RemoteAgentCreate(BaseModel):
    """Schema for registering a new remote agent."""
    name: str = Field(..., min_length=1, max_length=255)
    agent_type: str = Field(..., min_length=1, max_length=50)
    endpoint_url: str = Field(..., min_length=1, max_length=500)
    health_check_path: str = Field(default="/health", max_length=255)
    api_key: Optional[str] = Field(None, max_length=255)
    health_check_interval: int = Field(default=30, ge=10, le=300)
    description: Optional[str] = Field(None, max_length=1000)
    capabilities: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)


class RemoteAgentUpdate(BaseModel):
    """Schema for updating a remote agent."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    agent_type: Optional[str] = Field(None, min_length=1, max_length=50)
    endpoint_url: Optional[str] = Field(None, min_length=1, max_length=500)
    health_check_path: Optional[str] = Field(None, max_length=255)
    api_key: Optional[str] = Field(None, max_length=255)
    health_check_interval: Optional[int] = Field(None, ge=10, le=300)
    description: Optional[str] = Field(None, max_length=1000)
    capabilities: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None


class RemoteAgentResponse(BaseModel):
    """Schema for remote agent response."""
    id: UUID
    name: str
    agent_type: str
    endpoint_url: str
    health_check_path: str
    status: str
    last_health_check: Optional[datetime]
    health_check_interval: int
    description: Optional[str]
    capabilities: List[str]
    config: Dict[str, Any]
    # Alert state
    consecutive_failures: int
    alert_acknowledged: bool
    # Alert thresholds
    alert_after_consecutive_failures: int
    alert_after_offline_minutes: int
    warning_latency_ms: int
    critical_latency_ms: int
    created_at: datetime
    updated_at: datetime
    # Note: api_key is NOT included in responses for security

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    status: str
    response_time_ms: Optional[int]
    last_health_check: datetime
    message: Optional[str]


class AgentChatRequest(BaseModel):
    """Schema for sending a chat message to an agent."""
    message: str = Field(..., min_length=1)
    thread_id: Optional[str] = None
    project_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class AgentChatResponse(BaseModel):
    """Schema for agent chat response."""
    response: str
    thread_id: str
    agent_id: UUID
    timestamp: datetime


class RemoteAgentHealthHistoryResponse(BaseModel):
    """Schema for remote agent health history response."""
    id: UUID
    agent_id: UUID
    status: str
    response_time_ms: Optional[int]
    error_message: Optional[str]
    checked_at: datetime
    created_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RemoteAgentWithHistoryResponse(RemoteAgentResponse):
    """Schema for remote agent with recent health history."""
    recent_health_history: Optional[List[RemoteAgentHealthHistoryResponse]] = None


class AgentAcknowledgement(BaseModel):
    """Schema for acknowledging an alert."""
    acknowledged_by: Optional[str] = Field(None, max_length=255)


class AgentThresholdUpdate(BaseModel):
    """Schema for updating agent alert thresholds."""
    alert_after_consecutive_failures: Optional[int] = Field(None, ge=1, le=20)
    alert_after_offline_minutes: Optional[int] = Field(None, ge=1, le=1440)
    warning_latency_ms: Optional[int] = Field(None, ge=100, le=30000)
    critical_latency_ms: Optional[int] = Field(None, ge=100, le=30000)
