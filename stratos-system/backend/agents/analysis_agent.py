"""Analysis Agent - 需求分析 Agent

This module implements the AnalysisAgent for requirement analysis, duplicate detection,
and triage using Deep Agents.
"""

from typing import Dict, Optional
from .base_agent import BaseAgent


class AnalysisAgent(BaseAgent):
    """需求分析 Agent - 负责需求分析、重复检测和分类"""

    def get_agent_type(self) -> str:
        return "analysis_agent"

    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
        """
        处理需求分析任务

        Args:
            requirement_data: 需求数据
            context: 上下文信息
            thread_id: Deep Agent 线程 ID

        Returns:
            分析结果，包含优先级、复杂度、时间估计、风险评估等
        """
        # 构建输入数据
        input_data = {
            "requirement_id": requirement_data.get("id"),
            "title": requirement_data.get("title"),
            "description": requirement_data.get("description"),
            "lane": "analysis",
            "context": context
        }

        # 使用 Deep Agent 执行分析
        result = await self.execute_with_deepagent(input_data, thread_id=thread_id)

        return {
            "success": True,
            "agent_type": self.get_agent_type(),
            "result": result,
            "thread_id": thread_id
        }
