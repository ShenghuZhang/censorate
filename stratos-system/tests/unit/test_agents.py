"""
Unit Tests for AI Agents system.

This module implements unit tests for the Stratos AI Agents system.
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from app.agents.analysis_agent import AnalysisAgent
from app.agents.design_agent import DesignAgent
from app.agents.development_agent import DevelopmentAgent
from app.agents.testing_agent import TestingAgent
from app.agents import get_agent_class, AGENT_TYPES
from app.services.deepagent_service import DeepAgentService
from app.services.lark_service import LarkService
from app.core.config import Settings


class TestAgentRegistry:
    """Tests for the agent registry functionality."""

    def test_get_agent_class_valid_type(self):
        """Test that valid agent types return the correct class."""
        for agent_type in ["analysis_agent", "design_agent", "development_agent", "testing_agent"]:
            agent_class = get_agent_class(agent_type)
            assert agent_class is not None
            class_name = agent_class.__name__.lower()
            base_type = agent_type.replace("_", "")
            assert base_type in class_name

    def test_get_agent_class_invalid_type(self):
        """Test that invalid agent types raise ValueError."""
        with pytest.raises(ValueError):
            get_agent_class("invalid_agent")

    def test_agent_types_dict_contains_all_agents(self):
        """Test that AGENT_TYPES dictionary contains all required agent types."""
        expected_agents = [
            "analysis_agent",
            "design_agent",
            "development_agent",
            "testing_agent"
        ]
        for agent_type in expected_agents:
            assert agent_type in AGENT_TYPES, f"Agent type '{agent_type}' not in AGENT_TYPES"


class TestAnalysisAgent:
    """Tests for AnalysisAgent functionality."""

    def test_initialization(self):
        """Test AnalysisAgent initialization."""
        mock_settings = Mock(spec=Settings)
        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)
        config = {}

        agent = AnalysisAgent(mock_deepagent, mock_lark, config)
        assert isinstance(agent, AnalysisAgent)
        assert agent.get_agent_type() == "analysis_agent"


class TestDesignAgent:
    """Tests for DesignAgent functionality."""

    def test_initialization(self):
        """Test DesignAgent initialization."""
        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)
        config = {}

        agent = DesignAgent(mock_deepagent, mock_lark, config)
        assert isinstance(agent, DesignAgent)
        assert agent.get_agent_type() == "design_agent"


class TestDevelopmentAgent:
    """Tests for DevelopmentAgent functionality."""

    def test_initialization(self):
        """Test DevelopmentAgent initialization."""
        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)
        config = {}

        agent = DevelopmentAgent(mock_deepagent, mock_lark, config)
        assert isinstance(agent, DevelopmentAgent)
        assert agent.get_agent_type() == "development_agent"


class TestTestingAgent:
    """Tests for TestingAgent functionality."""

    def test_initialization(self):
        """Test TestingAgent initialization."""
        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)
        config = {}

        agent = TestingAgent(mock_deepagent, mock_lark, config)
        assert isinstance(agent, TestingAgent)
        assert agent.get_agent_type() == "testing_agent"


class TestDeepAgentService:
    """Tests for DeepAgentService functionality."""

    def test_initialization(self):
        """Test DeepAgentService initialization."""
        settings = Mock(spec=Settings)
        settings.DEEPAGENT_API_URL = "http://localhost:8001"
        settings.DEEPAGENT_API_KEY = "test_key"

        service = DeepAgentService(settings)
        assert isinstance(service, DeepAgentService)
        assert service.api_url == "http://localhost:8001"


class TestLarkService:
    """Tests for LarkService functionality."""

    def test_initialization(self):
        """Test LarkService initialization."""
        settings = Mock(spec=Settings)
        settings.LARK_APP_ID = "test_app_id"
        settings.LARK_APP_SECRET = "test_app_secret"

        service = LarkService(settings)
        assert isinstance(service, LarkService)
        assert service.app_id == "test_app_id"
        assert service.app_secret == "test_app_secret"
