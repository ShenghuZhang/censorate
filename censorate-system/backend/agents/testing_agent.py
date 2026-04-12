"""Testing Agent - 测试 Agent

This module implements the TestingAgent for test case generation, test execution,
and coverage analysis using Deep Agents.
"""

from typing import Dict, Optional
from .base_agent import BaseAgent


class TestingAgent(BaseAgent):
    """测试 Agent - 负责生成测试用例、执行测试和分析覆盖率"""

    def get_agent_type(self) -> str:
        return "testing_agent"

    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
        """
        处理测试生成和执行任务

        Args:
            requirement_data: 需求数据
            context: 上下文信息（包含开发阶段的结果）
            thread_id: Deep Agent 线程 ID

        Returns:
            测试结果，包含测试用例、覆盖率报告、执行结果等
        """
        input_data = {
            "requirement_id": requirement_data.get("id"),
            "title": requirement_data.get("title"),
            "description": requirement_data.get("description"),
            "lane": "testing",
            "development_result": context.get("development_result"),
            "context": context
        }

        result = await self.execute_with_deepagent(input_data, thread_id=thread_id)

        return {
            "success": True,
            "agent_type": self.get_agent_type(),
            "result": result,
            "thread_id": thread_id
        }
