import httpx
from typing import Dict, Optional, AsyncGenerator, Any
from app.core.config import Settings


class DeepAgentService:
    """DeepAgent integration service."""

    def __init__(self, settings: Settings):
        """Initialize DeepAgent service."""
        self.api_url = settings.DEEPAGENT_API_URL
        self.api_key = settings.DEEPAGENT_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    async def execute_agent(
        self,
        agent_type: str,
        input_data: Dict,
        requirement_id: str,
        lane: str,
        thread_id: Optional[str] = None,
        config: Optional[Dict] = None,
        checkpointer: Optional[Dict] = None
    ) -> Dict:
        """Execute a DeepAgent with session persistence and checkpointer support."""
        payload = {
            "agent_type": agent_type,
            "input": input_data,
            "thread_id": thread_id,
            "checkpointer": checkpointer,
            "config": config or {}
        }

        response = await self.client.post("/execute", json=payload)
        response.raise_for_status()

        return response.json()

    async def execute_agent_stream(
        self,
        agent_type: str,
        input_data: Dict,
        requirement_id: str,
        lane: str,
        thread_id: Optional[str] = None,
        config: Optional[Dict] = None,
        checkpointer: Optional[Dict] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a DeepAgent with streaming response.

        Yields:
            Stream chunks containing partial results
        """
        payload = {
            "agent_type": agent_type,
            "input": input_data,
            "thread_id": thread_id,
            "checkpointer": checkpointer,
            "config": config or {},
            "stream": True
        }

        async with self.client.stream("POST", "/execute", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        import json
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        yield {"type": "text", "content": line}

    async def get_agent_thread(self, thread_id: str) -> Dict:
        """Get agent thread state for session recovery."""
        response = await self.client.get(f"/threads/{thread_id}")
        response.raise_for_status()
        return response.json()

    async def create_thread(self, thread_id: str, initial_state: Optional[Dict] = None) -> Dict:
        """Create a new agent thread."""
        response = await self.client.post("/threads", json={
            "thread_id": thread_id,
            "initial_state": initial_state
        })
        response.raise_for_status()
        return response.json()

    async def resume_from_checkpoint(self, thread_id: str, checkpoint: Dict) -> Dict:
        """Resume agent execution from checkpoint."""
        response = await self.client.post(f"/threads/{thread_id}/resume", json={
            "checkpoint": checkpoint
        })
        response.raise_for_status()
        return response.json()

    async def cancel_execution(self, thread_id: str) -> Dict:
        """Cancel an ongoing agent execution."""
        response = await self.client.post(f"/threads/{thread_id}/cancel")
        response.raise_for_status()
        return response.json()

    async def get_execution_status(self, thread_id: str) -> Dict:
        """Get the current status of an agent execution."""
        response = await self.client.get(f"/threads/{thread_id}/status")
        response.raise_for_status()
        return response.json()
