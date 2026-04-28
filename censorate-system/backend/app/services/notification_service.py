"""Notification service - core notification logic."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import (
    Notification,
    UserNotificationPreference,
    NotificationType,
    Requirement,
    User
)
from ..repositories import (
    NotificationRepository,
    UserNotificationPreferenceRepository
)
from ..core.notification_redis import notification_redis


class NotificationService:
    """Service for managing notifications."""

    def __init__(
        self,
        notification_repo: Optional[NotificationRepository] = None,
        preference_repo: Optional[UserNotificationPreferenceRepository] = None
    ):
        self.notification_repo = notification_repo or NotificationRepository()
        self.preference_repo = preference_repo or UserNotificationPreferenceRepository()

    def get_user_notifications(
        self,
        db: Session,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user."""
        return self.notification_repo.get_by_user(
            db, user_id, limit, offset, unread_only
        )

    def get_unread_count(self, db: Session, user_id: UUID) -> int:
        """Get unread notification count for a user."""
        # Check cache first
        cached = notification_redis.get_unread_count(user_id)
        if cached is not None:
            return cached

        # Fallback to database
        count = self.notification_repo.get_unread_count(db, user_id)
        notification_redis.set_unread_count(user_id, count)
        return count

    def mark_as_read(self, db: Session, notification_id: UUID) -> Optional[Notification]:
        """Mark a notification as read."""
        notification = self.notification_repo.mark_as_read(db, notification_id)
        if notification:
            notification_redis.clear_unread_cache(notification.user_id)
        return notification

    def mark_all_as_read(self, db: Session, user_id: UUID) -> int:
        """Mark all user's notifications as read."""
        count = self.notification_repo.mark_all_as_read(db, user_id)
        notification_redis.clear_unread_cache(user_id)
        return count

    def delete_notification(self, db: Session, notification_id: UUID) -> bool:
        """Delete (archive) a notification."""
        notification = self.notification_repo.get(db, notification_id)
        if notification:
            result = self.notification_repo.archive(db, notification_id)
            if result:
                notification_redis.clear_unread_cache(notification.user_id)
            return result
        return False

    def get_user_preferences(self, db: Session, user_id: UUID) -> UserNotificationPreference:
        """Get or create user preferences."""
        return self.preference_repo.get_or_create(db, user_id)

    def update_user_preferences(
        self,
        db: Session,
        user_id: UUID,
        preferences: Dict[str, Any]
    ) -> UserNotificationPreference:
        """Update user preferences."""
        pref = self.preference_repo.get_or_create(db, user_id)
        for key, value in preferences.items():
            if hasattr(pref, key):
                setattr(pref, key, value)
        return self.preference_repo.update(db, pref)

    def create_mention_notification(
        self,
        db: Session,
        user_id: UUID,
        requirement: Requirement,
        comment_id: UUID,
        mentioned_by: UUID,
        mentioned_by_name: str,
        comment_snippet: str
    ) -> Optional[Notification]:
        """Create a mention notification if not duplicate and enabled."""
        # Check user preferences
        preferences = self.get_user_preferences(db, user_id)
        if not preferences.enable_mention_notifications:
            return None

        # Check deduplication
        dedup_key = f"notifications:sent:mention:{comment_id}:{user_id}"
        if not notification_redis.should_send_notification(dedup_key, ttl=604800):  # 7 days
            return None

        # Create notification
        notification = Notification(
            user_id=user_id,
            type=NotificationType.MENTION.value,
            title="You were mentioned",
            message=f"@{mentioned_by_name} mentioned you in a comment on REQ-{requirement.req_number}: {requirement.title}",
            requirement_id=requirement.id,
            related_id=comment_id,
            notification_metadata={
                "comment_id": str(comment_id),
                "mentioned_by": str(mentioned_by),
                "mentioned_by_name": mentioned_by_name,
                "comment_snippet": comment_snippet[:200]
            }
        )

        result = self.notification_repo.create(db, notification)
        self._publish_notification(result)
        return result

    def create_assignment_notification(
        self,
        db: Session,
        user_id: UUID,
        requirement: Requirement,
        assigned_by: Optional[UUID],
        assigned_by_name: Optional[str],
        previous_assignee: Optional[UUID] = None
    ) -> Optional[Notification]:
        """Create an assignment notification if not duplicate and enabled."""
        # Check user preferences
        preferences = self.get_user_preferences(db, user_id)
        if not preferences.enable_assignment_notifications:
            return None

        # Check deduplication - use timestamp to allow reassignments
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        dedup_key = f"notifications:sent:assignment:{requirement.id}:{user_id}:{timestamp}"
        if not notification_redis.should_send_notification(dedup_key, ttl=86400):  # 1 day
            return None

        # Create notification message
        if previous_assignee:
            message = f"REQ-{requirement.req_number}: {requirement.title} has been reassigned to you"
        else:
            message = f"REQ-{requirement.req_number}: {requirement.title} has been assigned to you"

        notification = Notification(
            user_id=user_id,
            type=NotificationType.ASSIGNMENT.value,
            title="Requirement Assigned",
            message=message,
            requirement_id=requirement.id,
            related_id=requirement.id,
            notification_metadata={
                "assigned_by": str(assigned_by) if assigned_by else None,
                "assigned_by_name": assigned_by_name,
                "previous_assignee": str(previous_assignee) if previous_assignee else None
            }
        )

        result = self.notification_repo.create(db, notification)
        self._publish_notification(result)
        return result

    def create_due_date_notification(
        self,
        db: Session,
        user_id: UUID,
        requirement: Requirement,
        days_remaining: int
    ) -> Optional[Notification]:
        """Create a due date reminder notification if not duplicate and enabled."""
        # Check user preferences
        preferences = self.get_user_preferences(db, user_id)
        if not preferences.enable_due_date_reminders:
            return None

        # Check deduplication - one per day
        date_str = datetime.utcnow().strftime("%Y%m%d")
        dedup_key = f"notifications:sent:due_date:{requirement.id}:{user_id}:{date_str}"
        if not notification_redis.should_send_notification(dedup_key, ttl=172800):  # 48 hours
            return None

        # Create appropriate message based on days remaining
        if days_remaining < 0:
            title = "Overdue!"
            message = f"REQ-{requirement.req_number}: {requirement.title} is {abs(days_remaining)} day(s) overdue"
        elif days_remaining == 0:
            title = "Due Today!"
            message = f"REQ-{requirement.req_number}: {requirement.title} is due today"
        elif days_remaining == 1:
            title = "Due Tomorrow"
            message = f"REQ-{requirement.req_number}: {requirement.title} is due tomorrow"
        else:
            title = "Due Soon"
            message = f"REQ-{requirement.req_number}: {requirement.title} is due in {days_remaining} days"

        notification = Notification(
            user_id=user_id,
            type=NotificationType.DUE_DATE_REMINDER.value,
            title=title,
            message=message,
            requirement_id=requirement.id,
            related_id=requirement.id,
            notification_metadata={
                "due_date": requirement.expected_completion_at.isoformat() if requirement.expected_completion_at else None,
                "days_remaining": days_remaining
            }
        )

        result = self.notification_repo.create(db, notification)
        self._publish_notification(result)
        return result

    def _publish_notification(self, notification: Notification) -> None:
        """Publish notification to Redis pub/sub for real-time delivery."""
        try:
            notification_data = {
                "id": str(notification.id),
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "read": notification.read,
                "created_at": notification.created_at.isoformat(),
                "requirement_id": str(notification.requirement_id) if notification.requirement_id else None
            }
            notification_redis.publish_notification(str(notification.user_id), notification_data)
            notification_redis.increment_unread_count(str(notification.user_id))
        except Exception as e:
            print(f"Failed to publish notification: {e}")


# Singleton instance
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Get singleton notification service instance."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
