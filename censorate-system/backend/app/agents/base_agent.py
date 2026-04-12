from abc import ABC, abstractmethod
from typing import Dict, Optional, AsyncGenerator, Any
from app.services.deepagent_service import DeepAgentService
from app.services.lark_service import LarkService


class BaseAgent(ABC):
    """Base abstract agent class."""

    def __init__(
        self,
        deepagent_service: DeepAgentService,
        lark_service: LarkService,
        config: Dict
    ):
        """Initialize agent with services and configuration."""
        self.deepagent = deepagent_service
        self.lark = lark_service
        self.config = config

    @abstractmethod
    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
        """Process a requirement."""
        pass

    @abstractmethod
    def get_agent_type(self) -> str:
        """Return agent type identifier."""
        pass

    async def execute_with_deepagent(
        self,
        input_data: Dict,
        thread_id: Optional[str] = None,
        checkpointer: Optional[Dict] = None
    ) -> Dict:
        """Execute agent through DeepAgent with session persistence."""
        return await self.deepagent.execute_agent(
            agent_type=self.get_agent_type(),
            input_data=input_data,
            requirement_id=input_data["requirement_id"],
            lane=input_data.get("lane", ""),
            thread_id=thread_id,
            checkpointer=checkpointer,
            config=self.config
        )

    async def execute_with_deepagent_stream(
        self,
        input_data: Dict,
        thread_id: Optional[str] = None,
        checkpointer: Optional[Dict] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute agent through DeepAgent with streaming response.

        Yields:
            Stream chunks containing partial results
        """
        async for chunk in self.deepagent.execute_agent_stream(
            agent_type=self.get_agent_type(),
            input_data=input_data,
            requirement_id=input_data["requirement_id"],
            lane=input_data.get("lane", ""),
            thread_id=thread_id,
            checkpointer=checkpointer,
            config=self.config
        ):
            yield chunk

    async def stream_process(
        self,
        requirement_data: Dict,
        context: Dict,
        thread_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a requirement with streaming response.

        Yields:
            Stream chunks containing partial results
        """
        input_data = {
            "requirement_id": requirement_data.get("id"),
            "title": requirement_data.get("title"),
            "description": requirement_data.get("description"),
            "lane": self.get_agent_type().replace("_agent", ""),
            "context": context
        }

        async for chunk in self.execute_with_deepagent_stream(
            input_data,
            thread_id=thread_id
        ):
            yield chunk
