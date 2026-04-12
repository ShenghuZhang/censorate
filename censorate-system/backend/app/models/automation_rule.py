"""AutomationRule model - defines automation rules for Censorate."""

from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from .base import UUIDType, BaseModel, JsonType
from sqlalchemy.orm import relationship


class AutomationRule(BaseModel):
    """
    Automation rule model - defines conditions and actions for automated processes.

    Examples of automation rules:
    - When a requirement is moved to 'Analysis' lane, automatically execute
      the AnalysisAgent
    - When a requirement is returned, notify the assigned team member
    - When a requirement is completed, automatically close associated tasks
    """

    __tablename__ = "automation_rules"

    project_id = Column(UUIDType, ForeignKey("projects.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    rule_type = Column(String(50), default="event-based", nullable=False)
    conditions = Column(JsonType, nullable=True)
    actions = Column(JsonType, nullable=True)
    schedule = Column(String(50), nullable=True)
    created_by = Column(String, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="automation_rules")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<AutomationRule {self.name}>"

    @classmethod
    def create_event_based_rule(
        cls,
        name: str,
        description: str,
        project_id: str,
        created_by: str,
        conditions: dict,
        actions: dict
    ):
        """
        Create a new event-based automation rule.

        Args:
            name: Rule name
            description: Rule description
            project_id: Project ID the rule belongs to
            created_by: User who created the rule
            conditions: Event conditions
            actions: Actions to execute

        Returns:
            AutomationRule instance
        """
        return cls(
            name=name,
            description=description,
            project_id=project_id,
            rule_type="event-based",
            conditions=conditions,
            actions=actions,
            is_active=True,
            created_by=created_by
        )

    @classmethod
    def create_scheduled_rule(
        cls,
        name: str,
        description: str,
        project_id: str,
        created_by: str,
        schedule: str,
        conditions: dict,
        actions: dict
    ):
        """
        Create a new scheduled automation rule.

        Args:
            name: Rule name
            description: Rule description
            project_id: Project ID the rule belongs to
            created_by: User who created the rule
            schedule: Cron schedule for execution
            conditions: Conditions to check before executing
            actions: Actions to execute

        Returns:
            AutomationRule instance
        """
        return cls(
            name=name,
            description=description,
            project_id=project_id,
            rule_type="scheduled",
            schedule=schedule,
            conditions=conditions,
            actions=actions,
            is_active=True,
            created_by=created_by
        )
