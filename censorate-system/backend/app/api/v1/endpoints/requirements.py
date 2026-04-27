from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.requirement import Requirement
from app.models.project import Project
from app.schemas.requirement import (
    RequirementCreate, RequirementUpdate, RequirementResponse,
    RequirementTransition, RequirementTransitionWithData
)
from app.schemas.requirement_status_history import RequirementStatusHistoryResponse
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.requirement_service import RequirementService
from app.services.comment_service import CommentService
from app.repositories.requirement_status_history_repository import RequirementStatusHistoryRepository
from app.core.exceptions import (
    NotFoundException,
    StateTransitionException,
    BadRequestException
)

router = APIRouter()
requirement_service = RequirementService()
comment_service = CommentService()
history_repo = RequirementStatusHistoryRepository()


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

    # Get initial status from project swimlane configuration if available
    initial_status = "backlog"
    if project.settings and "swimlanes" in project.settings and len(project.settings["swimlanes"]) > 0:
        # Use the first swimlane, convert to snake_case for status
        first_lane = project.settings["swimlanes"][0]
        initial_status = first_lane.lower().replace(' ', '_')

    requirement = Requirement(
        project_id=project_id,
        req_number=req_number,
        title=requirement_in.title,
        description=requirement_in.description,
        status=initial_status,
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
    db.flush()  # Flush to get the ID without committing yet

    # Create initial history record
    from app.models.requirement_status_history import RequirementStatusHistory
    history = RequirementStatusHistory(
        requirement_id=requirement.id,
        from_status=None,
        to_status=initial_status,
        changed_by=requirement.created_by,
        note="Requirement created",
        is_backward=False,
        changed_at=requirement.created_at
    )
    db.add(history)

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
    """Transition a requirement to a new status (supports dynamic swimlanes)."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.archived_at.is_(None)
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )

    # Get project for potential backward transition detection (optional)
    project = db.query(Project).filter(Project.id == requirement.project_id).first()

    # Get swimlane configuration from project settings if available
    swimlanes = []
    if project and project.settings and "swimlanes" in project.settings:
        swimlanes = project.settings["swimlanes"]

    # Try to detect backward transitions using project swimlane order if available
    if swimlanes:
        try:
            # Convert status to display names for comparison (handle slugified vs display names)
            from_slug = requirement.status.lower().replace('_', ' ')
            to_slug = transition.to_status.lower().replace('_', ' ')

            # Find indices (case-insensitive partial match)
            from_index = None
            to_index = None

            for i, lane in enumerate(swimlanes):
                lane_slug = lane.lower().replace(' ', '_')
                if lane_slug == requirement.status or lane.lower() == from_slug:
                    from_index = i
                if lane_slug == transition.to_status or lane.lower() == to_slug:
                    to_index = i

            if from_index is not None and to_index is not None and to_index < from_index:
                requirement.return_count += 1
                requirement.last_returned_at = datetime.utcnow()
        except Exception:
            # If anything fails, skip backward transition tracking
            pass

    requirement.status = transition.to_status

    # Check if we're moving to a "done-like" state (last swimlane or contains "done"/"complete" in name)
    is_done_state = False
    if swimlanes and transition.to_status == swimlanes[-1].lower().replace(' ', '_'):
        is_done_state = True
    elif "done" in transition.to_status.lower() or "complete" in transition.to_status.lower():
        is_done_state = True

    if is_done_state:
        requirement.completed_at = datetime.utcnow()
    else:
        requirement.completed_at = None

    db.commit()
    db.refresh(requirement)
    return requirement


@router.post("/requirements/{requirement_id}/transition-with-data", response_model=RequirementResponse)
def transition_requirement_with_data(
    requirement_id: str,
    transition: RequirementTransitionWithData,
    db: Session = Depends(get_db)
):
    """Transition requirement with assignment and expected date."""
    import asyncio
    try:
        # Run async function synchronously
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        requirement = loop.run_until_complete(
            requirement_service.transition_with_data(
                db,
                requirement_id,
                transition.to_status,
                transition.assigned_to,
                transition.assigned_to_name,
                transition.expected_completion_at,
                transition.note,
                transition.changed_by,
                transition.changed_by_name
            )
        )
        # Refresh from DB to get updated entity
        db_req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
        return db_req
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/requirements/{requirement_id}/history", response_model=List[RequirementStatusHistoryResponse])
def get_requirement_history(
    requirement_id: str,
    db: Session = Depends(get_db)
):
    """Get status history for a requirement."""
    # Verify requirement exists
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.archived_at.is_(None)
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )

    history = history_repo.get_by_requirement(db, requirement_id)
    return history


@router.get("/requirements/{requirement_id}/comments", response_model=List[CommentResponse])
def get_comments(
    requirement_id: str,
    db: Session = Depends(get_db)
):
    """Get comments for a requirement."""
    # Verify requirement exists
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.archived_at.is_(None)
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )

    comments = comment_service.get_comments(db, requirement_id)
    return comments


@router.post("/requirements/{requirement_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    requirement_id: str,
    comment: CommentCreate,
    db: Session = Depends(get_db)
):
    """Create a comment."""
    # Verify requirement exists
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.archived_at.is_(None)
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )

    print(f"\n=== Creating comment ===")
    print(f"Received data: {comment.model_dump()}")

    new_comment = comment_service.create_comment(
        db,
        requirement_id,
        comment.model_dump()
    )

    print(f"Created comment: author_name={new_comment.author_name}, content={new_comment.content[:30]}...")
    return new_comment


@router.post("/requirements/{requirement_id}/upload-attachment")
async def upload_attachment(
    requirement_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an attachment."""
    # Verify requirement exists
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.archived_at.is_(None)
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )

    # TODO: Implement actual file upload
    # For now, return a mock response
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "File upload placeholder - implementation needed"
    }


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
