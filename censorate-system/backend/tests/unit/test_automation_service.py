"""
Tests for AutomationService.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.automation_service import AutomationService
from app.schemas.automation import AutomationRuleCreate, AutomationRuleUpdate
from app.models.automation_rule import AutomationRule
from app.core.exceptions import NotFoundException, BadRequestException


class TestAutomationService:
    """Tests for AutomationService functionality."""

    def test_get_rule(self, mock_db_session: Session):
        """Test getting an automation rule by ID."""
        automation_service = AutomationService()
        rule_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_rule = Mock(spec=AutomationRule)
        mock_rule.id = rule_id

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_rule

        result = automation_service.get_rule(mock_db_session, rule_id)
        assert result == mock_rule

    def test_get_rule_not_found(self, mock_db_session: Session):
        """Test getting a rule that doesn't exist."""
        automation_service = AutomationService()
        rule_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Note: get_rule returns None, doesn't raise
        result = automation_service.get_rule(mock_db_session, rule_id)
        assert result is None

    def test_create_rule(self, mock_db_session: Session):
        """Test creating an automation rule."""
        automation_service = AutomationService()
        rule_data = AutomationRuleCreate(
            name="Test Rule",
            description="Test automation rule",
            rule_type="event-based",
            conditions={"event_type": "requirement_created"},
            actions={"transition": "analysis"},
            schedule=None,
            is_active=True,
            project_id=None
        )

        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        with patch.object(automation_service, '_validate_rule_data'):
            result = automation_service.create_rule(mock_db_session, rule_data, "test-user-id")

            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once()

    def test_update_rule(self, mock_db_session: Session):
        """Test updating an automation rule."""
        automation_service = AutomationService()
        rule_id = UUID("12345678-1234-5678-1234-567812345678")
        update_data = AutomationRuleUpdate(
            name="Updated Rule Name",
            description="Updated description"
        )

        mock_rule = Mock(spec=AutomationRule)
        mock_rule.id = rule_id
        mock_rule.name = "Old Name"
        mock_rule.description = "Old description"

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_rule

        with patch.object(automation_service, '_validate_rule_data'):
            result = automation_service.update_rule(mock_db_session, rule_id, update_data, "test-user-id")

            assert mock_rule.name == "Updated Rule Name"
            assert mock_rule.description == "Updated description"
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once()

    def test_delete_rule(self, mock_db_session: Session):
        """Test deleting an automation rule."""
        automation_service = AutomationService()
        rule_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_rule = Mock(spec=AutomationRule)
        mock_rule.id = rule_id

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_rule

        automation_service.delete_rule(mock_db_session, rule_id, "test-user-id")

        mock_db_session.delete.assert_called_once_with(mock_rule)
        mock_db_session.commit.assert_called_once()

    def test_get_rules_for_project(self, mock_db_session: Session):
        """Test getting all rules for a project."""
        automation_service = AutomationService()
        project_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_rules = [
            Mock(spec=AutomationRule),
            Mock(spec=AutomationRule)
        ]

        mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_rules

        results = automation_service.get_rules(mock_db_session, project_id=project_id)

        assert len(results) == 2
        assert mock_rules[0] in results
        assert mock_rules[1] in results

    def test_validate_rule_data_event_based(self, mock_db_session: Session):
        """Test validating event-based rule data."""
        automation_service = AutomationService()

        rule_data = Mock()
        rule_data.rule_type = "event-based"
        rule_data.conditions = {"event_type": "requirement_created"}
        rule_data.actions = {"notify": "team"}
        rule_data.schedule = None

        # Should not raise
        automation_service._validate_rule_data(rule_data)

    def test_validate_rule_data_missing_event_type(self, mock_db_session: Session):
        """Test validating event-based rule without event_type."""
        automation_service = AutomationService()

        rule_data = Mock()
        rule_data.rule_type = "event-based"
        rule_data.conditions = {}
        rule_data.actions = {"notify": "team"}
        rule_data.schedule = None

        with pytest.raises(BadRequestException):
            automation_service._validate_rule_data(rule_data)
