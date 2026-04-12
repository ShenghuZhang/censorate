# Agents module
from .base_agent import BaseAgent
from .analysis_agent import AnalysisAgent
from .design_agent import DesignAgent
from .development_agent import DevelopmentAgent
from .testing_agent import TestingAgent
from app.core.exceptions import BadRequestException

AGENT_TYPES = {
    "analysis_agent": AnalysisAgent,
    "design_agent": DesignAgent,
    "development_agent": DevelopmentAgent,
    "testing_agent": TestingAgent
}


def get_agent_class(agent_type: str):
    """Get agent class by type."""
    agent_class = AGENT_TYPES.get(agent_type)
    if not agent_class:
        raise BadRequestException(f"Unknown agent type: {agent_type}")
    return agent_class
