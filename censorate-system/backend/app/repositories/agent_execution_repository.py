"""Agent execution repository - provides data access layer for agent executions."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import AgentExecution
from .base_repository import BaseRepository


class AgentExecutionRepository(BaseRepository):
    """Repository for agent execution operations."""

    def get(self, db: Session, id: UUID) -> Optional[AgentExecution]:
        """Get a single agent execution by ID."""
        return db.query(AgentExecution).filter(AgentExecution.id == id).first()

    def get_all(self, db: Session) -> List[AgentExecution]:
        """Get all agent executions."""
        return db.query(AgentExecution).all()

    def create(self, db: Session, entity: AgentExecution) -> AgentExecution:
        """Create a new agent execution."""
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(self, db: Session, entity: AgentExecution) -> AgentExecution:
        """Update an existing agent execution."""
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, id: UUID) -> None:
        """Delete an agent execution by ID."""
        entity = db.query(AgentExecution).filter(AgentExecution.id == id).first()
        if entity:
            db.delete(entity)
            db.commit()

    def get_by_requirement(self, db: Session, requirement_id: UUID) -> List[AgentExecution]:
        """Get agent executions by requirement ID."""
        return db.query(AgentExecution).filter(AgentExecution.requirement_id == requirement_id).all()

    def get_current_execution(self, db: Session, requirement_id: UUID) -> Optional[AgentExecution]:
        """Get current running agent execution for a requirement."""
        return db.query(AgentExecution).filter(
            AgentExecution.requirement_id == requirement_id,
            AgentExecution.status == "running"
        ).first()
