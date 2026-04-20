"""Skills API endpoints - complete skill management with version control and ZIP downloads."""

import json
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from app.api.deps import get_db
from app.services import get_skill_service
from app.schemas import (
    SkillCreate, SkillUpdate, SkillResponse, SkillListResponse,
    SkillVersionResponse, CategoryListResponse, SkillUploadResponse,
    SkillSearchResponse
)
from app.core.exceptions import NotFoundException, ValidationException, ConflictException

router = APIRouter()
skill_service = get_skill_service()


# ===== Skill List & Search =====

@router.get("/skills", response_model=SkillListResponse)
def list_skills(
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all available skills with optional category filter.

    Supports pagination and category filtering.
    """
    skills, total = skill_service.list_skills(db, category, skip, limit)
    return {
        "count": total,
        "skip": skip,
        "limit": limit,
        "skills": [SkillResponse.model_validate(s) for s in skills]
    }


@router.get("/skills/categories", response_model=CategoryListResponse)
def list_categories(db: Session = Depends(get_db)):
    """
    List all skill categories and their counts.
    """
    categories, counts = skill_service.get_categories(db)
    return {
        "categories": categories,
        "counts": counts
    }


@router.get("/skills/search", response_model=SkillSearchResponse)
def search_skills(
    q: str = Query(..., min_length=1, max_length=200),
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search skills by name or description.

    Args:
        q: Search query string
        category: Optional category filter
        skip: Pagination skip
        limit: Pagination limit
    """
    skills, total = skill_service.search_skills(db, q, category, skip, limit)
    return {
        "count": total,
        "results": [
            {
                "skill": SkillResponse.model_validate(s),
                "relevance_score": 1.0  # TODO: Implement proper relevance scoring
            }
            for s in skills
        ]
    }


@router.get("/skills/popular")
def get_popular_skills(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get popular skills based on download statistics.
    """
    # TODO: Implement proper popularity based on stats
    skills, _ = skill_service.list_skills(db, None, 0, limit)
    return {
        "count": len(skills),
        "skills": [SkillResponse.model_validate(s) for s in skills]
    }


# ===== Skill CRUD =====

@router.get("/skills/{slug}", response_model=SkillResponse)
def get_skill(slug: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific skill.

    Includes skill metadata, latest version, and file list.
    """
    try:
        skill = skill_service.get_skill(db, slug, increment_views=True)

        # Load versions for response
        versions = skill_service.list_versions(db, skill.id)
        latest_version = None

        if skill.latest_version_id:
            latest_version = next((v for v in versions if v.id == skill.latest_version_id), None)

        return SkillResponse(
            **skill.to_dict(),
            latest_version=SkillVersionResponse.model_validate(latest_version) if latest_version else None,
            versions=[SkillVersionResponse.model_validate(v) for v in versions]
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/skills", status_code=status.HTTP_201_CREATED, response_model=SkillUploadResponse)
async def upload_skill(
    files: List[UploadFile] = File(...),
    metadata: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload and publish a new skill.

    Accepts multiple files with a metadata JSON. The SKILL.md file is required.

    Args:
        files: List of uploaded files
        metadata: JSON string with skill metadata (name, description, category, tags, version, changelog)
    """
    try:
        # Parse metadata
        metadata_dict = json.loads(metadata)
        skill_data = SkillCreate(
            name=metadata_dict.get("name"),
            description=metadata_dict.get("description"),
            category=metadata_dict.get("category"),
            tags=metadata_dict.get("tags", [])
        )

        # Read file contents
        skill_files = []
        for file in files:
            content = await file.read()
            filename = file.filename or ""

            # Check if it's a ZIP file
            if filename.lower().endswith(".zip"):
                from app.services.storage_service import get_storage_service
                storage_service = get_storage_service()
                extracted_files = storage_service.extract_zip(content)
                skill_files.extend(extracted_files)
            else:
                skill_files.append({
                    "path": filename,
                    "content": content,
                    "filename": filename
                })

        # Create skill
        version = metadata_dict.get("version", "1.0.0")
        changelog = metadata_dict.get("changelog", "Initial version")

        skill = skill_service.create_skill(
            db,
            skill_data,
            skill_files,
            owner_id=None  # TODO: Get from auth
        )

        # Create version (create_skill does this, but let's set it to latest and publish)
        skill.is_published = True
        skill_service.skill_repo.update(db, skill)

        # Refresh skill with versions
        skill = skill_service.get_skill(db, skill.slug)

        return {
            "status": "success",
            "message": f"Skill '{skill.name}' uploaded successfully",
            "skill": SkillResponse.model_validate(skill)
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid metadata JSON"
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.put("/skills/{slug}", response_model=SkillResponse)
def update_skill(
    slug: str,
    data: SkillUpdate,
    db: Session = Depends(get_db)
):
    """
    Update skill metadata.

    This updates the skill's name, description, tags, etc. To upload a new version,
    use the version upload endpoint.
    """
    try:
        skill = skill_service.get_skill(db, slug)
        updated_skill = skill_service.update_skill(db, skill.id, data)
        return SkillResponse.model_validate(updated_skill)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/skills/{slug}", status_code=status.HTTP_200_OK)
def archive_skill(slug: str, db: Session = Depends(get_db)):
    """
    Archive (soft delete) a skill.

    The skill will no longer appear in list/search results but can be restored.
    """
    try:
        skill = skill_service.get_skill(db, slug)
        skill_service.archive_skill(db, skill.id)
        return {
            "status": "success",
            "message": f"Skill '{slug}' archived successfully"
        }
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ===== Version Management =====

@router.get("/skills/{slug}/versions")
def list_versions(slug: str, db: Session = Depends(get_db)):
    """
    List all versions of a skill.
    """
    try:
        skill = skill_service.get_skill(db, slug)
        versions = skill_service.list_versions(db, skill.id)
        return {
            "count": len(versions),
            "versions": [SkillVersionResponse.model_validate(v) for v in versions]
        }
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/skills/{slug}/versions/{version}")
def get_version(slug: str, version: str, db: Session = Depends(get_db)):
    """
    Get a specific version of a skill.
    """
    try:
        skill = skill_service.get_skill(db, slug)
        ver = skill_service.get_version(db, skill.id, version)

        # Load files
        files = skill_service.get_files_for_version(db, ver.id)
        ver_dict = ver.to_dict()
        ver_dict["files"] = [f.to_dict() for f in files]

        return ver_dict
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/skills/{slug}/versions", status_code=status.HTTP_201_CREATED)
async def upload_version(
    slug: str,
    files: List[UploadFile] = File(...),
    version: str = Form(...),
    changelog: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a new version of an existing skill.
    """
    try:
        skill = skill_service.get_skill(db, slug)

        # Read file contents
        skill_files = []
        for file in files:
            content = await file.read()
            skill_files.append({
                "path": file.filename,
                "content": content,
                "filename": file.filename
            })

        # Create version
        ver = skill_service.create_version(
            db,
            skill.id,
            skill_files,
            version,
            changelog
        )

        # Set as latest
        skill_service.set_latest_version(db, skill.id, ver.id)

        return {
            "status": "success",
            "message": f"Version {version} uploaded successfully",
            "version": SkillVersionResponse.model_validate(ver)
        }
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# ===== File Access =====

@router.get("/skills/{slug}/files/{file_path:path}")
def get_file(
    slug: str,
    file_path: str,
    version: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get a specific file from a skill.

    If no version is specified, uses the latest version.
    """
    try:
        skill = skill_service.get_skill(db, slug)

        # Get version
        if version:
            ver = skill_service.get_version(db, skill.id, version)
        elif skill.latest_version_id:
            ver = skill_service.version_repo.get(db, skill.latest_version_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No version available"
            )

        if not ver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )

        content = skill_service.get_file_content(db, ver.id, file_path)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Determine content type
        file_record = skill_service.file_repo.get_by_version_and_path(db, ver.id, file_path)
        media_type = file_record.content_type if file_record else "text/plain"

        return StreamingResponse(
            BytesIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f'inline; filename="{file_path}"'}
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ===== ZIP Download =====

@router.get("/skills/{slug}/download")
def download_skill(
    slug: str,
    version: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Download a skill as a ZIP file.

    Args:
        slug: Skill slug
        version: Optional version (uses latest if not provided)
    """
    try:
        skill = skill_service.get_skill(db, slug)

        # Get version
        ver = None
        if version:
            ver = skill_service.get_version(db, skill.id, version)
            version_id = ver.id
        else:
            version_id = skill.latest_version_id

        if not version_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No version available"
            )

        # Generate ZIP
        zip_content = skill_service.generate_zip(db, skill.id, version_id)

        # Record download (use IP as identity)
        # TODO: Get real client IP
        skill_service.record_download(db, skill.id, version_id, "anonymous")

        version_str = ver.version if ver else "latest"
        filename = f"{skill.slug}-{version_str}.zip"

        return StreamingResponse(
            BytesIO(zip_content),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "private, max-age=60"
            }
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
