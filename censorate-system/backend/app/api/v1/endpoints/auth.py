"""Authentication endpoints for Censorate API."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    UserResponse,
    ChangePasswordRequest
)
from app.services.auth_service import AuthService
from app.core.security import get_current_user
from app.core.exceptions import CensorateException
from app.models.user import User

router = APIRouter()
auth_service = AuthService()


@router.post("/auth/login", response_model=AuthResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return access token.

    - **email**: User email address
    - **password**: User password
    """
    return auth_service.login(db, login_data)


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    - **email**: User email address
    - **name**: User full name
    - **password**: Password (min 6 characters)
    """
    return auth_service.register(db, register_data)


@router.get("/auth/me", response_model=UserResponse)
def get_current_user_info(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.
    """
    from uuid import UUID
    user = auth_service.get_current_user(db, UUID(current_user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return UserResponse.model_validate(user)


@router.post("/auth/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    password_data: ChangePasswordRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user password.

    - **current_password**: Current password
    - **new_password**: New password (min 6 characters)
    """
    from uuid import UUID
    auth_service.change_password(db, UUID(current_user_id), password_data)
    return None
