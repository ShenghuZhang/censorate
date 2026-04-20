from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.requirement import Requirement
from app.models.project import Project
from app.core.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Analytics and reporting service."""

    def get_project_statistics(self, db: Session, project_id: str) -> Dict[str, Any]:
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

    def get_requirement_trend_analysis(self, db: Session, project_id: str) -> List[Dict[str, Any]]:
        """Get requirement trend analysis for a project (deprecated - use get_daily_throughput)."""
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

    def get_daily_throughput(self, db: Session, project_id: str, days: int = 14) -> List[Dict[str, Any]]:
        """Get daily throughput data for a project."""
        logger.info(f"Getting daily throughput for project: {project_id}, days: {days}")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days - 1)

        # Initialize all dates in range
        daily_data = {}
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            daily_data[date_str] = {
                "date": date_str,
                "created": 0,
                "completed": 0,
                "is_overload": False
            }

        # Count created requirements by day
        requirements = db.query(Requirement).filter(
            Requirement.project_id == project_id,
            Requirement.created_at >= start_date
        ).all()

        for req in requirements:
            date_str = req.created_at.strftime("%Y-%m-%d")
            if date_str in daily_data:
                daily_data[date_str]["created"] += 1

        # Count completed requirements by day (using updated_at for done status)
        completed_reqs = db.query(Requirement).filter(
            Requirement.project_id == project_id,
            Requirement.status == "done",
            Requirement.updated_at >= start_date
        ).all()

        for req in completed_reqs:
            date_str = req.updated_at.strftime("%Y-%m-%d")
            if date_str in daily_data:
                daily_data[date_str]["completed"] += 1

        # Mark overload days (created > 5)
        for date_str in daily_data:
            if daily_data[date_str]["created"] > 5:
                daily_data[date_str]["is_overload"] = True

        return sorted(list(daily_data.values()), key=lambda x: x["date"])

    def get_member_workload(self, db: Session, project_id: str) -> List[Dict[str, Any]]:
        """Get member workload statistics for a project."""
        logger.info(f"Getting member workload for project: {project_id}")

        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

        # Group by assigned_to
        member_workload: Dict[str, Dict[str, Any]] = {}

        for req in requirements:
            member_id = req.assigned_to or "unassigned"
            if member_id not in member_workload:
                member_workload[member_id] = {
                    "member_id": member_id,
                    "member_name": member_id if member_id != "unassigned" else "Unassigned",
                    "todo": 0,
                    "in_review": 0,
                    "done": 0,
                    "total": 0
                }

            if req.status == "todo":
                member_workload[member_id]["todo"] += 1
            elif req.status == "in_review":
                member_workload[member_id]["in_review"] += 1
            elif req.status == "done":
                member_workload[member_id]["done"] += 1

            member_workload[member_id]["total"] += 1

        return list(member_workload.values())
