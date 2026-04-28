"""Attachment repository - provides data access layer for attachments."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import Attachment
from .base_repository import BaseRepository


class AttachmentRepository(BaseRepository):
    """Repository for attachment operations."""

    def get(self, db: Session, id: UUID) -> Optional[Attachment]:
        """Get a single attachment by ID."""
        return db.query(Attachment).filter(Attachment.id == id).first()

    def get_all(self, db: Session) -> List[Attachment]:
        """Get all attachments."""
        return db.query(Attachment).all()

    def create(self, db: Session, entity: dict) -> Attachment:
        """Create a new attachment."""
        attachment = Attachment(**entity)
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        return attachment

    def update(self, db: Session, entity: Attachment) -> Attachment:
        """Update an existing attachment."""
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, id: UUID) -> None:
        """Delete an attachment by ID."""
        entity = db.query(Attachment).filter(Attachment.id == id).first()
        if entity:
            db.delete(entity)
            db.commit()

    def get_by_requirement(self, db: Session, requirement_id: UUID) -> List[Attachment]:
        """Get all attachments for a requirement."""
        return db.query(Attachment).filter(
            Attachment.requirement_id == requirement_id,
            Attachment.archived_at.is_(None)
        ).order_by(Attachment.created_at.desc()).all()

    def get_by_filename(self, db: Session, requirement_id: UUID, filename: str) -> Optional[Attachment]:
        """Get attachment by filename for a requirement."""
        return db.query(Attachment).filter(
            Attachment.requirement_id == requirement_id,
            Attachment.filename == filename,
            Attachment.archived_at.is_(None)
        ).first()
