"""
Custom exceptions and error handling for Stratos API.
"""

from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse


class StratosException(Exception):
    """Base exception class for all Stratos exceptions."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"
    error_code: str = "INTERNAL_ERROR"
    extra: Optional[Dict[str, Any]] = None

    def __init__(
        self,
        detail: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        if detail:
            self.detail = detail
        self.extra = extra
        super().__init__(self.detail)


class NotFoundException(StratosException):
    """Exception raised when a resource is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"
    error_code = "NOT_FOUND"


class ValidationException(StratosException):
    """Exception raised when input validation fails."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation error"
    error_code = "VALIDATION_ERROR"


class ConflictException(StratosException):
    """Exception raised when there's a conflict with the current state."""
    status_code = status.HTTP_409_CONFLICT
    detail = "Resource conflict"
    error_code = "CONFLICT"


class ForbiddenException(StratosException):
    """Exception raised when access is forbidden."""
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Access forbidden"
    error_code = "FORBIDDEN"


class UnauthorizedException(StratosException):
    """Exception raised when authentication is required."""
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Unauthorized"
    error_code = "UNAUTHORIZED"


class BadRequestException(StratosException):
    """Exception raised for invalid requests."""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request"
    error_code = "BAD_REQUEST"


class StateTransitionException(StratosException):
    """Exception raised when an invalid state transition is attempted."""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid state transition"
    error_code = "INVALID_TRANSITION"


class AgentExecutionException(StratosException):
    """Exception raised when agent execution fails."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Agent execution failed"
    error_code = "AGENT_ERROR"


class LarkIntegrationException(StratosException):
    """Exception raised when Lark integration fails."""
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "Lark integration error"
    error_code = "LARK_ERROR"


def create_error_response(
    exception: StratosException,
    request: Optional[Request] = None
) -> Dict[str, Any]:
    """Create a standardized error response."""
    response: Dict[str, Any] = {
        "error": {
            "code": exception.error_code,
            "message": exception.detail,
            "status": exception.status_code
        }
    }

    if exception.extra:
        response["error"]["details"] = exception.extra

    if request:
        response["error"]["path"] = str(request.url.path)

    return response


async def stratos_exception_handler(request: Request, exc: StratosException) -> JSONResponse:
    """Global exception handler for Stratos exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc, request)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback exception handler for unexpected errors."""
    error = StratosException(
        detail="An unexpected error occurred"
    )
    return JSONResponse(
        status_code=error.status_code,
        content=create_error_response(error, request)
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(StratosException, stratos_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
