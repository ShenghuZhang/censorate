"""Profile API endpoints for Censorate API."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import User
from app.schemas.profile import (
    UserProjectResponse,
    UserActivityResponse,
    UserContributionHeatmapResponse,
    UserProfileResponse
)
from app.services.profile_service import profile_service


router = APIRouter()


@router.get("/users/{user_id}/projects", response_model=List[UserProjectResponse])
def get_user_projects(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's projects."""
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    projects = profile_service.get_user_projects(db, user_uuid)
    return projects


@router.get("/users/{user_id}/activity", response_model=List[UserActivityResponse])
def get_user_activity(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's recent activity."""
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    activities = profile_service.get_user_activity(db, user_uuid)
    return activities


@router.get("/users/{user_id}/heatmap", response_model=UserContributionHeatmapResponse)
def get_user_heatmap(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's contribution heatmap."""
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    heatmap = profile_service.get_contribution_heatmap(db, user_uuid)
    return heatmap


@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get full user profile."""
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    projects = profile_service.get_user_projects(db, user_uuid)
    activities = profile_service.get_user_activity(db, user_uuid)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "projects": projects,
        "recent_activity": activities,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }
