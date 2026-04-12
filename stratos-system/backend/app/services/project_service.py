from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.repositories.project_repository import ProjectRepository
from app.core.logger import get_logger
from app.exceptions import ProjectNotFoundError, ProjectAlreadyExistsError

logger = get_logger(__name__)


class ProjectService:
    """Project management service."""

    def __init__(self):
        """Initialize project service."""
        self.repository = ProjectRepository()

    def create_project(self, db: Session, project_data: ProjectCreate) -> Project:
        """Create a new project with validation."""
        logger.info(f"Creating project: {project_data.name}")

        # Check if project name already exists
        existing_project = db.query(Project).filter(Project.name == project_data.name).first()
        if existing_project:
            raise ProjectAlreadyExistsError(f"Project '{project_data.name}' already exists")

        # Create project with proper data
        project_data_dict = project_data.model_dump()
        # Set required fields that might not be in the schema
        if 'created_by' not in project_data_dict:
            project_data_dict['created_by'] = 'system'
        if 'slug' not in project_data_dict:
            project_data_dict['slug'] = project_data.name.lower().replace(' ', '-')

        project = Project(**project_data_dict)
        project = self.repository.create(db, project)
        logger.info(f"Project created successfully: {project.id}")
        return project

    def update_project(self, db: Session, project_id: UUID, project_data: ProjectUpdate) -> Project:
        """Update an existing project."""
        logger.info(f"Updating project: {project_id}")

        project = self.repository.get(db, project_id)
        if not project:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        # Check if name is being changed and if new name exists
        if project_data.name and project_data.name != project.name:
            existing_project = db.query(Project).filter(Project.name == project_data.name).first()
            if existing_project:
                raise ProjectAlreadyExistsError(f"Project '{project_data.name}' already exists")

        # Update project fields manually since repository's update expects an entity
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(project, field):
                setattr(project, field, value)

        updated_project = self.repository.update(db, project)
        logger.info(f"Project updated successfully: {project_id}")
        return updated_project

    def get_project(self, db: Session, project_id: UUID) -> Optional[Project]:
        """Get project by ID."""
        project = self.repository.get(db, project_id)
        if not project:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        return project

    def get_projects(self, db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects with pagination."""
        return self.repository.get_multi(db, skip, limit)

    def delete_project(self, db: Session, project_id: UUID) -> None:
        """Delete a project."""
        logger.info(f"Deleting project: {project_id}")

        project = self.repository.get(db, project_id)
        if not project:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        self.repository.delete(db, project_id)
        logger.info(f"Project deleted successfully: {project_id}")
