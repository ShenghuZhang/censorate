"""Notification scheduler service - due date reminder scheduling."""

import logging
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from ..models import Requirement
from ..repositories import RequirementRepository
from .notification_service import get_notification_service

logger = logging.getLogger(__name__)


class NotificationSchedulerService:
    """Service for scheduling and processing due date reminders."""

    def __init__(
        self,
        requirement_repo: Optional[RequirementRepository] = None
    ):
        self.requirement_repo = requirement_repo or RequirementRepository()
        self.notification_service = get_notification_service()

    def check_due_dates(self, db: Session) -> None:
        """
        Check for upcoming due dates and send notifications.

        Checks for requirements due in the next 2 days, and overdue requirements.
        Sends one notification per user per requirement per day.
        """
        logger.info("Checking for due date reminders...")

        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        requirements = self._get_requirements_with_due_dates(db)

        reminder_count = 0
        for requirement in requirements:
            if not requirement.assigned_to or not requirement.expected_completion_at:
                continue

            try:
                due_date = requirement.expected_completion_at
                if due_date.tzinfo is None:
                    due_date = due_date.replace(tzinfo=timezone.utc)

                days_remaining = (due_date.date() - now.date()).days

                # Only send reminders for:
                # - Due in 0, 1, or 2 days
                # - Overdue (negative days)
                if -30 <= days_remaining <= 2:
                    # Skip if already completed
                    if requirement.completed_at:
                        continue

                    # Create notification
                    self.notification_service.create_due_date_notification(
                        db=db,
                        user_id=UUID(requirement.assigned_to) if isinstance(requirement.assigned_to, str) else requirement.assigned_to,
                        requirement=requirement,
                        days_remaining=days_remaining
                    )
                    reminder_count += 1

            except Exception as e:
                logger.error(f"Error processing due date for requirement {requirement.id}: {e}")

        logger.info(f"Sent {reminder_count} due date reminders")

    def _get_requirements_with_due_dates(self, db: Session) -> list:
        """Get all requirements with due dates."""
        from sqlalchemy import and_, or_

        now = datetime.utcnow()

        # Get requirements due in next 2 days or overdue in last 30 days
        return db.query(Requirement).filter(
            Requirement.expected_completion_at.isnot(None),
            Requirement.assigned_to.isnot(None),
            Requirement.archived_at.is_(None),
            Requirement.completed_at.is_(None)
        ).all()


# Singleton instance
_scheduler_service: Optional[NotificationSchedulerService] = None


def get_notification_scheduler_service() -> NotificationSchedulerService:
    """Get singleton notification scheduler service instance."""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = NotificationSchedulerService()
    return _scheduler_service
