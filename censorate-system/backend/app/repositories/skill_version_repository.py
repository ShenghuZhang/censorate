"""Skill Version repository - provides database operations for skill version entities."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import SkillVersion
from .base_repository import BaseRepository


class SkillVersionRepository(BaseRepository):
    """Repository for SkillVersion entity."""

    def get(self, db: Session, id: UUID) -> Optional[SkillVersion]:
        """Get a single skill version by ID."""
        return db.query(SkillVersion).filter(SkillVersion.id == id).first()

    def get_all(self, db: Session) -> List[SkillVersion]:
        """Get all skill versions."""
        return db.query(SkillVersion).all()

    def create(self, db: Session, version: SkillVersion) -> SkillVersion:
        """Create a new skill version."""
        db.add(version)
        db.commit()
        db.refresh(version)
        return version

    def update(self, db: Session, version: SkillVersion) -> SkillVersion:
        """Update an existing skill version."""
        db.commit()
        db.refresh(version)
        return version

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a skill version by ID."""
        version = self.get(db, id)
        if version:
            db.delete(version)
            db.commit()

    def get_by_skill_and_version(
        self,
        db: Session,
        skill_id: UUID,
        version: str
    ) -> Optional[SkillVersion]:
        """Get a specific version for a skill."""
        return (
            db.query(SkillVersion)
            .filter(SkillVersion.skill_id == skill_id, SkillVersion.version == version)
            .first()
        )

    def get_latest_for_skill(
        self,
        db: Session,
        skill_id: UUID
    ) -> Optional[SkillVersion]:
        """Get the latest version for a skill."""
        return (
            db.query(SkillVersion)
            .filter(SkillVersion.skill_id == skill_id, SkillVersion.is_latest == True)
            .first()
        )

    def get_all_for_skill(
        self,
        db: Session,
        skill_id: UUID
    ) -> List[SkillVersion]:
        """Get all versions for a skill, ordered by creation date descending."""
        return (
            db.query(SkillVersion)
            .filter(SkillVersion.skill_id == skill_id)
            .order_by(desc(SkillVersion.created_at))
            .all()
        )

    def set_latest(self, db: Session, version_id: UUID) -> None:
        """Set a specific version as latest for its skill."""
        version = self.get(db, version_id)
        if version:
            # Unset all other versions as latest
            db.query(SkillVersion).filter(
                SkillVersion.skill_id == version.skill_id
            ).update({"is_latest": False})
            # Set this version as latest
            version.is_latest = True
            db.commit()

    def unset_latest_for_skill(self, db: Session, skill_id: UUID) -> None:
        """Unset latest flag for all versions of a skill."""
        db.query(SkillVersion).filter(
            SkillVersion.skill_id == skill_id
        ).update({"is_latest": False})
        db.commit()
