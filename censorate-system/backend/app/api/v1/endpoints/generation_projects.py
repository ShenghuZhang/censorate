from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from app.api.deps import get_db
from app.models.template import Template
from app.models.generation_project import GenerationProject
from app.models.pipeline_step import PipelineStep
from app.models.generated_file import GeneratedFile
from app.schemas.generation_project import (
    GenerationProjectCreate,
    GenerationProjectResponse,
    GenerationProjectDetailResponse,
    PRDConfirmation,
    CodeApproval,
    PipelineStepResponse,
    GeneratedFileResponse,
)
from app.state_machine.generation_state_machine import GenerationStateMachine, GenerationState
from app.services.pipeline_orchestrator import PipelineOrchestrator
from app.core.config import Settings

router = APIRouter()


def _get_project(db: Session, project_id: str) -> GenerationProject:
    project = (
        db.query(GenerationProject)
        .options(
            joinedload(GenerationProject.steps),
            joinedload(GenerationProject.files),
            joinedload(GenerationProject.template),
        )
        .filter(GenerationProject.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/", response_model=List[GenerationProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """List all generation projects."""
    return db.query(GenerationProject).order_by(GenerationProject.created_at.desc()).all()


@router.post("/", response_model=GenerationProjectResponse, status_code=201)
def create_project(data: GenerationProjectCreate, db: Session = Depends(get_db)):
    """Create a new generation project."""
    template = db.query(Template).filter(Template.slug == data.template_slug).first()
    if not template:
        raise HTTPException(status_code=400, detail=f"Template '{data.template_slug}' not found")
    project = GenerationProject(
        name=data.name,
        description=data.description,
        user_story=data.user_story,
        template_id=template.id,
        status=GenerationState.DRAFT,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=GenerationProjectDetailResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get project details with steps and files."""
    project = _get_project(db, project_id)
    return project


@router.post("/{project_id}/confirm", response_model=GenerationProjectDetailResponse)
def confirm_prd(
    project_id: str,
    body: PRDConfirmation,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Confirm PRD and trigger architecture design."""
    project = _get_project(db, project_id)

    if not GenerationStateMachine.can_transition(project.status, GenerationState.CONFIRMED):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot confirm from state '{project.status}'",
        )

    project.status = GenerationState.CONFIRMED
    if body.edited_prd:
        project.prd_content = body.edited_prd.model_dump()
    db.commit()

    settings = Settings.get()
    orchestrator = PipelineOrchestrator(settings)
    background_tasks.add_task(orchestrator.run_analysis, project_id)

    db.refresh(project)
    return project


@router.post("/{project_id}/approve-architecture", response_model=GenerationProjectDetailResponse)
def approve_architecture(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Approve architecture design and trigger code generation."""
    project = _get_project(db, project_id)

    if not GenerationStateMachine.can_transition(project.status, GenerationState.GENERATING):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start code generation from state '{project.status}'",
        )

    project.status = GenerationState.GENERATING
    db.commit()

    settings = Settings.get()
    orchestrator = PipelineOrchestrator(settings)
    background_tasks.add_task(orchestrator.run_code_generation, project_id)

    db.refresh(project)
    return project


@router.post("/{project_id}/approve-code", response_model=GenerationProjectDetailResponse)
def approve_code(
    project_id: str,
    body: CodeApproval,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Approve generated code and trigger GitHub push."""
    project = _get_project(db, project_id)

    if not GenerationStateMachine.can_transition(project.status, GenerationState.PUSHING):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start push from state '{project.status}'",
        )

    project.status = GenerationState.PUSHING
    db.commit()

    settings = Settings.get()
    orchestrator = PipelineOrchestrator(settings)
    background_tasks.add_task(orchestrator.run_push, project_id)

    db.refresh(project)
    return project


@router.post("/{project_id}/retry", response_model=GenerationProjectDetailResponse)
def retry_project(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Retry pipeline from the last failed step."""
    project = _get_project(db, project_id)

    if not GenerationStateMachine.is_retryable(project.status):
        raise HTTPException(
            status_code=400,
            detail=f"Project is not in a retryable state ({project.status})",
        )

    settings = Settings.get()
    orchestrator = PipelineOrchestrator(settings)

    # Find the last failed step
    failed_step = (
        db.query(PipelineStep)
        .filter(
            PipelineStep.project_id == project_id,
            PipelineStep.status == "failed",
        )
        .order_by(PipelineStep.started_at.desc())
        .first()
    )

    if failed_step:
        background_tasks.add_task(orchestrator.retry_pipeline, project_id, failed_step.step_type)
    else:
        # No explicit failed step found, restart from analysis
        background_tasks.add_task(orchestrator.run_analysis, project_id)

    db.refresh(project)
    return project


@router.post("/{project_id}/cancel", response_model=GenerationProjectDetailResponse)
def cancel_project(project_id: str, db: Session = Depends(get_db)):
    """Cancel project and reset to draft."""
    project = _get_project(db, project_id)

    if not GenerationStateMachine.can_transition(project.status, GenerationState.DRAFT):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel from state '{project.status}'",
        )

    project.status = GenerationState.DRAFT
    project.error_message = None
    db.commit()
    db.refresh(project)
    return project
