"""Requirement Service - manages requirements lifecycle and agent integration."""

from typing import Dict, Optional, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models import Requirement, AgentExecution
from ..repositories import (
    RequirementRepository,
    AgentExecutionRepository,
    LaneRoleRepository
)
from .deepagent_service import DeepAgentService
from .lark_service import LarkService


class RequirementService:
    """Service for managing requirements with agent integration."""

    def __init__(
        self,
        deepagent_service: DeepAgentService,
        lark_service: LarkService,
        req_repo: RequirementRepository = None,
        agent_exec_repo: AgentExecutionRepository = None,
        lane_role_repo: LaneRoleRepository = None
    ):
        """Initialize requirement service."""
        self.deepagent = deepagent_service
        self.lark = lark_service
        self.req_repo = req_repo or RequirementRepository()
        self.agent_exec_repo = agent_exec_repo or AgentExecutionRepository()
        self.lane_role_repo = lane_role_repo or LaneRoleRepository()

    def get_requirement(self, db: Session, requirement_id: UUID) -> Optional[Requirement]:
        """Get a single requirement by ID."""
        return self.req_repo.get(db, requirement_id)

    def get_all_requirements(self, db: Session) -> list:
        """Get all requirements."""
        return self.req_repo.get_all(db)

    def create_requirement(self, db: Session, data: Dict) -> Requirement:
        """Create a new requirement."""
        requirement = Requirement(**data)
        return self.req_repo.create(db, requirement)

    async def transition_with_agent(
        self,
        db: Session,
        requirement_id: UUID,
        to_status: str,
        user_id: Optional[UUID] = None,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transition requirement with agent execution.

        Args:
            db: Database session
            requirement_id: Requirement ID
            to_status: Target status/lane
            user_id: Optional user ID performing the transition
            thread_id: Optional Deep Agent thread ID

        Returns:
            Transition result
        """
        requirement = self.req_repo.get(db, requirement_id)
        if not requirement:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(f"Requirement {requirement_id} not found")

        # Get lane role configuration
        lane_role = self.lane_role_repo.get_by_lane(
            db, requirement.project_id, to_status
        )

        if lane_role and lane_role.is_active and lane_role.agent_type:
            # Execute the associated agent
            result = await self._execute_lane_agent(
                db, requirement, lane_role, thread_id
            )

            if result.get("success"):
                await self._update_requirement_status(
                    db, requirement_id, to_status, result
                )

            return result
        else:
            # No agent configured, just update status
            return await self._update_requirement_status(
                db, requirement_id, to_status, {}
            )

    async def _execute_lane_agent(
        self,
        db: Session,
        requirement: Requirement,
        lane_role,
        thread_id: Optional[str]
    ) -> Dict[str, Any]:
        """Execute agent for the lane."""
        from ..agents import get_agent_class
        agent_class = get_agent_class(lane_role.agent_type)
        if not agent_class:
            return {
                "success": False,
                "error": f"Agent type '{lane_role.agent_type}' not found"
            }

        agent = agent_class(
            deepagent_service=self.deepagent,
            lark_service=self.lark,
            config=lane_role.config
        )

        context = await self._build_agent_context(db, requirement)

        requirement_data = {
            "id": str(requirement.id),
            "title": requirement.title,
            "description": requirement.description,
            "status": requirement.status,
        }

        result = await agent.process(requirement_data, context, thread_id=thread_id)

        return result

    async def _build_agent_context(self, db: Session, requirement: Requirement) -> Dict:
        """Build context data for agent execution."""
        previous_executions = self.agent_exec_repo.get_by_requirement(
            db, requirement.id
        )[:5]

        return {
            "project_id": str(requirement.project_id),
            "requirement_id": str(requirement.id),
            "current_status": requirement.status,
            "previous_executions": [
                {
                    "agent_type": exec.agent_type,
                    "status": exec.status,
                    "output": exec.output_data
                }
                for exec in previous_executions
            ],
            "thread_id": requirement.current_thread_id
        }

    async def _update_requirement_status(
        self,
        db: Session,
        requirement_id: UUID,
        to_status: str,
        result: Dict
    ) -> Dict[str, Any]:
        """Update requirement status and related fields."""
        requirement = self.req_repo.get(db, requirement_id)

        # Check for backward move
        from app.state_machine.requirement_state_machine import RequirementStateMachine

        # Get project for state machine check
        project = db.query(Requirement).filter(Requirement.id == requirement_id).first()
        if project:
            if RequirementStateMachine.is_backward_transition(
                requirement.status, to_status, "technical"
            ):
                requirement.return_count += 1
                requirement.last_returned_at = datetime.now(timezone.utc)

        requirement.status = to_status

        if result.get("thread_id"):
            requirement.current_thread_id = result.get("thread_id")

        if result.get("result"):
            requirement.ai_suggestions = result.get("result")

        if to_status == "done":
            requirement.completed_at = datetime.now(timezone.utc)

        self.req_repo.update(db, requirement)

        return {
            "success": True,
            "requirement_id": str(requirement_id)
        }

    async def create_from_lark(
        self,
        db: Session,
        project_id: UUID,
        lark_message: Dict,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Create a requirement from a Lark message."""
        title = self._extract_title(lark_message)
        description = self._extract_description(lark_message)

        req_number = await self._get_next_req_number(db, project_id)

        lark_doc = None
        if self.lark:
            try:
                lark_doc = await self.lark.create_document(
                    title=f"REQ-{req_number}: {title}",
                    content=f"# {title}\n\n{description}"
                )
            except Exception:
                lark_doc = None

        requirement = Requirement(
            project_id=project_id,
            req_id=f"REQ-{req_number}",
            title=title,
            description=description,
            status="backlog",
            source="lark",
            source_metadata=lark_message,
            lark_doc_token=lark_doc.get("token") if lark_doc else None,
            lark_doc_url=lark_doc.get("url") if lark_doc else None,
            lark_editable=bool(lark_doc),
            created_by=user_id,
        )

        self.req_repo.create(db, requirement)

        return {
            "success": True,
            "requirement": requirement
        }

    def _extract_title(self, lark_message: Dict) -> str:
        """Extract title from Lark message."""
        return lark_message.get("title", "New Requirement")

    def _extract_description(self, lark_message: Dict) -> str:
        """Extract description from Lark message."""
        return lark_message.get("content", "")

    async def _get_next_req_number(self, db: Session, project_id: UUID) -> int:
        """Get next requirement number."""
        requirements = self.req_repo.get_by_project(db, project_id)
        return len(requirements) + 1
