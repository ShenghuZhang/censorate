from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.requirement import Requirement
from app.models.project import Project
from app.schemas.requirement import RequirementCreate, RequirementUpdate, RequirementResponse, RequirementTransition
from app.core.exceptions import (
    NotFoundException,
    StateTransitionException,
    BadRequestException
)

router = APIRouter()


def get_next_req_number(project_id: str, db: Session) -> int:
    """Get the next requirement number for a project."""
    max_req = db.query(Requirement).filter(
        Requirement.project_id == project_id
    ).order_by(Requirement.req_number.desc()).first()
    return (max_req.req_number + 1) if max_req else 1


@router.get("/projects/{project_id}/requirements", response_model=List[RequirementResponse])
def list_requirements(project_id: str, db: Session = Depends(get_db)):
    """List all requirements for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    requirements = db.query(Requirement).filter(
        Requirement.project_id == project_id,
        Requirement.archived_at.is_(None)
    ).order_by(Requirement.req_number).all()
    return requirements


@router.post("/projects/{project_id}/requirements", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
def create_requirement(
    project_id: str,
    requirement_in: RequirementCreate,
    db: Session = Depends(get_db)
):
    """Create a new requirement."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    req_number = get_next_req_number(project_id, db)

    requirement = Requirement(
        project_id=project_id,
        req_number=req_number,
        title=requirement_in.title,
        description=requirement_in.description,
        status="backlog",
        priority=requirement_in.priority,
        source=requirement_in.source,
        source_metadata=requirement_in.source_metadata,
        lark_doc_token=requirement_in.lark_doc_token,
        lark_doc_url=requirement_in.lark_doc_url,
        lark_editable=requirement_in.lark_editable,
        created_by="default-user",
        return_count=0
    )
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement


@router.get("/requirements/{requirement_id}", response_model=RequirementResponse)
def get_requirement(requirement_id: str, db: Session = Depends(get_db)):
    """Get a requirement by ID."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.archived_at.is_(None)
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    return requirement


@router.put("/requirements/{requirement_id}", response_model=RequirementResponse)
def update_requirement(
    requirement_id: str,
    requirement_in: RequirementUpdate,
    db: Session = Depends(get_db)
):
    """Update a requirement."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.archived_at.is_(None)
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )

    update_data = requirement_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(requirement, field, value)

    db.commit()
    db.refresh(requirement)
    return requirement


@router.delete("/requirements/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_requirement(requirement_id: str, db: Session = Depends(get_db)):
    """Delete (archive) a requirement."""
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    requirement.archived_at = datetime.utcnow()
    db.commit()
    return None


@router.post("/requirements/{requirement_id}/transition", response_model=RequirementResponse)
def transition_requirement(
    requirement_id: str,
    transition: RequirementTransition,
    db: Session = Depends(get_db)
):
    """Transition a requirement to a new status."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.archived_at.is_(None)
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )

    from app.state_machine.requirement_state_machine import RequirementStateMachine
    project = db.query(Project).filter(Project.id == requirement.project_id).first()

    if not RequirementStateMachine.can_transition(
        requirement.status, transition.to_status, project.project_type
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from {requirement.status} to {transition.to_status}"
        )

    # Check if it's a backward transition
    if RequirementStateMachine.is_backward_transition(
        requirement.status, transition.to_status, project.project_type
    ):
        requirement.return_count += 1
        requirement.last_returned_at = datetime.utcnow()

    requirement.status = transition.to_status

    if transition.to_status == "done":
        requirement.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(requirement)
    return requirement


@router.post("/requirements/{requirement_id}/ai-analyze")
def ai_analyze_requirement(requirement_id: str, db: Session = Depends(get_db)):
    """Trigger AI analysis for a requirement."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.archived_at.is_(None)
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )

    # TODO: Implement actual AI analysis
    return {"message": "AI analysis triggered", "requirement_id": requirement_id}
