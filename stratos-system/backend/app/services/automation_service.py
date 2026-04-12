"""Automation Service - manages automation rules and their execution.

Handles event-based and scheduled automation for Stratos Management System.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import AutomationRule, Project
from app.schemas.automation import (
    AutomationRuleCreate,
    AutomationRuleUpdate,
    AutomationRuleResponse
)
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException
)


class AutomationService:
    """Service for managing automation rules."""

    def get_rule(self, db: Session, rule_id: UUID) -> Optional[AutomationRule]:
        """Get an automation rule by ID.

        Args:
            db: Database session
            rule_id: Rule ID

        Returns:
            AutomationRule instance or None if not found
        """
        return db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()

    def get_rules(
        self,
        db: Session,
        project_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> List[AutomationRule]:
        """Get automation rules with optional filters.

        Args:
            db: Database session
            project_id: Optional project filter
            is_active: Optional active status filter

        Returns:
            List of AutomationRule instances
        """
        query = db.query(AutomationRule)

        if project_id:
            query = query.filter(AutomationRule.project_id == project_id)

        if is_active is not None:
            query = query.filter(AutomationRule.is_active == is_active)

        return query.order_by(AutomationRule.created_at.desc()).all()

    def create_rule(
        self,
        db: Session,
        rule_data: AutomationRuleCreate,
        user_id: str
    ) -> AutomationRule:
        """Create a new automation rule.

        Args:
            db: Database session
            rule_data: Rule creation data
            user_id: User creating the rule

        Returns:
            Created AutomationRule instance
        """
        # Verify project exists if project_id is provided
        if rule_data.project_id:
            project = db.query(Project).filter(Project.id == rule_data.project_id).first()
            if not project:
                raise NotFoundException("Project not found")

        # Validate rule data
        self._validate_rule_data(rule_data)

        # Create new rule
        rule = AutomationRule(
            name=rule_data.name,
            description=rule_data.description,
            project_id=rule_data.project_id,
            rule_type=rule_data.rule_type,
            conditions=rule_data.conditions,
            actions=rule_data.actions,
            schedule=rule_data.schedule,
            is_active=rule_data.is_active,
            created_by=user_id
        )

        db.add(rule)
        db.commit()
        db.refresh(rule)

        return rule

    def update_rule(
        self,
        db: Session,
        rule_id: UUID,
        rule_data: AutomationRuleUpdate,
        user_id: str
    ) -> AutomationRule:
        """Update an existing automation rule.

        Args:
            db: Database session
            rule_id: Rule ID
            rule_data: Rule update data
            user_id: User updating the rule

        Returns:
            Updated AutomationRule instance
        """
        rule = self.get_rule(db, rule_id)
        if not rule:
            raise NotFoundException("Automation rule not found")

        # Validate rule data
        if rule_data.conditions or rule_data.actions:
            self._validate_rule_data(rule_data)

        # Update rule fields
        update_data = rule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(rule, field):
                setattr(rule, field, value)

        db.commit()
        db.refresh(rule)

        return rule

    def delete_rule(self, db: Session, rule_id: UUID, user_id: str) -> None:
        """Delete an automation rule.

        Args:
            db: Database session
            rule_id: Rule ID
            user_id: User deleting the rule
        """
        rule = self.get_rule(db, rule_id)
        if not rule:
            raise NotFoundException("Automation rule not found")

        db.delete(rule)
        db.commit()

    def toggle_rule_status(
        self,
        db: Session,
        rule_id: UUID,
        user_id: str
    ) -> AutomationRule:
        """Toggle rule active status.

        Args:
            db: Database session
            rule_id: Rule ID
            user_id: User toggling the rule

        Returns:
            Updated AutomationRule instance
        """
        rule = self.get_rule(db, rule_id)
        if not rule:
            raise NotFoundException("Automation rule not found")

        rule.is_active = not rule.is_active
        db.commit()
        db.refresh(rule)

        return rule

    def execute_rule(
        self,
        db: Session,
        rule_id: UUID,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a rule.

        Args:
            db: Database session
            rule_id: Rule ID
            event_data: Event data

        Returns:
            Execution results
        """
        rule = self.get_rule(db, rule_id)
        if not rule:
            raise NotFoundException("Automation rule not found")

        if not rule.is_active:
            return {"rule": str(rule_id), "success": False, "message": "Rule is inactive"}

        # Check conditions
        if not self._check_conditions(rule.conditions, event_data):
            return {"rule": str(rule_id), "success": False, "message": "Conditions not met"}

        # Execute actions
        try:
            results = self._execute_actions(db, rule.actions, event_data)
            return {"rule": str(rule_id), "success": True, "results": results}
        except Exception as e:
            return {"rule": str(rule_id), "success": False, "message": str(e)}

    def execute_matching_rules(
        self,
        db: Session,
        event_type: str,
        event_data: Dict[str, Any],
        project_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Find and execute all rules that match an event.

        Args:
            db: Database session
            event_type: Type of event
            event_data: Event data
            project_id: Optional project filter

        Returns:
            List of execution results
        """
        rules = self.get_rules(db, project_id=project_id, is_active=True)

        results = []
        for rule in rules:
            if self._is_rule_matching(rule, event_type, event_data):
                execution_result = self.execute_rule(db, rule.id, event_data)
                results.append(execution_result)

        return results

    def _is_rule_matching(
        self,
        rule: AutomationRule,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """Check if a rule matches an event.

        Args:
            rule: Rule to check
            event_type: Type of event
            event_data: Event data

        Returns:
            True if rule matches, False otherwise
        """
        if rule.rule_type == "event-based":
            conditions = rule.conditions or {}
            if conditions.get("event_type") == event_type:
                return self._check_conditions(rule.conditions, event_data)

        return False

    def _check_conditions(
        self,
        conditions: Optional[Dict],
        event_data: Dict[str, Any]
    ) -> bool:
        """Check if conditions are met.

        Args:
            conditions: Conditions dictionary
            event_data: Event data

        Returns:
            True if all conditions are met
        """
        if not conditions:
            return True

        # TODO: Implement complex conditions checking

        return True

    def _execute_actions(
        self,
        db: Session,
        actions: Optional[Dict],
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute rule actions.

        Args:
            db: Database session
            actions: Actions dictionary
            event_data: Event data

        Returns:
            List of action execution results
        """
        if not actions:
            return []

        # TODO: Implement actual action execution
        return [
            {
                "action": "notification",
                "type": "email",
                "success": True,
                "message": "Notification sent"
            }
        ]

    def _validate_rule_data(self, rule_data: Any) -> None:
        """Validate rule creation or update data.

        Args:
            rule_data: Rule data to validate

        Raises:
            BadRequestException if data is invalid
        """
        if rule_data.rule_type == "event-based":
            if not rule_data.conditions or not rule_data.conditions.get("event_type"):
                raise BadRequestException("Event-based rules must specify event_type condition")

        if rule_data.rule_type == "scheduled":
            if not rule_data.schedule:
                raise BadRequestException("Scheduled rules must specify schedule")

        if not rule_data.conditions and not rule_data.actions:
            raise BadRequestException("Rule must have at least conditions or actions")
