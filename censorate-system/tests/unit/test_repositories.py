"""
Tests for Repository layer.
"""

import pytest
from unittest.mock import Mock, MagicMock
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.requirement_repository import RequirementRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_member_repository import TeamMemberRepository
from app.models.requirement import Requirement
from app.models.project import Project
from app.models.team_member import TeamMember


class TestRequirementRepository:
    """Tests for RequirementRepository functionality."""

    def test_get(self, mock_db_session: Session):
        """Test getting a requirement by ID."""
        repo = RequirementRepository()
        req_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_req = Mock(spec=Requirement)
        mock_req.id = req_id
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_req

        result = repo.get(mock_db_session, req_id)

        assert result == mock_req

    def test_get_all(self, mock_db_session: Session):
        """Test getting all requirements."""
        repo = RequirementRepository()

        mock_reqs = [Mock(spec=Requirement), Mock(spec=Requirement)]
        mock_db_session.query.return_value.all.return_value = mock_reqs

        results = repo.get_all(mock_db_session)

        assert len(results) == 2
        assert results == mock_reqs

    def test_create(self, mock_db_session: Session):
        """Test creating a requirement."""
        repo = RequirementRepository()

        mock_req = Mock(spec=Requirement)
        mock_req.id = UUID("12345678-1234-5678-1234-567812345678")

        result = repo.create(mock_db_session, mock_req)

        mock_db_session.add.assert_called_once_with(mock_req)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_req)
        assert result == mock_req

    def test_get_by_project(self, mock_db_session: Session):
        """Test getting requirements by project."""
        repo = RequirementRepository()
        project_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_reqs = [Mock(spec=Requirement), Mock(spec=Requirement)]
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_reqs

        results = repo.get_by_project(mock_db_session, project_id)

        assert len(results) == 2

    def test_get_by_status(self, mock_db_session: Session):
        """Test getting requirements by status."""
        repo = RequirementRepository()
        project_id = UUID("12345678-1234-5678-1234-567812345678")
        status = "analysis"

        mock_reqs = [Mock(spec=Requirement)]

        # Create a realistic mock query chain
        mock_query1 = Mock()
        mock_query2 = Mock()
        mock_query2.all.return_value = mock_reqs
        mock_query1.filter.return_value = mock_query2
        mock_db_session.query.return_value = mock_query1

        results = repo.get_by_status(mock_db_session, project_id, status)

        assert len(results) == 1


class TestProjectRepository:
    """Tests for ProjectRepository functionality."""

    def test_get(self, mock_db_session: Session):
        """Test getting a project by ID."""
        repo = ProjectRepository()
        project_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_project = Mock(spec=Project)
        mock_project.id = project_id
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_project

        result = repo.get(mock_db_session, project_id)

        assert result == mock_project

    def test_get_all(self, mock_db_session: Session):
        """Test getting all projects."""
        repo = ProjectRepository()

        mock_projects = [Mock(spec=Project), Mock(spec=Project)]
        mock_db_session.query.return_value.all.return_value = mock_projects

        results = repo.get_all(mock_db_session)

        assert len(results) == 2
        assert results == mock_projects

    def test_get_by_slug(self, mock_db_session: Session):
        """Test getting a project by slug."""
        repo = ProjectRepository()
        slug = "test-project"

        mock_project = Mock(spec=Project)
        mock_project.slug = slug
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_project

        result = repo.get_by_slug(mock_db_session, slug)

        assert result == mock_project

    def test_search(self, mock_db_session: Session):
        """Test searching projects."""
        repo = ProjectRepository()
        query = "test"

        mock_projects = [Mock(spec=Project), Mock(spec=Project)]
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_projects

        results = repo.search(mock_db_session, query)

        assert len(results) == 2


class TestTeamMemberRepository:
    """Tests for TeamMemberRepository functionality."""

    def test_get(self, mock_db_session: Session):
        """Test getting a team member by ID."""
        repo = TeamMemberRepository()
        member_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_member = Mock(spec=TeamMember)
        mock_member.id = member_id
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_member

        result = repo.get(mock_db_session, member_id)

        assert result == mock_member

    def test_get_all(self, mock_db_session: Session):
        """Test getting all team members."""
        repo = TeamMemberRepository()

        mock_members = [Mock(spec=TeamMember), Mock(spec=TeamMember)]
        mock_db_session.query.return_value.all.return_value = mock_members

        results = repo.get_all(mock_db_session)

        assert len(results) == 2
        assert results == mock_members

    def test_get_by_project(self, mock_db_session: Session):
        """Test getting team members by project."""
        repo = TeamMemberRepository()
        project_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_members = [Mock(spec=TeamMember), Mock(spec=TeamMember)]
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_members

        results = repo.get_by_project(mock_db_session, project_id)

        assert len(results) == 2

    def test_get_ai_agents(self, mock_db_session: Session):
        """Test getting AI agents."""
        repo = TeamMemberRepository()
        project_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_agents = [Mock(spec=TeamMember), Mock(spec=TeamMember)]
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_agents

        results = repo.get_ai_agents(mock_db_session, project_id)

        assert len(results) == 2

    def test_get_human_members(self, mock_db_session: Session):
        """Test getting human members."""
        repo = TeamMemberRepository()
        project_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_members = [Mock(spec=TeamMember), Mock(spec=TeamMember)]
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_members

        results = repo.get_human_members(mock_db_session, project_id)

        assert len(results) == 2


class TestAgentExecutionRepository:
    """Tests for AgentExecutionRepository functionality."""

    def test_get(self, mock_db_session: Session):
        """Test getting an agent execution by ID."""
        from app.repositories.agent_execution_repository import AgentExecutionRepository
        from app.models.agent_execution import AgentExecution

        repo = AgentExecutionRepository()
        exec_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_exec = Mock(spec=AgentExecution)
        mock_exec.id = exec_id
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_exec

        result = repo.get(mock_db_session, exec_id)

        assert result == mock_exec

    def test_get_by_requirement(self, mock_db_session: Session):
        """Test getting agent executions by requirement."""
        from app.repositories.agent_execution_repository import AgentExecutionRepository
        from app.models.agent_execution import AgentExecution

        repo = AgentExecutionRepository()
        requirement_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_execs = [Mock(spec=AgentExecution), Mock(spec=AgentExecution)]
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_execs

        results = repo.get_by_requirement(mock_db_session, requirement_id)

        assert len(results) == 2

    def test_get_current_execution(self, mock_db_session: Session):
        """Test getting current running execution."""
        from app.repositories.agent_execution_repository import AgentExecutionRepository
        from app.models.agent_execution import AgentExecution

        repo = AgentExecutionRepository()
        requirement_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_exec = Mock(spec=AgentExecution)
        mock_exec.status = "running"
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_exec

        result = repo.get_current_execution(mock_db_session, requirement_id)

        assert result == mock_exec


class TestLaneRoleRepository:
    """Tests for LaneRoleRepository functionality."""

    def test_get(self, mock_db_session: Session):
        """Test getting a lane role by ID."""
        from app.repositories.lane_role_repository import LaneRoleRepository
        from app.models.lane_role import LaneRole

        repo = LaneRoleRepository()
        role_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_role = Mock(spec=LaneRole)
        mock_role.id = role_id
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_role

        result = repo.get(mock_db_session, role_id)

        assert result == mock_role

    def test_get_by_project(self, mock_db_session: Session):
        """Test getting lane roles by project."""
        from app.repositories.lane_role_repository import LaneRoleRepository
        from app.models.lane_role import LaneRole

        repo = LaneRoleRepository()
        project_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_roles = [Mock(spec=LaneRole), Mock(spec=LaneRole)]
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_roles

        results = repo.get_by_project(mock_db_session, project_id)

        assert len(results) == 2

    def test_get_by_lane(self, mock_db_session: Session):
        """Test getting lane role by project and lane."""
        from app.repositories.lane_role_repository import LaneRoleRepository
        from app.models.lane_role import LaneRole

        repo = LaneRoleRepository()
        project_id = UUID("12345678-1234-5678-1234-567812345678")
        lane = "analysis"

        mock_role = Mock(spec=LaneRole)
        mock_role.lane = lane
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_role

        result = repo.get_by_lane(mock_db_session, project_id, lane)

        assert result == mock_role
