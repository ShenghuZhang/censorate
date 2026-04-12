"""Authentication schemas for Censorate API."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, model_validator
from uuid import UUID


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr = Field(..., description="User email")
    emailAddress: EmailStr | None = Field(None, description="User email (alias)")
    password: str = Field(..., min_length=1, description="User password")

    @model_validator(mode="before")
    @classmethod
    def handle_email_alias(cls, values):
        """Handle both email and emailAddress fields."""
        if isinstance(values, dict):
            if "emailAddress" in values and "email" not in values:
                values["email"] = values["emailAddress"]
            # Always remove emailAddress to avoid conflicts
            if "emailAddress" in values:
                del values["emailAddress"]
        return values


class RegisterRequest(BaseModel):
    """Schema for user registration request."""
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., min_length=1, max_length=255, description="User full name")
    password: str = Field(..., min_length=6, max_length=128, description="Password (min 6 characters)")


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    name: str
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for full authentication response."""
    token: TokenResponse
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=6, max_length=128, description="New password (min 6 characters)")
