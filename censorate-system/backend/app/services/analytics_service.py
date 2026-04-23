from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.requirement import Requirement
from app.models.project import Project
from app.core.logger import get_logger

logger = get_logger(__name__)

# Default status colors if not specified
DEFAULT_COLORS = [
    "bg-gray-500",
    "bg-blue-500",
    "bg-amber-500",
    "bg-green-500",
    "bg-purple-500",
    "bg-pink-500",
    "bg-indigo-500",
    "bg-red-500",
]
DEFAULT_BG_COLORS = [
    "bg-gray-100",
    "bg-blue-100",
    "bg-amber-100",
    "bg-green-100",
    "bg-purple-100",
    "bg-pink-100",
    "bg-indigo-100",
    "bg-red-100",
]


def _get_status_from_swimlane(swimlane: str) -> str:
    """Convert swimlane name to status identifier."""
    return swimlane.lower().replace(" ", "_").replace("-", "_")


class AnalyticsService:
    """Analytics and reporting service."""

    def get_project_statistics(self, db: Session, project_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific project."""
        logger.info(f"Getting project statistics: {project_id}")

        # Get project and its swimlane configuration
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        swimlanes = project.settings.get("swimlanes", ["Backlog", "Todo", "In Review", "Done"])
        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

        total = len(requirements)

        # Count requirements per swimlane
        status_distribution = []
        for idx, swimlane in enumerate(swimlanes):
            status = _get_status_from_swimlane(swimlane)
            count = len([r for r in requirements if r.status == status])
            status_distribution.append({
                "status": status,
                "label": swimlane,
                "count": count,
                "percentage": (count / total) * 100 if total > 0 else 0,
                "color": DEFAULT_COLORS[idx % len(DEFAULT_COLORS)],
                "bg_color": DEFAULT_BG_COLORS[idx % len(DEFAULT_BG_COLORS)],
            })

        # Calculate completion rate (last swimlane is considered done)
        done_status = _get_status_from_swimlane(swimlanes[-1])
        done_count = len([r for r in requirements if r.status == done_status])

        return {
            "project_id": project_id,
            "total_requirements": total,
            "completion_rate": (done_count / total) * 100 if total > 0 else 0,
            "status_distribution": status_distribution
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
            if req.completed_at:
                monthly_trends[month]["completed"] += 1

        return sorted(list(monthly_trends.values()), key=lambda x: x["month"])

    def get_daily_throughput(self, db: Session, project_id: str, days: int = 14) -> List[Dict[str, Any]]:
        """Get daily throughput data for a project."""
        logger.info(f"Getting daily throughput for project: {project_id}, days: {days}")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days - 1)

        # Get all requirements for the project
        all_requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

        # Initialize all dates in range
        daily_data = {}
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            daily_data[date_str] = {
                "date": date_str,
                "completed": 0,
                "backlog": 0,
                "is_overload": False
            }

        # First pass: count requirements completed each day using completed_at field
        for req in all_requirements:
            if req.completed_at:
                date_str = req.completed_at.strftime("%Y-%m-%d")
                if date_str in daily_data:
                    daily_data[date_str]["completed"] += 1

        # Calculate backlog for each day:
        # For each day, count requirements that:
        # 1. Were created on or before that day
        # 2. Either are not completed OR were completed after that day
        sorted_dates = sorted(daily_data.keys())

        for date_str in sorted_dates:
            # Get date object and set to end of day (23:59:59)
            current_date = datetime.strptime(date_str, "%Y-%m-%d")
            current_date = current_date.replace(hour=23, minute=59, second=59)

            backlog_count = 0
            for req in all_requirements:
                # Requirement must be created on or before current date
                if req.created_at > current_date:
                    continue

                # If requirement is not completed OR was completed after current date
                if not req.completed_at or req.completed_at > current_date:
                    backlog_count += 1

            daily_data[date_str]["backlog"] = backlog_count

        return sorted(list(daily_data.values()), key=lambda x: x["date"])

    def get_member_workload(self, db: Session, project_id: str) -> List[Dict[str, Any]]:
        """Get member workload statistics for a project."""
        logger.info(f"Getting member workload for project: {project_id}")

        # Get project and its swimlane configuration
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            swimlanes = ["Backlog", "Todo", "In Review", "Done"]
        else:
            swimlanes = project.settings.get("swimlanes", ["Backlog", "Todo", "In Review", "Done"])

        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

        # Group by assigned_to
        member_workload: Dict[str, Dict[str, Any]] = {}

        for req in requirements:
            member_id = req.assigned_to or "unassigned"
            if member_id not in member_workload:
                # Initialize with all swimlanes
                workload = {
                    "member_id": member_id,
                    "member_name": member_id if member_id != "unassigned" else "Unassigned",
                    "total": 0
                }
                # Add each swimlane as a field
                for swimlane in swimlanes:
                    status = _get_status_from_swimlane(swimlane)
                    workload[status] = 0
                member_workload[member_id] = workload

            # Increment the count for the current status
            status = req.status or _get_status_from_swimlane(swimlanes[0])
            if status in member_workload[member_id]:
                member_workload[member_id][status] += 1
            member_workload[member_id]["total"] += 1

        return list(member_workload.values())
