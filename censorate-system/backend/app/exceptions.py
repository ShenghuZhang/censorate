"""Censorate Management System exceptions."""

from typing import Optional, Dict


class CensorateError(Exception):
    """Base exception class for Censorate system."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        """Initialize exception with message and optional details."""
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(CensorateError):
    """Resource not found error."""
    pass


class ProjectNotFoundError(NotFoundError):
    """Project not found error."""
    pass


class RequirementNotFoundError(NotFoundError):
    """Requirement not found error."""
    pass


class TaskNotFoundError(NotFoundError):
    """Task not found error."""
    pass


class TestCaseNotFoundError(NotFoundError):
    """Test case not found error."""
    pass


class AgentNotFoundError(NotFoundError):
    """Agent not found error."""
    pass


class ValidationError(CensorateError):
    """Validation error."""
    pass


class ProjectAlreadyExistsError(CensorateError):
    """Project already exists error."""
    pass


class TransitionError(CensorateError):
    """Invalid state transition error."""
    pass


class AuthorizationError(CensorateError):
    """Authorization failed error."""
    pass


class AIServiceError(CensorateError):
    """AI service error."""
    pass


class DeepAgentError(CensorateError):
    """DeepAgent integration error."""
    pass


class DuplicateError(CensorateError):
    """Duplicate resource error."""
    pass


class GitHubIntegrationError(CensorateError):
    """GitHub integration error."""
    pass


class LarkIntegrationError(CensorateError):
    """Lark integration error."""
    pass
