"""Notification schemas - Pydantic models for notification API."""

from datetime import datetime, timezone
from typing import Optional, Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer
from enum import Enum


class NotificationType(str, Enum):
    """Types of notifications."""
    MENTION = "mention"
    ASSIGNMENT = "assignment"
    DUE_DATE_REMINDER = "due_date_reminder"


class NotificationResponse(BaseModel):
    """Response schema for notification."""
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    read: bool
    read_at: Optional[datetime] = None
    requirement_id: Optional[UUID] = None
    related_id: Optional[UUID] = None
    notification_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at', 'read_at')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Ensure datetime has timezone info and serialize as ISO."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    """Schema for marking a notification as read."""
    notification_id: UUID


class UserNotificationPreferenceResponse(BaseModel):
    """Response schema for user notification preferences."""
    id: UUID
    user_id: UUID
    enable_mention_notifications: bool
    enable_assignment_notifications: bool
    enable_due_date_reminders: bool
    mention_email: bool
    assignment_email: bool
    due_date_email: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Ensure datetime has timezone info and serialize as ISO."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True


class UserNotificationPreferenceUpdate(BaseModel):
    """Schema for updating user notification preferences."""
    enable_mention_notifications: Optional[bool] = None
    enable_assignment_notifications: Optional[bool] = None
    enable_due_date_reminders: Optional[bool] = None
    mention_email: Optional[bool] = None
    assignment_email: Optional[bool] = None
    due_date_email: Optional[bool] = None


class UnreadCountResponse(BaseModel):
    """Response schema for unread count."""
    count: int
