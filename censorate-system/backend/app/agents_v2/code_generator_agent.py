"""Agent that generates actual code files from architecture design."""
from typing import List, Optional
from app.services.claude_service import ClaudeService
from app.schemas.architecture import ArchitectureOutput, FileSpec
from app.schemas.prd import PRDOutput

CODE_GEN_SYSTEM_PROMPT = """You are an expert software engineer. Your job is to generate
complete, production-ready code files for a project.

Given the architecture spec, PRD, and context of already-generated files,
produce a single file with correct, working code.

Rules:
1. Generate COMPLETE code - no placeholders, no "TODO" comments
2. Follow the conventions of the target language/framework
3. Ensure imports match actual file paths in the project
4. Code must be syntactically valid
5. Include proper error handling
6. Use environment variables for configuration
7. Follow RESTful conventions for APIs
8. Generate proper type hints and docstrings

Output only the file content, no explanations."""


class CodeGeneratorAgent:
    """Generates code files based on architecture design."""

    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service

    def generate_file(
        self,
        file_spec: FileSpec,
        architecture: ArchitectureOutput,
        prd: PRDOutput,
        existing_files_context: str = "",
    ) -> str:
        """Generate a single code file."""
        user_prompt = (
            f"File to generate: {file_spec.path}\n"
            f"Language: {file_spec.language}\n"
            f"Is config: {file_spec.is_config}\n"
            f"Content description: {file_spec.content_description}\n\n"
            f"Project: {architecture.project_name}\n"
            f"Full file tree:\n"
            + "\n".join(f"  {f.path}" for f in architecture.file_tree) + "\n\n"
            f"Backend deps: {architecture.backend_dependencies}\n"
            f"Frontend deps: {architecture.frontend_dependencies}\n"
            f"PRD features:\n"
            + "\n".join(f"  - {f.name}: {f.description}" for f in prd.features) + "\n\n"
            f"Already generated files context:\n{existing_files_context}\n\n"
            f"Generate the complete file content:"
        )
        return self.claude.generate_text(
            system_prompt=CODE_GEN_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

    async def generate_file_async(
        self,
        file_spec: FileSpec,
        architecture: ArchitectureOutput,
        prd: PRDOutput,
        existing_files_context: str = "",
    ) -> str:
        """Async version of generate_file."""
        return await self.claude.generate_text_async(
            system_prompt=CODE_GEN_SYSTEM_PROMPT,
            user_prompt=(
                f"File to generate: {file_spec.path}\n"
                f"Language: {file_spec.language}\n"
                f"Is config: {file_spec.is_config}\n"
                f"Content description: {file_spec.content_description}\n\n"
                f"Project: {architecture.project_name}\n"
                f"Full file tree:\n"
                + "\n".join(f"  {f.path}" for f in architecture.file_tree) + "\n\n"
                f"Backend deps: {architecture.backend_dependencies}\n"
                f"Frontend deps: {architecture.frontend_dependencies}\n"
                f"PRD features:\n"
                + "\n".join(f"  - {f.name}: {f.description}" for f in prd.features) + "\n\n"
                f"Already generated files context:\n{existing_files_context}\n\n"
                f"Generate the complete file content:"
            ),
        )
