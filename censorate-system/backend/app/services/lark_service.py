import httpx
from typing import Dict, Optional, List
from datetime import datetime
from app.core.config import Settings
from app.core.exceptions import LarkIntegrationException


class LarkService:
    """Lark (Feishu) integration service."""

    def __init__(self, settings: Settings):
        """Initialize Lark service."""
        self.app_id = settings.LARK_APP_ID
        self.app_secret = settings.LARK_APP_SECRET
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token: Optional[str] = None
        self.client = httpx.AsyncClient()

    async def get_access_token(self) -> str:
        """Get Lark access token."""
        if self.access_token:
            return self.access_token

        response = await self.client.post(
            f"{self.base_url}/auth/v3/tenant_access_token/internal",
            json={
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
        )

        result = response.json()
        if result.get("code") != 0:
            raise LarkIntegrationException(f"Failed to get access token: {result}")

        self.access_token = result["tenant_access_token"]
        return self.access_token

    async def create_document(
        self,
        title: str,
        content: str
    ) -> Dict:
        """Create a Lark document."""
        token = await self.get_access_token()

        response = await self.client.post(
            f"{self.base_url}/docx/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": title}
        )

        result = response.json()
        if result.get("code") != 0:
            raise LarkIntegrationException(f"Failed to create document: {result}")

        doc_token = result["data"]["document"]["document_id"]

        await self.append_to_document(doc_token, content)

        return {
            "token": doc_token,
            "url": f"https://feishu.cn/docx/{doc_token}"
        }

    async def append_to_document(
        self,
        doc_token: str,
        content: str,
        position: str = "END"
    ):
        """Append content to a Lark document."""
        token = await self.get_access_token()

        blocks = self._markdown_to_blocks(content)

        response = await self.client.post(
            f"{self.base_url}/docx/v1/documents/{doc_token}/blocks/{position}/children",
            headers={"Authorization": f"Bearer {token}"},
            json={"children": blocks, "index": -1}
        )

        result = response.json()
        if result.get("code") != 0:
            raise LarkIntegrationException(f"Failed to append to document: {result}")

    async def get_document_permission(
        self,
        doc_token: str,
        user_id: str
    ) -> bool:
        """Check if user has document edit permission."""
        token = await self.get_access_token()

        response = await self.client.get(
            f"{self.base_url}/docx/v1/documents/{doc_token}/permission",
            headers={"Authorization": f"Bearer {token}"},
            params={"user_id": user_id}
        )

        result = response.json()
        if result.get("code") != 0:
            return False

        permissions = result.get("data", {}).get("permissions", [])
        return any(p.get("type") == "edit" for p in permissions)

    def _markdown_to_blocks(self, markdown: str) -> List[Dict]:
        """Convert Markdown to Lark document blocks."""
        lines = markdown.split('\n')
        blocks = []

        for line in lines:
            if line.startswith('# '):
                blocks.append({
                    "type": "heading1",
                    "heading1": {"elements": [{"text": {"content": line[2:]}}]}
                })
            elif line.startswith('## '):
                blocks.append({
                    "type": "heading2",
                    "heading2": {"elements": [{"text": {"content": line[3:]}}]}
                })
            elif line.strip():
                blocks.append({
                    "type": "text",
                    "text": {"elements": [{"text": {"content": line}}]}
                })

        return blocks

    async def handle_webhook(self, payload: Dict) -> Dict:
        """Handle Lark webhook."""
        event_type = payload.get("type")
        event_data = payload.get("event", {})

        if event_type == "approval_instance":
            return await self._handle_approval(event_data)
        elif event_type == "message":
            return await self._handle_message(event_data)

        return {"status": "ignored"}

    async def _handle_approval(self, event_data: Dict) -> Dict:
        """Handle approval events."""
        approval_code = event_data.get("approval_code")
        instance_id = event_data.get("instance")

        return {"status": "processed", "action": "transition_requirement"}

    async def _handle_message(self, event_data: Dict) -> Dict:
        """Handle message events."""
        return {"status": "processed"}
