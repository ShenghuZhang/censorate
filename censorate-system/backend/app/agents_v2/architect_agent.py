"""Agent that designs system architecture from a PRD."""
from app.services.claude_service import ClaudeService
from app.schemas.prd import PRDOutput
from app.schemas.architecture import ArchitectureOutput

ARCHITECT_SYSTEM_PROMPT = """You are a senior software architect. Your job is to design
a complete project architecture from a PRD.

Given the PRD and template conventions, produce:
1. A complete file tree (every file that needs to be created)
2. Backend dependencies with versions
3. Frontend dependencies with versions
4. Environment variables needed
5. Database models/entities
6. Docker configuration (if applicable)

For a FastAPI + Next.js monorepo:
- Backend goes in backend/ directory
- Frontend goes in frontend/ directory
- Root files in project root

Be specific about file paths. Each FileSpec should have a clear path and content_description
that tells the code generator exactly what to build."""


class ArchitectAgent:
    """Produces complete architecture design from PRD."""

    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service

    def design(self, prd: PRDOutput, template_config: dict) -> ArchitectureOutput:
        """Design architecture from PRD and template config."""
        user_prompt = (
            f"PRD:\n{prd.model_dump_json(indent=2)}\n\n"
            f"Template config:\n{template_config}"
        )
        return self.claude.generate_structured(
            system_prompt=ARCHITECT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=ArchitectureOutput,
        )

    async def design_async(self, prd: PRDOutput, template_config: dict) -> ArchitectureOutput:
        """Async version of design."""
        return await self.claude.generate_structured_async(
            system_prompt=ARCHITECT_SYSTEM_PROMPT,
            user_prompt=f"PRD:\n{prd.model_dump_json(indent=2)}\n\nTemplate config:\n{template_config}",
            output_model=ArchitectureOutput,
        )
