"""
Tests for AuthService.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, RegisterRequest, ChangePasswordRequest
from app.models.user import User
from app.core.exceptions import UnauthorizedException, NotFoundException, BadRequestException


class TestAuthService:
    """Tests for AuthService functionality."""

    def test_login_success(self, mock_db_session: Session):
        """Test successful login."""
        # Setup
        auth_service = AuthService()
        login_data = LoginRequest(email="test@example.com", password="password123")

        # Mock user with valid UUID
        from uuid import UUID
        mock_user = Mock(spec=User)
        mock_user.id = UUID("12345678-1234-5678-1234-567812345678")
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_user.is_active = True
        mock_user.is_superuser = False
        from datetime import datetime
        mock_user.created_at = datetime.now()
        mock_user.updated_at = None
        mock_user.avatar_url = None

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # Patch the password verification and token generation
        with patch('app.services.auth_service.verify_password', return_value=True):
            with patch('app.services.auth_service.create_access_token', return_value="test-token"):
                # Execute
                result = auth_service.login(mock_db_session, login_data)

                # Verify
                assert result.token is not None
                assert result.user is not None
                assert result.token.access_token == "test-token"

    def test_login_user_not_found(self, mock_db_session: Session):
        """Test login with user not found."""
        # Setup
        auth_service = AuthService()
        login_data = LoginRequest(email="notfound@example.com", password="password123")

        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Execute and Verify
        with pytest.raises(UnauthorizedException):
            auth_service.login(mock_db_session, login_data)

    def test_login_invalid_password(self, mock_db_session: Session):
        """Test login with invalid password."""
        # Setup
        auth_service = AuthService()
        login_data = LoginRequest(email="test@example.com", password="wrongpassword")

        mock_user = Mock(spec=User)
        mock_user.is_active = True

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # Patch password verification to fail
        with patch('app.services.auth_service.verify_password', return_value=False):
            # Execute and Verify
            with pytest.raises(UnauthorizedException):
                auth_service.login(mock_db_session, login_data)

    def test_register_success(self, mock_db_session: Session):
        """Test successful registration."""
        # Setup
        auth_service = AuthService()
        register_data = RegisterRequest(
            email="newuser@example.com",
            name="New User",
            password="password123"
        )

        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Patch the password hash and token generation
        with patch('app.services.auth_service.get_password_hash', return_value="hashed-password"):
            with patch('app.services.auth_service.create_access_token', return_value="test-token"):
                # Execute
                # We need to mock the actual user creation in the database
                from uuid import UUID
                from datetime import datetime
                mock_user = Mock(spec=User)
                mock_user.id = UUID("12345678-1234-5678-1234-567812345679")
                mock_user.email = register_data.email
                mock_user.name = register_data.name
                mock_user.hashed_password = "hashed-password"
                mock_user.is_active = True
                mock_user.is_superuser = False
                mock_user.created_at = datetime.now()
                mock_user.updated_at = None
                mock_user.avatar_url = None

                # We need to patch the add and commit methods since we're mocking the user creation
                def mock_add(obj):
                    obj.id = mock_user.id
                    obj.created_at = mock_user.created_at

                mock_db_session.add.side_effect = mock_add
                mock_db_session.refresh.side_effect = lambda obj: None

                result = auth_service.register(mock_db_session, register_data)

                # Verify
                assert result.token is not None
                assert result.user is not None
                assert result.token.access_token == "test-token"

    def test_register_email_already_exists(self, mock_db_session: Session):
        """Test registration with existing email."""
        # Setup
        auth_service = AuthService()
        register_data = RegisterRequest(
            email="existing@example.com",
            name="Existing User",
            password="password123"
        )

        mock_user = Mock(spec=User)
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # Execute and Verify
        with pytest.raises(BadRequestException):
            auth_service.register(mock_db_session, register_data)

    def test_change_password_success(self, mock_db_session: Session):
        """Test successful password change."""
        # Setup
        auth_service = AuthService()
        password_data = ChangePasswordRequest(
            current_password="password123",
            new_password="newpassword456"
        )

        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.hashed_password = "old-hashed-password"

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # Patch password verification and hashing
        with patch('app.services.auth_service.verify_password', return_value=True):
            with patch('app.services.auth_service.get_password_hash', return_value="new-hashed-password"):
                # Execute
                auth_service.change_password(mock_db_session, "test-user-id", password_data)

                # Verify
                assert mock_user.hashed_password == "new-hashed-password"

    def test_change_password_user_not_found(self, mock_db_session: Session):
        """Test password change with user not found."""
        # Setup
        auth_service = AuthService()
        password_data = ChangePasswordRequest(
            current_password="password123",
            new_password="newpassword456"
        )

        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Execute and Verify
        with pytest.raises(NotFoundException):
            auth_service.change_password(mock_db_session, "nonexistent-user", password_data)

    def test_change_password_invalid_current_password(self, mock_db_session: Session):
        """Test password change with invalid current password."""
        # Setup
        auth_service = AuthService()
        password_data = ChangePasswordRequest(
            current_password="wrongpassword",
            new_password="newpassword456"
        )

        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.hashed_password = "old-hashed-password"

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # Patch password verification to fail
        with patch('app.services.auth_service.verify_password', return_value=False):
            # Execute and Verify
            with pytest.raises(BadRequestException):
                auth_service.change_password(mock_db_session, "test-user-id", password_data)
