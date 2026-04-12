"""
Tests for RequirementService.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.requirement_service import RequirementService
from app.schemas.requirement import RequirementCreate, RequirementUpdate, RequirementTransition
from app.models.requirement import Requirement
from app.exceptions import RequirementNotFoundError


class TestRequirementService:
    """Tests for RequirementService functionality."""

    def test_get_requirement(self, mock_db_session: Session):
        """Test getting a requirement by ID."""
        requirement_service = RequirementService(
            deepagent_service=Mock(),
            lark_service=Mock()
        )
        requirement_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_requirement = Mock(spec=Requirement)
        mock_requirement.id = requirement_id

        with patch.object(requirement_service.req_repo, 'get', return_value=mock_requirement):
            result = requirement_service.get_requirement(mock_db_session, requirement_id)
            assert result == mock_requirement
            requirement_service.req_repo.get.assert_called_once_with(mock_db_session, requirement_id)

    def test_get_requirement_not_found(self, mock_db_session: Session):
        """Test getting a requirement that doesn't exist."""
        requirement_service = RequirementService(
            deepagent_service=Mock(),
            lark_service=Mock()
        )
        requirement_id = UUID("12345678-1234-5678-1234-567812345678")

        with patch.object(requirement_service.req_repo, 'get', return_value=None):
            result = requirement_service.get_requirement(mock_db_session, requirement_id)
            assert result is None

    def test_create_requirement(self, mock_db_session: Session):
        """Test creating a requirement."""
        requirement_service = RequirementService(
            deepagent_service=Mock(),
            lark_service=Mock()
        )
        requirement_data = RequirementCreate(
            title="Test Requirement",
            description="Test requirement description",
            priority="high",
            source="manual"
        )

        # Create a dictionary from the Pydantic model
        requirement_data_dict = requirement_data.model_dump()

        mock_requirement = Mock(spec=Requirement)
        mock_requirement.id = UUID("12345678-1234-5678-1234-567812345679")

        with patch.object(requirement_service.req_repo, 'create', return_value=mock_requirement):
            result = requirement_service.create_requirement(mock_db_session, requirement_data_dict)

            assert result == mock_requirement
            requirement_service.req_repo.create.assert_called_once()

    def test_get_all_requirements(self, mock_db_session: Session):
        """Test getting all requirements."""
        requirement_service = RequirementService(
            deepagent_service=Mock(),
            lark_service=Mock()
        )

        mock_requirements = [
            Mock(spec=Requirement),
            Mock(spec=Requirement)
        ]

        with patch.object(requirement_service.req_repo, 'get_all', return_value=mock_requirements):
            results = requirement_service.get_all_requirements(mock_db_session)

            assert results == mock_requirements
            requirement_service.req_repo.get_all.assert_called_once_with(mock_db_session)
