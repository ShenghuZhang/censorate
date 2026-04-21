from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter()

# Default swimlane configuration
DEFAULT_SWIMLANES = ["Backlog", "Todo", "In Review", "Done"]


@router.get("", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """List all projects."""
    projects = db.query(Project).filter(Project.archived_at.is_(None)).all()
    return projects


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new project."""
    slug = project_in.name.lower().replace(" ", "-")

    # Build settings
    settings = {}
    if project_in.settings:
        settings = project_in.settings.model_dump(exclude_unset=True)

    # Set default swimlanes if not provided
    if "swimlanes" not in settings:
        settings["swimlanes"] = DEFAULT_SWIMLANES

    project = Project(
        name=project_in.name,
        slug=slug,
        description=project_in.description,
        project_type=project_in.project_type,
        created_by="default-user",
        settings=settings
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get a project by ID."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.archived_at.is_(None)
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update a project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.archived_at.is_(None)
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    update_data = project_in.model_dump(exclude_unset=True)

    # Handle settings merge (not overwrite)
    if "settings" in update_data:
        new_settings = update_data.pop("settings")
        # Merge with existing settings
        project.settings = {**project.settings, **new_settings}

    # Handle other fields
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Delete (archive) a project."""
    from datetime import datetime
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    project.archived_at = datetime.utcnow()
    db.commit()
    return None
