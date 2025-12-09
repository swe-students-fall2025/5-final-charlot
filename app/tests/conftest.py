"""Mocks client, db, and user"""

from bson import ObjectId
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app import create_app


@pytest.fixture
def test_client():
    """Create and configure new test app/client instance"""

    test_app = create_app()
    test_client = TestClient(test_app)
    yield test_client


@pytest.fixture
def mock_settings():
    """Mock settings"""

    with patch("app.config.get_settings") as mock_settings:
        yield mock_settings


def side_effect_user(query: dict):
    """Mock finding a user"""

    if query["username"] == "taken_username":
        return {
            "_id": ObjectId(),
            "username": query["username"],
            "password_hash": "correct_password",
            "sesions": []
        }
    return None


@pytest.fixture
def mock_user():
    """Mock user db functions"""

    with patch("app.db.users_collection") as user_mock:
        user_mock.find_one = Mock(side_effect=side_effect_user)
        user_mock.insert_one = Mock(return_value=Mock(inserted_id=ObjectId(), acknowledged=True))
        yield user_mock
