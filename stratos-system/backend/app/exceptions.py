"""Stratos Management System exceptions."""

from typing import Optional, Dict


class StratosError(Exception):
    """Base exception class for Stratos system."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        """Initialize exception with message and optional details."""
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(StratosError):
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


class ValidationError(StratosError):
    """Validation error."""
    pass


class ProjectAlreadyExistsError(StratosError):
    """Project already exists error."""
    pass


class TransitionError(StratosError):
    """Invalid state transition error."""
    pass


class AuthorizationError(StratosError):
    """Authorization failed error."""
    pass


class AIServiceError(StratosError):
    """AI service error."""
    pass


class DeepAgentError(StratosError):
    """DeepAgent integration error."""
    pass


class DuplicateError(StratosError):
    """Duplicate resource error."""
    pass


class GitHubIntegrationError(StratosError):
    """GitHub integration error."""
    pass


class LarkIntegrationError(StratosError):
    """Lark integration error."""
    pass
