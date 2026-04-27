"""Profile schemas for Censorate API."""

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer


class UserProjectResponse(BaseModel):
    """Schema for user's project information."""
    id: UUID
    name: str
    description: Optional[str] = None
    role: Optional[str] = None
    joined_at: datetime

    @field_serializer('joined_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Ensure datetime has timezone info and serialize as ISO."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True


class UserActivityResponse(BaseModel):
    """Schema for user activity."""
    id: str
    type: str  # 'status_change' or 'comment'
    action: str
    target: str
    target_id: UUID
    timestamp: datetime
    note: Optional[str] = None

    @field_serializer('timestamp')
    def serialize_datetime(self, dt: datetime) -> str:
        """Ensure datetime has timezone info and serialize as ISO."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt.isoformat()


class UserContributionDay(BaseModel):
    """Schema for single day's contribution."""
    date: str
    count: int


class UserContributionHeatmapResponse(BaseModel):
    """Schema for user contribution heatmap."""
    contributions: List[UserContributionDay]
    total: int


class UserProfileResponse(BaseModel):
    """Schema for full user profile."""
    id: UUID
    name: str
    email: str
    projects: List[UserProjectResponse]
    recent_activity: List[UserActivityResponse]
    created_at: datetime
    updated_at: Optional[datetime]

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Ensure datetime has timezone info and serialize as ISO."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True
