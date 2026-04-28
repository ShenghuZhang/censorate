"""Notification repository - data access layer for notifications."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import Notification
from .base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    """Repository for notification operations."""

    def get(self, db: Session, id: UUID) -> Optional[Notification]:
        """Get a single notification by ID."""
        return db.query(Notification).filter(Notification.id == id).first()

    def get_all(self, db: Session) -> List[Notification]:
        """Get all notifications."""
        return db.query(Notification).all()

    def create(self, db: Session, entity: Notification) -> Notification:
        """Create a new notification."""
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(self, db: Session, entity: Notification) -> Notification:
        """Update an existing notification."""
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a notification by ID."""
        entity = db.query(Notification).filter(Notification.id == id).first()
        if entity:
            db.delete(entity)
            db.commit()

    def get_by_user(
        self,
        db: Session,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.archived_at.is_(None)
        )

        if unread_only:
            query = query.filter(Notification.read == False)

        return query.order_by(desc(Notification.created_at)).limit(limit).offset(offset).all()

    def get_unread_count(self, db: Session, user_id: UUID) -> int:
        """Get count of unread notifications for a user."""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False,
            Notification.archived_at.is_(None)
        ).count()

    def mark_as_read(self, db: Session, id: UUID) -> Optional[Notification]:
        """Mark a notification as read."""
        notification = self.get(db, id)
        if notification:
            notification.read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)
        return notification

    def mark_all_as_read(self, db: Session, user_id: UUID) -> int:
        """Mark all user's notifications as read."""
        updated = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False,
            Notification.archived_at.is_(None)
        ).update({
            "read": True,
            "read_at": datetime.utcnow()
        }, synchronize_session=False)
        db.commit()
        return updated

    def archive(self, db: Session, id: UUID) -> bool:
        """Archive a notification."""
        notification = self.get(db, id)
        if notification:
            notification.archived_at = datetime.utcnow()
            db.commit()
            return True
        return False
