"""Comment repository - provides data access layer for comments."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import Comment
from .base_repository import BaseRepository


class CommentRepository(BaseRepository):
    """Repository for comment operations."""

    def get(self, db: Session, id: UUID) -> Optional[Comment]:
        """Get a single comment by ID."""
        return db.query(Comment).filter(Comment.id == id).first()

    def get_all(self, db: Session) -> List[Comment]:
        """Get all comments."""
        return db.query(Comment).all()

    def create(self, db: Session, entity: Comment) -> Comment:
        """Create a new comment."""
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(self, db: Session, entity: Comment) -> Comment:
        """Update an existing comment."""
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a comment by ID."""
        entity = db.query(Comment).filter(Comment.id == id).first()
        if entity:
            db.delete(entity)
            db.commit()

    def get_by_requirement(self, db: Session, requirement_id: UUID) -> List[Comment]:
        """Get all comments for a requirement."""
        return db.query(Comment).filter(
            Comment.requirement_id == requirement_id,
            Comment.archived_at.is_(None)
        ).order_by(Comment.created_at.asc()).all()

    def archive(self, db: Session, id: UUID) -> bool:
        """Archive a comment."""
        from datetime import datetime
        entity = self.get(db, id)
        if entity:
            entity.archived_at = datetime.utcnow()
            db.commit()
            return True
        return False
