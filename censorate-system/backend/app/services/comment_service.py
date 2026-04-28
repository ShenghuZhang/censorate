"""Comment service - manages comment operations."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import Comment, Requirement
from ..repositories import CommentRepository
from .mention_service import get_mention_service


class CommentService:
    """Service for managing comments."""

    def __init__(self, comment_repo: CommentRepository = None):
        self.comment_repo = comment_repo or CommentRepository()
        self.mention_service = get_mention_service()

    def get_comments(self, db: Session, requirement_id: UUID) -> List[Comment]:
        """Get all comments for a requirement."""
        return self.comment_repo.get_by_requirement(db, requirement_id)

    def create_comment(self, db: Session, requirement_id: UUID, data: Dict) -> Comment:
        """Create a new comment."""
        comment = Comment(
            requirement_id=requirement_id,
            content=data.get("content"),
            author_id=data.get("author_id"),
            author_name=data.get("author_name"),
            is_ai=data.get("is_ai", False),
            attachments=data.get("attachments", [])
        )
        result = self.comment_repo.create(db, comment)

        # Process mentions and send notifications
        try:
            requirement = db.query(Requirement).filter(
                Requirement.id == requirement_id
            ).first()
            if requirement and result.author_id:
                self.mention_service.process_comment_mentions(
                    db=db,
                    comment=result,
                    requirement=requirement,
                    author_id=UUID(result.author_id) if isinstance(result.author_id, str) else result.author_id,
                    author_name=result.author_name or "Anonymous"
                )
        except Exception as e:
            # Don't fail the comment creation if mention processing fails
            print(f"Error processing mentions: {e}")

        return result

    def update_comment(self, db: Session, comment_id: UUID, data: Dict) -> Optional[Comment]:
        """Update a comment."""
        comment = self.comment_repo.get(db, comment_id)
        if not comment:
            return None

        if "content" in data:
            comment.content = data["content"]

        result = self.comment_repo.update(db, comment)

        # Process mentions again on update
        # Note: This might send duplicate notifications, but Redis dedup should handle it
        try:
            requirement = db.query(Requirement).filter(
                Requirement.id == comment.requirement_id
            ).first()
            if requirement and result.author_id:
                self.mention_service.process_comment_mentions(
                    db=db,
                    comment=result,
                    requirement=requirement,
                    author_id=UUID(result.author_id) if isinstance(result.author_id, str) else result.author_id,
                    author_name=result.author_name or "Anonymous"
                )
        except Exception as e:
            print(f"Error processing mentions on update: {e}")

        return result

    def delete_comment(self, db: Session, comment_id: UUID) -> bool:
        """Delete (archive) a comment."""
        return self.comment_repo.archive(db, comment_id)
