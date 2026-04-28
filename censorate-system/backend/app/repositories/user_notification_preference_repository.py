"""User notification preference repository - data access layer."""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import UserNotificationPreference
from .base_repository import BaseRepository


class UserNotificationPreferenceRepository(BaseRepository):
    """Repository for user notification preference operations."""

    def get(self, db: Session, id: UUID) -> Optional[UserNotificationPreference]:
        """Get a single preference by ID."""
        return db.query(UserNotificationPreference).filter(UserNotificationPreference.id == id).first()

    def get_all(self, db: Session) -> list:
        """Get all preferences."""
        return db.query(UserNotificationPreference).all()

    def create(self, db: Session, entity: UserNotificationPreference) -> UserNotificationPreference:
        """Create a new preference."""
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(self, db: Session, entity: UserNotificationPreference) -> UserNotificationPreference:
        """Update an existing preference."""
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a preference by ID."""
        entity = db.query(UserNotificationPreference).filter(UserNotificationPreference.id == id).first()
        if entity:
            db.delete(entity)
            db.commit()

    def get_by_user(self, db: Session, user_id: UUID) -> Optional[UserNotificationPreference]:
        """Get preferences for a user."""
        return db.query(UserNotificationPreference).filter(
            UserNotificationPreference.user_id == user_id
        ).first()

    def get_or_create(self, db: Session, user_id: UUID) -> UserNotificationPreference:
        """Get existing preferences or create defaults."""
        preference = self.get_by_user(db, user_id)
        if not preference:
            preference = UserNotificationPreference(user_id=user_id)
            db.add(preference)
            db.commit()
            db.refresh(preference)
        return preference
