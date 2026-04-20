"""Skill repository - provides database operations for skill entities."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from ..models import Skill
from .base_repository import BaseRepository


class SkillRepository(BaseRepository):
    """Repository for Skill entity."""

    def get(self, db: Session, id: UUID) -> Optional[Skill]:
        """Get a single skill by ID."""
        return db.query(Skill).filter(Skill.id == id).first()

    def get_all(self, db: Session) -> List[Skill]:
        """Get all skills."""
        return db.query(Skill).all()

    def create(self, db: Session, skill: Skill) -> Skill:
        """Create a new skill."""
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill

    def update(self, db: Session, skill: Skill) -> Skill:
        """Update an existing skill."""
        db.commit()
        db.refresh(skill)
        return skill

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a skill by ID."""
        skill = self.get(db, id)
        if skill:
            db.delete(skill)
            db.commit()

    def get_by_slug(self, db: Session, slug: str) -> Optional[Skill]:
        """Get a skill by slug."""
        return db.query(Skill).filter(Skill.slug == slug).first()

    def get_all_published(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Skill]:
        """Get all published skills with pagination."""
        return (
            db.query(Skill)
            .filter(Skill.is_published == True, Skill.is_archived == False)
            .order_by(desc(Skill.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self,
        db: Session,
        category: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Skill]:
        """Get skills by category."""
        return (
            db.query(Skill)
            .filter(
                Skill.category == category,
                Skill.is_published == True,
                Skill.is_archived == False
            )
            .order_by(desc(Skill.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(
        self,
        db: Session,
        query: str,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Skill]:
        """Search skills by name or description."""
        q = db.query(Skill).filter(
            Skill.is_published == True,
            Skill.is_archived == False,
            or_(
                Skill.name.ilike(f"%{query}%"),
                Skill.description.ilike(f"%{query}%")
            )
        )
        if category:
            q = q.filter(Skill.category == category)
        return q.order_by(desc(Skill.created_at)).offset(skip).limit(limit).all()

    def get_popular(
        self,
        db: Session,
        limit: int = 10
    ) -> List[Skill]:
        """Get popular skills sorted by download count."""
        # Skills with stats.downloads field sorted descending
        return (
            db.query(Skill)
            .filter(Skill.is_published == True, Skill.is_archived == False)
            .order_by(desc(Skill.created_at))  # TODO: Use download stats when available
            .limit(limit)
            .all()
        )

    def increment_downloads(self, db: Session, skill_id: UUID) -> None:
        """Increment download count for a skill."""
        skill = self.get(db, skill_id)
        if skill:
            if not skill.stats:
                skill.stats = {}
            skill.stats["downloads"] = skill.stats.get("downloads", 0) + 1
            db.commit()

    def increment_views(self, db: Session, skill_id: UUID) -> None:
        """Increment view count for a skill."""
        skill = self.get(db, skill_id)
        if skill:
            if not skill.stats:
                skill.stats = {}
            skill.stats["views"] = skill.stats.get("views", 0) + 1
            db.commit()

    def get_categories(self, db: Session) -> List[str]:
        """Get all unique skill categories."""
        result = (
            db.query(Skill.category)
            .filter(Skill.is_published == True, Skill.is_archived == False)
            .distinct()
            .order_by(Skill.category)
            .all()
        )
        return [r[0] for r in result]

    def get_category_counts(self, db: Session) -> dict:
        """Get count of skills per category."""
        result = (
            db.query(Skill.category, func.count(Skill.id))
            .filter(Skill.is_published == True, Skill.is_archived == False)
            .group_by(Skill.category)
            .all()
        )
        return {category: count for category, count in result}

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Skill]:
        """Get multiple skills with pagination."""
        return (
            db.query(Skill)
            .filter(Skill.is_archived == False)
            .order_by(desc(Skill.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
