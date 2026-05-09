from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
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
from app.schemas.attachment import AttachmentResponse
from app.services.requirement_service import RequirementService
from app.services.comment_service import CommentService
from app.services.attachment_service import AttachmentService
from app.repositories.requirement_status_history_repository import RequirementStatusHistoryRepository
from app.core.exceptions import (
    NotFoundException,
    StateTransitionException,
    BadRequestException
)

router = APIRouter()
requirement_service = RequirementService()
comment_service = CommentService()
attachment_service = AttachmentService()
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
async def transition_requirement(
    requirement_id: str,
    transition: RequirementTransition,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Transition requirement status."""
    from uuid import UUID
    try:
        req_uuid = UUID(requirement_id)
        # transition_with_agent handles agent dispatch + status update
        await requirement_service.transition_with_agent(
            db=db,
            requirement_id=req_uuid,
            to_status=transition.to_status
        )
        requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
        if not requirement:
            raise NotFoundException(f"Requirement {requirement_id} not found")
        
        # Dispatch to AI agent in background (session-safe)
        background_tasks.add_task(
            requirement_service._dispatch_to_assigned_agent_background,
            requirement.id, transition.to_status
        )
        
        return requirement
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid ID: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/requirements/{requirement_id}/transition-with-data", response_model=RequirementResponse)
async def transition_requirement_with_data(
    requirement_id: str,
    transition: RequirementTransitionWithData,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Transition requirement with assignment and expected date."""
    from uuid import UUID
    try:
        req_uuid = UUID(requirement_id)
        await requirement_service.transition_with_data(
            db,
            req_uuid,
            transition.to_status,
            transition.assigned_to,
            transition.assigned_to_name,
            transition.expected_completion_at,
            transition.note,
            transition.changed_by,
            transition.changed_by_name
        )
        db_req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
        if not db_req:
            raise NotFoundException(f"Requirement {requirement_id} not found")
        # Dispatch to AI agent if assigned to one (runs in background, session-safe)
        background_tasks.add_task(
            requirement_service._dispatch_to_assigned_agent_background,
            db_req.id, transition.to_status
        )
        return db_req
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid ID: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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


@router.post("/requirements/{requirement_id}/upload-attachment", response_model=AttachmentResponse)
async def upload_attachment(
    requirement_id: str,
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    """Upload an attachment to a requirement (stored in MinIO)."""
    attachment = await attachment_service.upload_attachment(
        db=db,
        requirement_id=requirement_id,
        file=file,
        uploaded_by="default-user",
        uploaded_by_name="Default User",
        description=description
    )
    return attachment_service.get_attachment_with_url(db, attachment)


@router.get("/requirements/{requirement_id}/attachments", response_model=List[AttachmentResponse])
def list_attachments(
    requirement_id: str,
    db: Session = Depends(get_db)
):
    """List all attachments for a requirement."""
    attachments = attachment_service.get_requirement_attachments(db, requirement_id)
    return [attachment_service.get_attachment_with_url(db, a) for a in attachments]


@router.delete("/requirements/{requirement_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    requirement_id: str,
    attachment_id: str,
    db: Session = Depends(get_db)
):
    """Delete an attachment from MinIO and database."""
    # Verify attachment belongs to requirement
    attachment = attachment_service.get_attachment(db, attachment_id)
    if not attachment or str(attachment.requirement_id) != requirement_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    success = attachment_service.delete_attachment(db, attachment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    return None


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
