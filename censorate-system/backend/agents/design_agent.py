"""Design Agent - 方案设计 Agent

This module implements the DesignAgent for design generation, architecture recommendations,
and UI wireframe creation using Deep Agents.
"""

from typing import Dict, Optional
from .base_agent import BaseAgent


class DesignAgent(BaseAgent):
    """方案设计 Agent - 负责生成设计文档、架构方案和 UI 线框图"""

    def get_agent_type(self) -> str:
        return "design_agent"

    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
        """
        处理设计生成任务

        Args:
            requirement_data: 需求数据
            context: 上下文信息（包含分析阶段的结果）
            thread_id: Deep Agent 线程 ID

        Returns:
            设计结果，包含架构建议、数据模型、API 设计、UI 线框图等
        """
        input_data = {
            "requirement_id": requirement_data.get("id"),
            "title": requirement_data.get("title"),
            "description": requirement_data.get("description"),
            "lane": "design",
            "analysis_result": context.get("analysis_result"),
            "context": context
        }

        result = await self.execute_with_deepagent(input_data, thread_id=thread_id)

        return {
            "success": True,
            "agent_type": self.get_agent_type(),
            "result": result,
            "thread_id": thread_id
        }
