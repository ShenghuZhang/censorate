"""Skill File repository - provides database operations for skill file entities."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import SkillFile
from .base_repository import BaseRepository


class SkillFileRepository(BaseRepository):
    """Repository for SkillFile entity."""

    def get(self, db: Session, id: UUID) -> Optional[SkillFile]:
        """Get a single skill file by ID."""
        return db.query(SkillFile).filter(SkillFile.id == id).first()

    def get_all(self, db: Session) -> List[SkillFile]:
        """Get all skill files."""
        return db.query(SkillFile).all()

    def create(self, db: Session, file: SkillFile) -> SkillFile:
        """Create a new skill file."""
        db.add(file)
        db.commit()
        db.refresh(file)
        return file

    def update(self, db: Session, file: SkillFile) -> SkillFile:
        """Update an existing skill file."""
        db.commit()
        db.refresh(file)
        return file

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a skill file by ID."""
        file = self.get(db, id)
        if file:
            db.delete(file)
            db.commit()

    def get_by_version(self, db: Session, version_id: UUID) -> List[SkillFile]:
        """Get all files for a version."""
        return (
            db.query(SkillFile)
            .filter(SkillFile.version_id == version_id)
            .order_by(SkillFile.path)
            .all()
        )

    def get_by_version_and_path(
        self,
        db: Session,
        version_id: UUID,
        path: str
    ) -> Optional[SkillFile]:
        """Get a specific file by version and path."""
        return (
            db.query(SkillFile)
            .filter(SkillFile.version_id == version_id, SkillFile.path == path)
            .first()
        )
