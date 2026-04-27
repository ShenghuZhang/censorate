"""Profile service - manages user profile data."""

from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import or_, desc, func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.project import Project
from app.models.team_member import TeamMember
from app.models.requirement_status_history import RequirementStatusHistory
from app.models.comment import Comment


class ProfileService:
    """Service for managing user profiles."""

    def __init__(self):
        pass

    def get_user_projects(self, db: Session, user_id: UUID) -> List[Dict[str, Any]]:
        """Get all projects user is part of."""
        # Find team members with matching email
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        # Get team members by email
        team_members = (
            db.query(TeamMember)
            .filter(
                TeamMember.email == user.email,
                TeamMember.status == "active"
            )
            .order_by(TeamMember.joined_at.desc())
            .all()
        )

        # Get projects
        project_ids = [tm.project_id for tm in team_members]
        projects = db.query(Project).filter(Project.id.in_(project_ids)).all()

        # Map by ID
        project_map = {p.id: p for p in projects}

        # Return combined info
        result = []
        for tm in team_members:
            project = project_map.get(tm.project_id)
            if project:
                result.append({
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "role": tm.role,
                    "joined_at": tm.joined_at
                })

        return result

    def get_user_activity(self, db: Session, user_id: UUID) -> List[Dict[str, Any]]:
        """Get recent user activity."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        activities = []

        # Status changes by user
        status_changes = (
            db.query(RequirementStatusHistory)
            .filter(
                or_(
                    RequirementStatusHistory.changed_by == str(user_id),
                    RequirementStatusHistory.changed_by_name == user.name,
                    RequirementStatusHistory.changed_by_name == user.email.split('@')[0]
                )
            )
            .order_by(desc(RequirementStatusHistory.created_at))
            .limit(20)
            .all()
        )

        for change in status_changes:
            action = f"{change.from_status.replace('_', ' ').title()} → {change.to_status.replace('_', ' ').title()}"
            activities.append({
                "id": f"status_{change.id}",
                "type": "status_change",
                "action": "Changed status of",
                "target": f"REQ-{change.id}",
                "target_id": change.requirement_id,
                "timestamp": change.created_at,
                "note": change.note
            })

        # Comments by user
        comments = (
            db.query(Comment)
            .filter(
                or_(
                    Comment.author_id == str(user_id),
                    Comment.author_name == user.name,
                    Comment.author_name == user.email.split('@')[0]
                )
            )
            .order_by(desc(Comment.created_at))
            .limit(20)
            .all()
        )

        for comment in comments:
            activities.append({
                "id": f"comment_{comment.id}",
                "type": "comment",
                "action": "Commented on",
                "target": f"REQ-{comment.id}",
                "target_id": comment.requirement_id,
                "timestamp": comment.created_at,
                "note": comment.content[:100] if comment.content else None
            })

        # Sort by timestamp, newest first
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:10]

    def get_contribution_heatmap(self, db: Session, user_id: UUID) -> Dict[str, Any]:
        """Get user contribution heatmap data."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"contributions": [], "total": 0}

        # Get date one year ago
        one_year_ago = datetime.utcnow() - timedelta(days=365)

        contributions = {}

        # Status changes
        status_changes = (
            db.query(RequirementStatusHistory)
            .filter(
                or_(
                    RequirementStatusHistory.changed_by == str(user_id),
                    RequirementStatusHistory.changed_by_name == user.name
                ),
                RequirementStatusHistory.created_at >= one_year_ago
            )
            .all()
        )

        for change in status_changes:
            date_key = change.created_at.date().isoformat()
            contributions[date_key] = contributions.get(date_key, 0) + 1

        # Comments
        comments = (
            db.query(Comment)
            .filter(
                or_(
                    Comment.author_id == str(user_id),
                    Comment.author_name == user.name
                ),
                Comment.created_at >= one_year_ago
            )
            .all()
        )

        for comment in comments:
            date_key = comment.created_at.date().isoformat()
            contributions[date_key] = contributions.get(date_key, 0) + 1

        # Format for response
        contribution_list = []
        total = 0
        for date_str, count in contributions.items():
            contribution_list.append({
                "date": date_str,
                "count": count
            })
            total += count

        # Sort by date
        contribution_list.sort(key=lambda x: x["date"])

        return {
            "contributions": contribution_list,
            "total": total
        }


profile_service = ProfileService()
