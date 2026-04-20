"""Skill Download repository - provides database operations for skill download entities."""

from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import SkillDownload
from .base_repository import BaseRepository


class SkillDownloadRepository(BaseRepository):
    """Repository for SkillDownload entity."""

    def get(self, db: Session, id: UUID) -> Optional[SkillDownload]:
        """Get a single skill download by ID."""
        return db.query(SkillDownload).filter(SkillDownload.id == id).first()

    def get_all(self, db: Session) -> List[SkillDownload]:
        """Get all skill downloads."""
        return db.query(SkillDownload).all()

    def create(self, db: Session, download: SkillDownload) -> SkillDownload:
        """Create a new skill download."""
        db.add(download)
        db.commit()
        db.refresh(download)
        return download

    def update(self, db: Session, download: SkillDownload) -> SkillDownload:
        """Update an existing skill download."""
        db.commit()
        db.refresh(download)
        return download

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a skill download by ID."""
        download = self.get(db, id)
        if download:
            db.delete(download)
            db.commit()

    def get_by_skill(
        self,
        db: Session,
        skill_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[SkillDownload]:
        """Get downloads for a skill."""
        return (
            db.query(SkillDownload)
            .filter(SkillDownload.skill_id == skill_id)
            .order_by(desc(SkillDownload.downloaded_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_skill_and_hour(
        self,
        db: Session,
        skill_id: UUID,
        identity_hash: str,
        hour_start: datetime
    ) -> Optional[SkillDownload]:
        """Check if there's already a download for this identity in the hour."""
        return (
            db.query(SkillDownload)
            .filter(
                SkillDownload.skill_id == skill_id,
                SkillDownload.identity_hash == identity_hash,
                SkillDownload.hour_start == hour_start
            )
            .first()
        )

    def count_by_skill(self, db: Session, skill_id: UUID) -> int:
        """Count total downloads for a skill."""
        return (
            db.query(SkillDownload)
            .filter(SkillDownload.skill_id == skill_id)
            .count()
        )

    def count_recent_by_skill(
        self,
        db: Session,
        skill_id: UUID,
        days: int = 7
    ) -> int:
        """Count downloads for a skill in the last N days."""
        since = datetime.utcnow() - timedelta(days=days)
        return (
            db.query(SkillDownload)
            .filter(
                SkillDownload.skill_id == skill_id,
                SkillDownload.downloaded_at >= since
            )
            .count()
        )

    def get_total_downloads(self, db: Session) -> int:
        """Get total number of downloads across all skills."""
        return db.query(SkillDownload).count()
