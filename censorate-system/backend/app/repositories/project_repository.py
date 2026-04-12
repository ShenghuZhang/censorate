"""Project repository - provides database operations for project entities."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import Project
from .base_repository import BaseRepository


class ProjectRepository(BaseRepository):
    """Repository for Project entity."""

    def get(self, db: Session, id: UUID) -> Optional[Project]:
        """Get a single project by ID."""
        return db.query(Project).filter(Project.id == id).first()

    def get_all(self, db: Session) -> List[Project]:
        """Get all projects."""
        return db.query(Project).all()

    def get_by_slug(self, db: Session, slug: str) -> Optional[Project]:
        """Get a project by slug."""
        return db.query(Project).filter(Project.slug == slug).first()

    def create(self, db: Session, project: Project) -> Project:
        """Create a new project."""
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def update(self, db: Session, project: Project) -> Project:
        """Update an existing project."""
        db.commit()
        db.refresh(project)
        return project

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a project by ID."""
        project = self.get(db, id)
        if project:
            db.delete(project)
            db.commit()

    def search(self, db: Session, query: str) -> List[Project]:
        """Search projects by name or description."""
        return db.query(Project).filter(
            (Project.name.ilike(f"%{query}%")) |
            (Project.description.ilike(f"%{query}%"))
        ).all()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get multiple projects with pagination."""
        return db.query(Project).offset(skip).limit(limit).all()
