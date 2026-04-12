"""Lane role repository - provides data access layer for lane roles."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import LaneRole
from .base_repository import BaseRepository


class LaneRoleRepository(BaseRepository):
    """Repository for lane role operations."""

    def get(self, db: Session, id: UUID) -> Optional[LaneRole]:
        """Get a single lane role by ID."""
        return db.query(LaneRole).filter(LaneRole.id == id).first()

    def get_all(self, db: Session) -> List[LaneRole]:
        """Get all lane roles."""
        return db.query(LaneRole).all()

    def create(self, db: Session, entity: LaneRole) -> LaneRole:
        """Create a new lane role."""
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(self, db: Session, entity: LaneRole) -> LaneRole:
        """Update an existing lane role."""
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a lane role by ID."""
        entity = db.query(LaneRole).filter(LaneRole.id == id).first()
        if entity:
            db.delete(entity)
            db.commit()

    def get_by_project(self, db: Session, project_id: UUID) -> List[LaneRole]:
        """Get all lane roles for a project."""
        return db.query(LaneRole).filter(LaneRole.project_id == project_id).all()

    def get_by_lane(self, db: Session, project_id: UUID, lane: str) -> Optional[LaneRole]:
        """Get lane role by project and lane name."""
        return db.query(LaneRole).filter(
            LaneRole.project_id == project_id,
            LaneRole.lane == lane
        ).first()
