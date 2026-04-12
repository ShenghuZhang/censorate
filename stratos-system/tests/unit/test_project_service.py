"""
Tests for ProjectService.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.project import Project
from app.exceptions import ProjectNotFoundError, ProjectAlreadyExistsError


class TestProjectService:
    """Tests for ProjectService functionality."""

    def test_get_project(self, mock_db_session: Session):
        """Test getting a project."""
        project_service = ProjectService()
        project_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_project = Mock(spec=Project)
        mock_project.id = project_id
        mock_project.name = "Test Project"

        with patch.object(project_service.repository, 'get', return_value=mock_project):
            result = project_service.get_project(mock_db_session, project_id)
            assert result == mock_project

    def test_get_project_not_found(self, mock_db_session: Session):
        """Test getting a project that doesn't exist."""
        project_service = ProjectService()
        project_id = UUID("12345678-1234-5678-1234-567812345678")

        with patch.object(project_service.repository, 'get', return_value=None):
            with pytest.raises(ProjectNotFoundError):
                project_service.get_project(mock_db_session, project_id)

    def test_create_project(self, mock_db_session: Session):
        """Test creating a project."""
        project_service = ProjectService()
        project_data = ProjectCreate(
            name="New Project",
            description="Test project description",
            project_type="non_technical"
        )

        mock_project = Mock(spec=Project)
        mock_project.id = UUID("12345678-1234-5678-1234-567812345679")
        mock_project.name = project_data.name
        mock_project.description = project_data.description

        with patch.object(project_service.repository, 'create', return_value=mock_project):
            mock_db_session.query.return_value.filter.return_value.first.return_value = None

            result = project_service.create_project(mock_db_session, project_data)

            assert result == mock_project
            project_service.repository.create.assert_called_once()

    def test_create_project_already_exists(self, mock_db_session: Session):
        """Test creating a project that already exists."""
        project_service = ProjectService()
        project_data = ProjectCreate(
            name="Existing Project",
            description="Project that already exists",
            project_type="non_technical"
        )

        existing_project = Mock(spec=Project)
        existing_project.name = project_data.name
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing_project

        with pytest.raises(ProjectAlreadyExistsError):
            project_service.create_project(mock_db_session, project_data)

    def test_update_project(self, mock_db_session: Session):
        """Test updating a project."""
        project_service = ProjectService()
        project_id = UUID("12345678-1234-5678-1234-567812345678")
        update_data = ProjectUpdate(
            name="Updated Project Name",
            description="Updated description"
        )

        mock_project = Mock(spec=Project)
        mock_project.id = project_id
        mock_project.name = "Old Project Name"
        mock_project.description = "Old description"

        with patch.object(project_service.repository, 'get', return_value=mock_project):
            with patch.object(project_service.repository, 'update', return_value=mock_project):
                mock_db_session.query.return_value.filter.return_value.first.return_value = None

                result = project_service.update_project(mock_db_session, project_id, update_data)

                assert result == mock_project
                project_service.repository.update.assert_called_once()

    def test_delete_project(self, mock_db_session: Session):
        """Test deleting a project."""
        project_service = ProjectService()
        project_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_project = Mock(spec=Project)
        mock_project.id = project_id

        with patch.object(project_service.repository, 'get', return_value=mock_project):
            with patch.object(project_service.repository, 'delete'):
                project_service.delete_project(mock_db_session, project_id)

                project_service.repository.delete.assert_called_once_with(mock_db_session, project_id)

    def test_get_projects(self, mock_db_session: Session):
        """Test getting all projects."""
        project_service = ProjectService()

        mock_projects = [
            Mock(spec=Project),
            Mock(spec=Project),
            Mock(spec=Project)
        ]

        with patch.object(project_service.repository, 'get_multi', return_value=mock_projects):
            results = project_service.get_projects(mock_db_session, skip=0, limit=10)

            assert len(results) == 3
            project_service.repository.get_multi.assert_called_once()
