"""Test agent streaming functionality and unit tests."""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any


class TestAnalysisAgent:
    """Tests for AnalysisAgent functionality."""

    def test_initialization(self):
        """Test AnalysisAgent initialization."""
        from app.agents.analysis_agent import AnalysisAgent
        from app.services.deepagent_service import DeepAgentService
        from app.services.lark_service import LarkService

        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)

        agent = AnalysisAgent(mock_deepagent, mock_lark, {})
        assert isinstance(agent, AnalysisAgent)
        assert agent.get_agent_type() == "analysis_agent"

    def test_get_agent_type(self):
        """Test AnalysisAgent get_agent_type method."""
        from app.agents.analysis_agent import AnalysisAgent
        from app.services.deepagent_service import DeepAgentService
        from app.services.lark_service import LarkService

        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)

        agent = AnalysisAgent(mock_deepagent, mock_lark, {})
        assert agent.get_agent_type() == "analysis_agent"


class TestDesignAgent:
    """Tests for DesignAgent functionality."""

    def test_initialization(self):
        """Test DesignAgent initialization."""
        from app.agents.design_agent import DesignAgent
        from app.services.deepagent_service import DeepAgentService
        from app.services.lark_service import LarkService

        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)

        agent = DesignAgent(mock_deepagent, mock_lark, {})
        assert isinstance(agent, DesignAgent)
        assert agent.get_agent_type() == "design_agent"


class TestDevelopmentAgent:
    """Tests for DevelopmentAgent functionality."""

    def test_initialization(self):
        """Test DevelopmentAgent initialization."""
        from app.agents.development_agent import DevelopmentAgent
        from app.services.deepagent_service import DeepAgentService
        from app.services.lark_service import LarkService

        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)

        agent = DevelopmentAgent(mock_deepagent, mock_lark, {})
        assert isinstance(agent, DevelopmentAgent)
        assert agent.get_agent_type() == "development_agent"


class TestTestingAgent:
    """Tests for TestingAgent functionality."""

    def test_initialization(self):
        """Test TestingAgent initialization."""
        from app.agents.testing_agent import TestingAgent
        from app.services.deepagent_service import DeepAgentService
        from app.services.lark_service import LarkService

        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)

        agent = TestingAgent(mock_deepagent, mock_lark, {})
        assert isinstance(agent, TestingAgent)
        assert agent.get_agent_type() == "testing_agent"


class TestDeepAgentService:
    """Tests for DeepAgentService functionality."""

    def test_initialization(self):
        """Test DeepAgentService initialization."""
        from app.services.deepagent_service import DeepAgentService
        from app.core.config import Settings

        settings = Mock(spec=Settings)
        settings.DEEPAGENT_API_URL = "http://localhost:8001"
        settings.DEEPAGENT_API_KEY = "test_key"

        service = DeepAgentService(settings)
        assert isinstance(service, DeepAgentService)
        assert service.api_url == "http://localhost:8001"


class TestStreamSupport:
    """Tests for streaming support in agents."""

    def test_base_agent_has_stream_process(self):
        """Test that BaseAgent has stream_process method."""
        from app.agents.base_agent import BaseAgent
        assert hasattr(BaseAgent, "stream_process")

    def test_deepagent_service_has_execute_agent_stream(self):
        """Test that DeepAgentService has execute_agent_stream method."""
        from app.services.deepagent_service import DeepAgentService
        assert hasattr(DeepAgentService, "execute_agent_stream")

    def test_deepagent_service_has_cancel_execution(self):
        """Test that DeepAgentService has cancel_execution method."""
        from app.services.deepagent_service import DeepAgentService
        assert hasattr(DeepAgentService, "cancel_execution")

    def test_deepagent_service_has_get_execution_status(self):
        """Test that DeepAgentService has get_execution_status method."""
        from app.services.deepagent_service import DeepAgentService
        assert hasattr(DeepAgentService, "get_execution_status")


def test_deepagent_configuration_exists():
    """Test that deepagent configuration is properly set up."""
    from app.core.config import Settings

    settings = Settings()
    assert hasattr(settings, "DEEPAGENT_API_URL")
    assert hasattr(settings, "DEEPAGENT_API_KEY")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
