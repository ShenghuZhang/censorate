"""Automation rule schemas - request/response models for automation rules."""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from uuid import UUID


class AutomationRuleBase(BaseModel):
    """Base schema for automation rule."""

    name: str = Field(..., min_length=1, max_length=255, description="Rule name")
    description: Optional[str] = Field(None, max_length=1000, description="Rule description")
    rule_type: str = Field("event-based", description="Rule type: 'event-based' or 'scheduled'")
    conditions: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Conditions dictionary")
    actions: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Actions dictionary")
    schedule: Optional[str] = Field(None, description="Cron schedule for scheduled rules")
    is_active: bool = Field(True, description="Whether the rule is active")


class AutomationRuleCreate(AutomationRuleBase):
    """Schema for creating a new automation rule."""

    project_id: Optional[UUID] = Field(None, description="Optional project ID")

    @model_validator(mode='after')
    def validate_rule_type(self):
        """Validate rule type-specific fields."""
        rule_type = self.rule_type
        schedule = self.schedule
        conditions = self.conditions

        if rule_type == "scheduled" and not schedule:
            raise ValueError("Scheduled rules must have a schedule")

        if rule_type == "event-based" and (not conditions or "event_type" not in conditions):
            raise ValueError("Event-based rules must specify event_type condition")

        return self


class AutomationRuleUpdate(BaseModel):
    """Schema for updating an automation rule."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    rule_type: Optional[str] = Field(None, description="Rule type: 'event-based' or 'scheduled'")
    conditions: Optional[Dict[str, Any]] = Field(None)
    actions: Optional[Dict[str, Any]] = Field(None)
    schedule: Optional[str] = Field(None, description="Cron schedule for scheduled rules")
    is_active: Optional[bool] = Field(None)

    @model_validator(mode='after')
    def validate_rule_type(self):
        """Validate rule type-specific fields."""
        rule_type = self.rule_type
        schedule = self.schedule
        conditions = self.conditions

        if rule_type == "scheduled" and not schedule:
            raise ValueError("Scheduled rules must have a schedule")

        if rule_type == "event-based" and conditions and "event_type" not in conditions:
            raise ValueError("Event-based rules must specify event_type condition")

        return self


class AutomationRuleResponse(BaseModel):
    """Schema for automation rule response."""

    id: UUID
    name: str
    description: Optional[str]
    project_id: Optional[UUID]
    rule_type: str
    conditions: Optional[Dict[str, Any]]
    actions: Optional[Dict[str, Any]]
    schedule: Optional[str]
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class AutomationRuleListResponse(BaseModel):
    """Schema for list of automation rules."""

    count: int
    rules: list[AutomationRuleResponse]


class AutomationExecutionResult(BaseModel):
    """Schema for automation rule execution result."""

    rule: str
    success: bool
    message: Optional[str] = None
    results: Optional[list[Dict[str, Any]]] = None


class AutomationExecutionRequest(BaseModel):
    """Schema for manual rule execution request."""

    event_data: Dict[str, Any] = Field(default_factory=dict)
