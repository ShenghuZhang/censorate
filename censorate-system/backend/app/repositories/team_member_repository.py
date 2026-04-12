"""Team Member repository - provides database operations for team member entities."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import TeamMember
from .base_repository import BaseRepository


class TeamMemberRepository(BaseRepository):
    """Repository for TeamMember entity."""

    def get(self, db: Session, id: UUID) -> Optional[TeamMember]:
        """Get a single team member by ID."""
        return db.query(TeamMember).filter(TeamMember.id == id).first()

    def get_all(self, db: Session) -> List[TeamMember]:
        """Get all team members."""
        return db.query(TeamMember).all()

    def get_by_project(self, db: Session, project_id: UUID) -> List[TeamMember]:
        """Get all team members for a specific project."""
        return db.query(TeamMember).filter(TeamMember.project_id == project_id).all()

    def get_ai_agents(self, db: Session, project_id: UUID) -> List[TeamMember]:
        """Get all AI agents in a project."""
        return db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.type == "ai"
        ).all()

    def get_human_members(self, db: Session, project_id: UUID) -> List[TeamMember]:
        """Get all human team members in a project."""
        return db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.type == "human"
        ).all()

    def get_by_role(self, db: Session, project_id: UUID, role: str) -> List[TeamMember]:
        """Get all team members with a specific role in a project."""
        return db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.role == role
        ).all()

    def create(self, db: Session, team_member: TeamMember) -> TeamMember:
        """Create a new team member."""
        db.add(team_member)
        db.commit()
        db.refresh(team_member)
        return team_member

    def update(self, db: Session, team_member: TeamMember) -> TeamMember:
        """Update an existing team member."""
        db.commit()
        db.refresh(team_member)
        return team_member

    def delete(self, db: Session, id: UUID) -> None:
        """Delete a team member by ID."""
        team_member = self.get(db, id)
        if team_member:
            db.delete(team_member)
            db.commit()
