"""Agent that converts raw user requirements into a structured PRD."""
from typing import Optional
from app.services.claude_service import ClaudeService
from app.schemas.prd import PRDOutput

PRD_SYSTEM_PROMPT = """You are a senior product analyst. Your job is to take a user's rough idea
and produce a structured Product Requirements Document (PRD).

Analyze the request thoroughly and produce:
1. A clear project name and description
2. Prioritized features (P0 = must have, P1 = nice to have, P2 = future)
3. User stories that capture the core workflows
4. Data models needed (entities and their relationships)
5. API endpoints the backend needs to expose
6. Frontend routes/pages needed
7. Tech stack decisions and rationale

Be specific and practical. Focus on what's needed for a working MVP."""


class RequirementAnalysisAgent:
    """Takes user story + template info, produces structured PRD."""

    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service

    def analyze(self, user_story: str, template_description: str = "") -> PRDOutput:
        """Analyze user requirements and generate structured PRD."""
        user_prompt = (
            f"Template context: {template_description}\n\n"
            f"User requirements:\n{user_story}"
        )
        return self.claude.generate_structured(
            system_prompt=PRD_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=PRDOutput,
        )

    async def analyze_async(self, user_story: str, template_description: str = "") -> PRDOutput:
        """Async version of analyze."""
        return await self.claude.generate_structured_async(
            system_prompt=PRD_SYSTEM_PROMPT,
            user_prompt=(
                f"Template context: {template_description}\n\n"
                f"User requirements:\n{user_story}"
            ),
            output_model=PRDOutput,
        )
