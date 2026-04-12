"""Development Agent - 开发 Agent

This module implements the DevelopmentAgent for code generation, implementation guidance,
and development best practices using Deep Agents.
"""

from typing import Dict, Optional
from .base_agent import BaseAgent


class DevelopmentAgent(BaseAgent):
    """开发 Agent - 负责生成实现代码、单元测试和文档"""

    def get_agent_type(self) -> str:
        return "development_agent"

    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
        """
        处理代码生成任务

        Args:
            requirement_data: 需求数据
            context: 上下文信息（包含设计阶段的结果）
            thread_id: Deep Agent 线程 ID

        Returns:
            开发结果，包含实现代码、测试文件、文档等
        """
        input_data = {
            "requirement_id": requirement_data.get("id"),
            "title": requirement_data.get("title"),
            "description": requirement_data.get("description"),
            "lane": "development",
            "design_result": context.get("design_result"),
            "context": context
        }

        result = await self.execute_with_deepagent(input_data, thread_id=thread_id)

        return {
            "success": True,
            "agent_type": self.get_agent_type(),
            "result": result,
            "thread_id": thread_id
        }
