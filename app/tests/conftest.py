"""Mocks client, db, and user"""

from unittest.mock import Mock, patch

import pytest
from bson import ObjectId

from app import create_app


@pytest.fixture
def test_app():
    """Create and configure new test app instance"""

    test_app = create_app()
    test_app.config.update({"TESTING": True, "SECRET_KEY": "test_secret_key"})
    yield test_app


@pytest.fixture
def test_client(test_app):
    """Client for testing"""
    yield test_app.test_client()


def side_effect_user(query: dict):
    """Mock finding a user"""

    if query["username"] == "taken_username":
        return {
            "_id": ObjectId(),
            "username": query["username"],
            "hashed_password": "correct_password",
        }
    return None


@pytest.fixture
def mock_user_collection():
    """Mock user collection"""

    with patch("app.db.db.users") as user_mock:
        user_mock.find_one = Mock(side_effect=side_effect_user)
        user_mock.insert_one = Mock(return_value=Mock(inserted_id=ObjectId(), acknowledged=True))
        yield user_mock


def side_effect_check_pw(query: str):
    """Mock checking password"""

    if query == "correct_password":
        return True
    return False


@pytest.fixture
def mock_user():
    """Mock user"""

    with patch("app.models.User") as user_mock:
        user_instance = Mock()
        user_instance.username = Mock()
        user_instance.check_password = Mock(side_effect=side_effect_check_pw)
        user_instance.set_password = Mock()
        user_mock.return_value = user_instance
        yield user_mock
