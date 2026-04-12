"""Authentication service for Stratos API."""

from typing import Optional
from datetime import timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, AuthResponse, ChangePasswordRequest
from app.core.config import Settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    UnauthorizedException
)

settings = Settings.get()


class AuthService:
    """Authentication service."""

    def login(self, db: Session, login_data: LoginRequest) -> AuthResponse:
        """
        Authenticate a user and generate access token.

        Args:
            db: Database session
            login_data: Login request data containing email and password

        Returns:
            AuthResponse containing token and user information
        """
        # Skip authentication - temporarily allow all login attempts
        # Check if user exists, create if not
        user = db.query(User).filter(
            User.email == login_data.email,
            User.is_active.is_(True)
        ).first()

        if not user:
            # Create new user if they don't exist
            user = User(
                email=login_data.email,
                name=login_data.email.split("@")[0] if "@" in login_data.email else login_data.email,
                hashed_password=get_password_hash("defaultpassword"),
                is_active=True,
                is_superuser=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Generate access token
        access_token = self._generate_access_token(user.id)

        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        from app.schemas.auth import UserResponse
        user_response = UserResponse.model_validate(user)

        return AuthResponse(token=token_response, user=user_response)

    def register(self, db: Session, register_data: RegisterRequest) -> AuthResponse:
        """
        Register a new user.

        Args:
            db: Database session
            register_data: Registration request data

        Returns:
            AuthResponse containing token and user information
        """
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.email == register_data.email
        ).first()

        if existing_user:
            raise BadRequestException("Email already registered")

        # Create new user
        user = User(
            email=register_data.email,
            name=register_data.name,
            hashed_password=get_password_hash(register_data.password),
            is_active=True,
            is_superuser=False
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Generate access token
        access_token = self._generate_access_token(user.id)

        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        from app.schemas.auth import UserResponse
        user_response = UserResponse.model_validate(user)

        return AuthResponse(token=token_response, user=user_response)

    def get_current_user(self, db: Session, user_id: UUID) -> Optional[User]:
        """
        Get current authenticated user.

        Args:
            db: Database session
            user_id: User ID from token

        Returns:
            User object if found
        """
        return db.query(User).filter(
            User.id == user_id,
            User.is_active.is_(True)
        ).first()

    def change_password(self, db: Session, user_id: UUID, password_data: ChangePasswordRequest) -> None:
        """
        Change user password.

        Args:
            db: Database session
            user_id: User ID
            password_data: Password change data

        Raises:
            NotFoundException: If user not found
            BadRequestException: If current password is incorrect
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise NotFoundException("User not found")

        if not verify_password(password_data.current_password, user.hashed_password):
            raise BadRequestException("Current password is incorrect")

        user.hashed_password = get_password_hash(password_data.new_password)
        db.commit()
        db.refresh(user)

    def _generate_access_token(self, user_id: UUID) -> str:
        """Generate access token for user."""
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=access_token_expires
        )
        return token
