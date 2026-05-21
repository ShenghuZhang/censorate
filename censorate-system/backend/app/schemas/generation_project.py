from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.schemas.prd import PRDOutput
from app.schemas.architecture import ArchitectureOutput
from app.schemas.review import FileReview


class GenerationProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    user_story: str
    template_slug: str = "fastapi-nextjs"


class PRDConfirmation(BaseModel):
    confirmed: bool
    edited_prd: Optional[PRDOutput] = None
    feedback: Optional[str] = None


class CodeApproval(BaseModel):
    approved: bool
    feedback: Optional[str] = None


class PipelineStepResponse(BaseModel):
    id: UUID
    step_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class GeneratedFileResponse(BaseModel):
    id: UUID
    file_path: str
    language: Optional[str] = None
    step: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class GeneratedFileDetailResponse(GeneratedFileResponse):
    content: str


class GenerationProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    status: str
    template_id: UUID
    repo_url: Optional[str] = None
    created_at: datetime
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GenerationProjectDetailResponse(GenerationProjectResponse):
    prd_content: Optional[Dict[str, Any]] = None
    architecture_design: Optional[Dict[str, Any]] = None
    steps: List[PipelineStepResponse] = []
    files: List[GeneratedFileResponse] = []
