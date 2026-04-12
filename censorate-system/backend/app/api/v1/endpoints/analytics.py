"""Analytics endpoints for Censorate API."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.analytics_service import AnalyticsService
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/projects/{project_id}/analytics")
def get_project_analytics(project_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get detailed analytics for a specific project."""
    logger.info(f"Getting analytics for project: {project_id}")

    try:
        analytics_service = AnalyticsService()
        statistics = analytics_service.get_project_statistics(db, project_id)
        return statistics
    except Exception as e:
        logger.error(f"Failed to get project analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project analytics"
        )


@router.get("/projects/{project_id}/analytics/trends")
def get_project_trends(project_id: str, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get requirement trend analysis for a project."""
    logger.info(f"Getting trends for project: {project_id}")

    try:
        analytics_service = AnalyticsService()
        trends = analytics_service.get_requirement_trend_analysis(db, project_id)
        return trends
    except Exception as e:
        logger.error(f"Failed to get project trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project trends"
        )


@router.get("/analytics/projects")
def get_all_projects_analytics(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get analytics for all projects."""
    logger.info("Getting analytics for all projects")

    try:
        analytics_service = AnalyticsService()
        statistics = analytics_service.get_all_projects_statistics(db)
        return statistics
    except Exception as e:
        logger.error(f"Failed to get all projects analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects analytics"
        )
