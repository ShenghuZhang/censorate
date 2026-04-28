"""Mention service - parse and handle @mentions in comments."""

import re
from typing import List, Tuple, Optional, Set
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import User, Requirement, Comment
from .notification_service import get_notification_service


class MentionService:
    """Service for parsing and handling @mentions."""

    # Regex pattern to match @mentions
    # Supports: @[Name](user-id) or @username
    MENTION_PATTERN = r'@\[([^\]]+)\]\(([^)]+)\)|@(\w+)'

    def __init__(self):
        self.notification_service = get_notification_service()

    def extract_mentions(self, content: str) -> List[Tuple[str, Optional[str]]]:
        """
        Extract mentions from comment content.

        Returns list of (name, user_id) tuples.
        user_id will be None for @username format (needs lookup).
        """
        mentions = []
        matches = re.finditer(self.MENTION_PATTERN, content)

        for match in matches:
            if match.group(1) and match.group(2):
                # Format: @[Name](user-id)
                mentions.append((match.group(1), match.group(2)))
            elif match.group(3):
                # Format: @username
                mentions.append((match.group(3), None))

        return mentions

    def find_mentioned_users(
        self,
        db: Session,
        content: str,
        project_id: Optional[UUID] = None
    ) -> List[User]:
        """Find all users mentioned in the content."""
        mentions = self.extract_mentions(content)
        if not mentions:
            return []

        user_ids: Set[str] = set()
        usernames: Set[str] = set()

        for name, user_id in mentions:
            if user_id:
                user_ids.add(user_id)
            else:
                usernames.add(name.lower())

        users: List[User] = []

        # Find users by ID
        if user_ids:
            id_users = db.query(User).filter(User.id.in_(user_ids)).all()
            users.extend(id_users)

        # Find users by name/email
        if usernames:
            name_users = db.query(User).filter(
                (User.name.ilike("%" + "%".join(usernames) + "%")) |
                (User.email.ilike("%" + "%".join(usernames) + "%"))
            ).all()
            users.extend(name_users)

        # Deduplicate
        seen = set()
        unique_users = []
        for user in users:
            if user.id not in seen:
                seen.add(user.id)
                unique_users.append(user)

        return unique_users

    def process_comment_mentions(
        self,
        db: Session,
        comment: Comment,
        requirement: Requirement,
        author_id: UUID,
        author_name: str
    ) -> None:
        """Process mentions in a comment and send notifications."""
        mentioned_users = self.find_mentioned_users(db, comment.content, requirement.project_id)

        # Don't notify the author
        mentioned_users = [u for u in mentioned_users if str(u.id) != str(author_id)]

        if not mentioned_users:
            return

        for user in mentioned_users:
            self.notification_service.create_mention_notification(
                db=db,
                user_id=user.id,
                requirement=requirement,
                comment_id=comment.id,
                mentioned_by=author_id,
                mentioned_by_name=author_name,
                comment_snippet=comment.content
            )


# Singleton instance
_mention_service: Optional[MentionService] = None


def get_mention_service() -> MentionService:
    """Get singleton mention service instance."""
    global _mention_service
    if _mention_service is None:
        _mention_service = MentionService()
    return _mention_service
