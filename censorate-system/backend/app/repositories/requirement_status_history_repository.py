"""Requirement status history repository - provides data access layer for status history."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import RequirementStatusHistory
from .base_repository import BaseRepository


class RequirementStatusHistoryRepository(BaseRepository):
    """Repository for requirement status history operations."""

    def get(self, db: Session, id: UUID) -> Optional[RequirementStatusHistory]:
        """Get a single status history record by ID."""
        return db.query(RequirementStatusHistory).filter(RequirementStatusHistory.id == id).first()

    def get_all(self, db: Session) -> List[RequirementStatusHistory]:
        """Get all status history records."""
        return db.query(RequirementStatusHistory).all()

    def create(self, db: Session, entity: RequirementStatusHistory) -> RequirementStatusHistory:
        """Create a new status history record."""
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(self, db: Session, entity: RequirementStatusHistory) -> RequirementStatusHistory:
        """Update an existing status history record."""
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a status history record by ID."""
        entity = db.query(RequirementStatusHistory).filter(RequirementStatusHistory.id == id).first()
        if entity:
            db.delete(entity)
            db.commit()

    def get_by_requirement(self, db: Session, requirement_id: UUID) -> List[RequirementStatusHistory]:
        """Get all history records for a requirement."""
        return db.query(RequirementStatusHistory).filter(
            RequirementStatusHistory.requirement_id == requirement_id,
            RequirementStatusHistory.archived_at.is_(None)
        ).order_by(RequirementStatusHistory.changed_at.desc()).all()

    def get_last_forward(self, db: Session, requirement_id: UUID, to_status: str) -> Optional[RequirementStatusHistory]:
        """Get last forward transition to a specific status."""
        return db.query(RequirementStatusHistory).filter(
            RequirementStatusHistory.requirement_id == requirement_id,
            RequirementStatusHistory.to_status == to_status,
            RequirementStatusHistory.is_backward == False,
            RequirementStatusHistory.archived_at.is_(None)
        ).order_by(RequirementStatusHistory.changed_at.desc()).first()

    def archive(self, db: Session, id: UUID) -> bool:
        """Archive a status history record."""
        from datetime import datetime
        entity = self.get(db, id)
        if entity:
            entity.archived_at = datetime.utcnow()
            db.commit()
            return True
        return False
