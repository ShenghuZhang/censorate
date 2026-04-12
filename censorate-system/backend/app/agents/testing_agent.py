from typing import Dict, Optional
from .base_agent import BaseAgent


class TestingAgent(BaseAgent):
    """Testing and quality assurance agent."""

    def get_agent_type(self) -> str:
        """Return agent type."""
        return "testing_agent"

    async def process(
        self,
        requirement_data: Dict,
        context: Dict,
        thread_id: Optional[str] = None
    ) -> Dict:
        """Generate test cases and run tests."""
        input_data = {
            "requirement_id": requirement_data["id"],
            "title": requirement_data["title"],
            "description": requirement_data.get("description", ""),
            "lane": "testing",
            **context
        }

        result = await self.execute_with_deepagent(
            input_data=input_data,
            thread_id=thread_id
        )

        return {
            "success": True,
            "data": result,
            "message": "Testing complete"
        }
