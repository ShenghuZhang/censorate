from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.generated_file import GeneratedFile
from app.schemas.generation_project import GeneratedFileResponse, GeneratedFileDetailResponse

router = APIRouter()


@router.get("/projects/{project_id}/files", response_model=List[GeneratedFileResponse])
def list_files(project_id: str, db: Session = Depends(get_db)):
    """List all generated files for a project."""
    files = (
        db.query(GeneratedFile)
        .filter(GeneratedFile.project_id == project_id)
        .order_by(GeneratedFile.file_path.asc())
        .all()
    )
    return files


@router.get("/projects/{project_id}/files/{file_id}", response_model=GeneratedFileDetailResponse)
def get_file(project_id: str, file_id: str, db: Session = Depends(get_db)):
    """Get a single generated file with content."""
    file = (
        db.query(GeneratedFile)
        .filter(
            GeneratedFile.id == file_id,
            GeneratedFile.project_id == project_id,
        )
        .first()
    )
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file
