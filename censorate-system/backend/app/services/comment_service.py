"""Comment service - manages comment operations."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import Comment
from ..repositories import CommentRepository


class CommentService:
    """Service for managing comments."""

    def __init__(self, comment_repo: CommentRepository = None):
        self.comment_repo = comment_repo or CommentRepository()

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
        return self.comment_repo.create(db, comment)

    def update_comment(self, db: Session, comment_id: UUID, data: Dict) -> Optional[Comment]:
        """Update a comment."""
        comment = self.comment_repo.get(db, comment_id)
        if not comment:
            return None

        if "content" in data:
            comment.content = data["content"]

        return self.comment_repo.update(db, comment)

    def delete_comment(self, db: Session, comment_id: UUID) -> bool:
        """Delete (archive) a comment."""
        return self.comment_repo.archive(db, comment_id)
