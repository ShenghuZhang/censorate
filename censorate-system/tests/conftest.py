"""
Pytest configuration for Stratos tests.
"""

import pytest
import sys
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture
def mock_settings():
    """Mock settings fixture."""
    from app.core.config import Settings
    settings = Settings(
        DATABASE_URL="sqlite:///:memory:",
        DEEPAGENT_API_URL="http://localhost:8001",
        DEEPAGENT_API_KEY="test_key",
        JWT_SECRET_KEY="test_secret",
        DEBUG=True
    )
    return settings


@pytest.fixture
def mock_db_session():
    """Mock database session fixture."""
    from unittest.mock import Mock
    return Mock()


@pytest.fixture
def test_client():
    """Test client fixture."""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


@pytest.fixture
def sample_project_data():
    """Sample project data fixture."""
    return {
        "name": "Test Project",
        "description": "A test project",
        "project_type": "software"
    }


@pytest.fixture
def sample_requirement_data():
    """Sample requirement data fixture."""
    return {
        "title": "Test Requirement",
        "description": "A test requirement",
        "priority": "high",
        "source": "manual"
    }


@pytest.fixture
def sample_user_data():
    """Sample user data fixture."""
    return {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    }
