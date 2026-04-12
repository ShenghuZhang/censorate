from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.requirement import Requirement
from app.models.project import Project
from app.core.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Analytics and reporting service."""

    def get_project_statistics(self, db: Session, project_id: int) -> Dict[str, Any]:
        """Get detailed statistics for a specific project."""
        logger.info(f"Getting project statistics: {project_id}")

        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

        total = len(requirements)
        done = len([r for r in requirements if r.status == "done"])
        in_review = len([r for r in requirements if r.status == "in_review"])
        todo = len([r for r in requirements if r.status == "todo"])
        backlog = len([r for r in requirements if r.status == "backlog"])

        return {
            "project_id": project_id,
            "total_requirements": total,
            "done": done,
            "in_review": in_review,
            "todo": todo,
            "backlog": backlog,
            "completion_rate": (done / total) * 100 if total > 0 else 0,
            "status_distribution": [
                {"status": "backlog", "count": backlog, "percentage": (backlog / total) * 100 if total > 0 else 0},
                {"status": "todo", "count": todo, "percentage": (todo / total) * 100 if total > 0 else 0},
                {"status": "in_review", "count": in_review, "percentage": (in_review / total) * 100 if total > 0 else 0},
                {"status": "done", "count": done, "percentage": (done / total) * 100 if total > 0 else 0}
            ]
        }

    def get_all_projects_statistics(self, db: Session) -> List[Dict[str, Any]]:
        """Get statistics for all projects."""
        logger.info("Getting all projects statistics")

        projects = db.query(Project).all()
        statistics = []

        for project in projects:
            project_stats = self.get_project_statistics(db, project.id)
            statistics.append({
                **project_stats,
                "project_name": project.name,
                "project_type": project.project_type,
                "created_at": project.created_at
            })

        return statistics

    def get_requirement_trend_analysis(self, db: Session, project_id: int) -> List[Dict[str, Any]]:
        """Get requirement trend analysis for a project."""
        logger.info(f"Getting requirement trend analysis for project: {project_id}")

        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

        monthly_trends = {}
        for req in requirements:
            month = req.created_at.strftime("%Y-%m")
            if month not in monthly_trends:
                monthly_trends[month] = {
                    "month": month,
                    "created": 0,
                    "completed": 0
                }
            monthly_trends[month]["created"] += 1
            if req.status == "done":
                monthly_trends[month]["completed"] += 1

        return sorted(list(monthly_trends.values()), key=lambda x: x["month"])
