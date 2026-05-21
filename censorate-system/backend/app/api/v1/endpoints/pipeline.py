from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.pipeline_step import PipelineStep
from app.schemas.generation_project import PipelineStepResponse

router = APIRouter()


@router.get("/projects/{project_id}/steps", response_model=List[PipelineStepResponse])
def list_steps(project_id: str, db: Session = Depends(get_db)):
    """List all pipeline steps for a project."""
    steps = (
        db.query(PipelineStep)
        .filter(PipelineStep.project_id == project_id)
        .order_by(PipelineStep.started_at.asc())
        .all()
    )
    return steps
