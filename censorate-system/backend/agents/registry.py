"""Agent Registry - 动态 Agent 查找和注册

This module implements the agent registry for dynamic agent lookup and instantiation.
"""

from typing import Dict, Type, Optional
from .base_agent import BaseAgent
from .analysis_agent import AnalysisAgent
from .design_agent import DesignAgent
from .development_agent import DevelopmentAgent
from .testing_agent import TestingAgent
from app.core.exceptions import BadRequestException


_AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {
    "analysis_agent": AnalysisAgent,
    "design_agent": DesignAgent,
    "development_agent": DevelopmentAgent,
    "testing_agent": TestingAgent,
}


_LANE_AGENT_MAP: Dict[str, str] = {
    "analysis": "analysis_agent",
    "design": "design_agent",
    "development": "development_agent",
    "testing": "testing_agent",
}


def get_agent_class(agent_type: str) -> Optional[Type[BaseAgent]]:
    """
    根据 Agent 类型获取对应的类

    Args:
        agent_type: Agent 类型标识

    Returns:
        Agent 类，如果未找到则返回 None
    """
    return _AGENT_REGISTRY.get(agent_type)


def get_agent_for_lane(lane: str) -> Optional[Type[BaseAgent]]:
    """
    根据泳道名称获取对应的 Agent 类

    Args:
        lane: 泳道名称

    Returns:
        Agent 类，如果未找到则返回 None
    """
    agent_type = _LANE_AGENT_MAP.get(lane)
    return get_agent_class(agent_type) if agent_type else None


def register_agent(agent_type: str, agent_class: Type[BaseAgent]) -> None:
    """
    注册自定义 Agent

    Args:
        agent_type: Agent 类型标识
        agent_class: Agent 类（继承自 BaseAgent）
    """
    _AGENT_REGISTRY[agent_type] = agent_class


def register_lane_agent(lane: str, agent_type: str) -> None:
    """
    注册泳道与 Agent 的映射关系

    Args:
        lane: 泳道名称
        agent_type: Agent 类型标识
    """
    if agent_type not in _AGENT_REGISTRY:
        raise BadRequestException(f"Agent type '{agent_type}' not registered")
    _LANE_AGENT_MAP[lane] = agent_type


def list_registered_agents() -> Dict[str, Type[BaseAgent]]:
    """
    获取所有已注册的 Agent

    Returns:
        字典，键为 Agent 类型，值为 Agent 类
    """
    return _AGENT_REGISTRY.copy()


def list_lane_agent_mappings() -> Dict[str, str]:
    """
    获取所有泳道与 Agent 的映射关系

    Returns:
        字典，键为泳道名称，值为 Agent 类型
    """
    return _LANE_AGENT_MAP.copy()
