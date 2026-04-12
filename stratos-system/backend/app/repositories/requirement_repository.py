"""Requirement repository - provides data access layer for requirements."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import Requirement
from .base_repository import BaseRepository


class RequirementRepository(BaseRepository):
    """Repository for requirement operations."""

    def get(self, db: Session, id: UUID) -> Optional[Requirement]:
        """Get a single requirement by ID."""
        return db.query(Requirement).filter(Requirement.id == id).first()

    def get_all(self, db: Session) -> List[Requirement]:
        """Get all requirements."""
        return db.query(Requirement).all()

    def create(self, db: Session, entity: Requirement) -> Requirement:
        """Create a new requirement."""
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(self, db: Session, entity: Requirement) -> Requirement:
        """Update an existing requirement."""
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a requirement by ID."""
        entity = db.query(Requirement).filter(Requirement.id == id).first()
        if entity:
            db.delete(entity)
            db.commit()

    def get_by_project(self, db: Session, project_id: UUID) -> List[Requirement]:
        """Get all requirements for a project."""
        return db.query(Requirement).filter(Requirement.project_id == project_id).all()

    def get_by_status(self, db: Session, project_id: UUID, status: str) -> List[Requirement]:
        """Get requirements by project and status."""
        return db.query(Requirement).filter(
            Requirement.project_id == project_id,
            Requirement.status == status
        ).all()

    def get_by_req_id(self, db: Session, project_id: UUID, req_id: str) -> Optional[Requirement]:
        """Get requirement by project and req_id."""
        return db.query(Requirement).filter(
            Requirement.project_id == project_id,
            Requirement.req_id == req_id
        ).first()
