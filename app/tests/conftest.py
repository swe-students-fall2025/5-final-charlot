"""Mocks client, db, and user"""

import pytest

from app import create_app
from unittest.mock import patch, Mock


@pytest.fixture
def test_app():
    """Create and configure new test app instance"""

    test_app = create_app()
    test_app.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "test_secret_key"
        }
    )
    yield test_app


@pytest.fixture
def test_client(test_app):
    """Client for testing"""
    yield test_app.test_client()


@pytest.fixture
def mock_db():
    """Mock database"""

    with patch("app.db") as db_mock:
        db_mock.users = Mock()
        db_mock.sessions = Mock()
        yield db_mock
