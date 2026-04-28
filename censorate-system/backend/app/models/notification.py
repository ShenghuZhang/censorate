"""Notification models - database schema for notifications."""

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel, UUIDType, JsonType
from datetime import datetime
import enum


class NotificationType(str, enum.Enum):
    """Types of notifications."""
    MENTION = "mention"
    ASSIGNMENT = "assignment"
    DUE_DATE_REMINDER = "due_date_reminder"


class Notification(BaseModel):
    """Notification model - stores user notifications."""
    __tablename__ = "notifications"

    user_id = Column(UUIDType, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    requirement_id = Column(UUIDType, ForeignKey("requirements.id"), nullable=True)
    related_id = Column(UUIDType, nullable=True)  # For comment/assignment tracking
    notification_metadata = Column(JsonType, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    requirement = relationship("Requirement", foreign_keys=[requirement_id])

    def __repr__(self):
        return f"<Notification {self.id} {self.type} {self.read}>"


class UserNotificationPreference(BaseModel):
    """User notification preferences."""
    __tablename__ = "user_notification_preferences"

    user_id = Column(UUIDType, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Enable/disable notification types
    enable_mention_notifications = Column(Boolean, default=True, nullable=False)
    enable_assignment_notifications = Column(Boolean, default=True, nullable=False)
    enable_due_date_reminders = Column(Boolean, default=True, nullable=False)

    # Delivery channel preferences
    mention_email = Column(Boolean, default=False, nullable=False)
    assignment_email = Column(Boolean, default=False, nullable=False)
    due_date_email = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<UserNotificationPreference {self.id} user={self.user_id}>"
