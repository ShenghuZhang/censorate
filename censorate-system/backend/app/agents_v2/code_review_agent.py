"""Agent that reviews generated code for issues and fixes them."""
from typing import List
from app.services.claude_service import ClaudeService
from app.schemas.review import FileReview, ReviewIssue

REVIEW_SYSTEM_PROMPT = """You are a senior code reviewer. Review the given code for:
1. Syntax errors and missing imports
2. Type mismatches
3. API contract violations
4. Missing error handling
5. Security issues (hardcoded secrets, injection vulnerabilities)
6. Best practices violations

For each issue, specify severity (error/warning/suggestion), the line number,
and a suggested fix. Be precise and actionable."""

FIX_SYSTEM_PROMPT = """You are an expert software engineer. Fix the issues identified
in the code review. Return ONLY the corrected file content, no explanations.
Preserve the overall structure and logic - only fix the specific issues mentioned."""


class CodeReviewAgent:
    """Reviews generated code and fixes issues."""

    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service

    def review_file(self, file_path: str, content: str, project_context: str = "") -> FileReview:
        """Review a single file and return issues found."""
        user_prompt = (
            f"File: {file_path}\n"
            f"Project context: {project_context}\n\n"
            f"Code to review:\n```\n{content}\n```"
        )
        result = self.claude.generate_structured(
            system_prompt=REVIEW_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=FileReview,
        )
        result.file_path = file_path
        return result

    def fix_file(self, content: str, review: FileReview) -> str:
        """Fix issues found in a file."""
        issues_text = "\n".join(
            f"[{i.severity}] Line {i.line_number or '?'}: {i.message}"
            for i in review.issues
        )
        user_prompt = (
            f"Original code:\n```\n{content}\n```\n\n"
            f"Issues to fix:\n{issues_text}\n\n"
            f"Return ONLY the corrected code:"
        )
        return self.claude.generate_text(
            system_prompt=FIX_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

    async def review_file_async(self, file_path: str, content: str, project_context: str = "") -> FileReview:
        """Async version of review_file."""
        return await self.claude.generate_structured_async(
            system_prompt=REVIEW_SYSTEM_PROMPT,
            user_prompt=(
                f"File: {file_path}\n"
                f"Project context: {project_context}\n\n"
                f"Code to review:\n```\n{content}\n```"
            ),
            output_model=FileReview,
        )

    async def fix_file_async(self, content: str, review: FileReview) -> str:
        """Async version of fix_file."""
        issues_text = "\n".join(
            f"[{i.severity}] Line {i.line_number or '?'}: {i.message}"
            for i in review.issues
        )
        return await self.claude.generate_text_async(
            system_prompt=FIX_SYSTEM_PROMPT,
            user_prompt=(
                f"Original code:\n```\n{content}\n```\n\n"
                f"Issues to fix:\n{issues_text}\n\n"
                f"Return ONLY the corrected code:"
            ),
        )
