"""Automation API endpoints - manage automation rules and execution."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.deps import get_db
from app.services.automation_service import AutomationService
from app.schemas.automation import (
    AutomationRuleCreate,
    AutomationRuleUpdate,
    AutomationRuleResponse,
    AutomationExecutionRequest,
    AutomationExecutionResult
)

router = APIRouter()
automation_service = AutomationService()


@router.get("/automation/rules")
def list_automation_rules(
    project_id: UUID = None,
    is_active: bool = None
):
    """
    List all automation rules with optional filters.

    Args:
        project_id: Optional project filter
        is_active: Optional active status filter

    Returns:
        List of automation rules
    """
    rules = automation_service.get_rules(project_id=project_id, is_active=is_active)
    return {
        "count": len(rules),
        "rules": [rule for rule in rules]
    }


@router.get("/automation/rules/{rule_id}", response_model=AutomationRuleResponse)
def get_automation_rule(rule_id: UUID):
    """
    Get a single automation rule by ID.

    Args:
        rule_id: Rule ID

    Returns:
        Automation rule details
    """
    rule = automation_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation rule not found"
        )
    return rule


@router.post("/automation/rules", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
def create_automation_rule(
    rule_data: AutomationRuleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new automation rule.

    Args:
        rule_data: Rule creation data

    Returns:
        Created rule details
    """
    # TODO: Get current user from token
    user_id = "system"

    try:
        rule = automation_service.create_rule(db, rule_data, user_id)
        return rule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/automation/rules/{rule_id}", response_model=AutomationRuleResponse)
def update_automation_rule(
    rule_id: UUID,
    rule_data: AutomationRuleUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing automation rule.

    Args:
        rule_id: Rule ID
        rule_data: Rule update data

    Returns:
        Updated rule details
    """
    rule = automation_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation rule not found"
        )

    try:
        # TODO: Get current user from token
        user_id = "system"
        updated_rule = automation_service.update_rule(db, rule_id, rule_data, user_id)
        return updated_rule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/automation/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_automation_rule(rule_id: UUID, db: Session = Depends(get_db)):
    """
    Delete an automation rule.

    Args:
        rule_id: Rule ID
    """
    rule = automation_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation rule not found"
        )

    # TODO: Get current user from token
    user_id = "system"
    automation_service.delete_rule(db, rule_id, user_id)


@router.post("/automation/rules/{rule_id}/execute")
def execute_automation_rule(
    rule_id: UUID,
    request: AutomationExecutionRequest,
    db: Session = Depends(get_db)
):
    """
    Manually execute an automation rule.

    Args:
        rule_id: Rule ID
        request: Execution request data

    Returns:
        Execution results
    """
    result = automation_service.execute_rule(db, rule_id, request.event_data)
    return result


@router.post("/automation/events/{event_type}/execute")
def execute_events(
    event_type: str,
    request: AutomationExecutionRequest,
    project_id: UUID = None,
    db: Session = Depends(get_db)
):
    """
    Execute all matching rules for an event.

    Args:
        event_type: Event type
        request: Execution request data
        project_id: Optional project filter

    Returns:
        List of execution results
    """
    results = automation_service.execute_matching_rules(
        db, event_type, request.event_data, project_id
    )
    return {
        "count": len(results),
        "results": results
    }


@router.post("/automation/rules/{rule_id}/toggle")
def toggle_automation_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Toggle an automation rule active/inactive.

    Args:
        rule_id: Rule ID

    Returns:
        Updated rule details
    """
    rule = automation_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation rule not found"
        )

    # TODO: Get current user from token
    user_id = "system"
    updated_rule = automation_service.toggle_rule_status(db, rule_id, user_id)
    return updated_rule
