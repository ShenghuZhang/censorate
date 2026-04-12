"""Base Agent class - abstract base class for all Censorate AI Agents.

This module implements the foundational Agent class following Deep Agents best practices.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from ..services.deepagent_service import DeepAgentService
from ..services.lark_service import LarkService


class BaseAgent(ABC):
    """基础 Agent 类 - 所有 Censorate AI Agent 的抽象基类"""

    def __init__(
        self,
        deepagent_service: DeepAgentService,
        lark_service: LarkService,
        config: Dict = None
    ):
        """
        Initialize the agent with required services and configuration.

        Args:
            deepagent_service: Deep Agent integration service
            lark_service: Lark/Feishu integration service
            config: Agent-specific configuration
        """
        self.deepagent = deepagent_service
        self.lark = lark_service
        self.config = config or {}

    @abstractmethod
    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
        """
        处理需求，返回结果

        Args:
            requirement_data: 需求数据
            context: 上下文信息
            thread_id: Deep Agent 线程 ID，用于会话持久化

        Returns:
            处理结果
        """
        pass

    @abstractmethod
    def get_agent_type(self) -> str:
        """返回 Agent 类型标识"""
        pass

    async def execute_with_deepagent(
        self,
        input_data: Dict,
        thread_id: Optional[str] = None,
        checkpointer: Optional[Dict] = None
    ) -> Dict:
        """
        通过 DeepAgent 执行 Agent（使用最佳实践）

        Args:
            input_data: 输入数据
            thread_id: Deep Agent 线程 ID，用于会话持久化
            checkpointer: 检查点，用于中断恢复

        Returns:
            执行结果
        """
        return await self.deepagent.execute_agent(
            agent_type=self.get_agent_type(),
            input_data=input_data,
            requirement_id=input_data.get("requirement_id"),
            lane=input_data.get("lane", self.get_agent_type().replace("_agent", "")),
            thread_id=thread_id,
            checkpointer=checkpointer,
            config=self.config
        )
