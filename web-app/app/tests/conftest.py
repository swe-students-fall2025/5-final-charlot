"""Mocks client, db, and user"""

from unittest.mock import Mock, patch

import pytest
from bson import ObjectId
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

import app.models as models
from app import create_app


@pytest.fixture
def test_app():
    """Create and configure new test app instance"""

    test_app = create_app()
    yield test_app


@pytest.fixture
def test_client(test_app):
    """Create a new test client"""

    test_client = TestClient(test_app)
    yield test_client


@pytest.fixture
def mock_settings():
    """Mock settings"""

    with patch("app.config.get_settings") as mock_settings:
        yield mock_settings


def side_effect_user(query: dict):
    """Mock finding a user"""

    if query.get("username") == "taken_username":
        return {
            "_id": ObjectId(),
            "username": query["username"],
            "password_hash": "correct_password",
            "sesions": [],
        }
    return None


@pytest.fixture
def mock_user():
    """Mock user db functions"""

    with patch("app.db.users_collection") as user_mock:
        user_mock.find_one = Mock(side_effect=side_effect_user)
        user_mock.insert_one = Mock(return_value=Mock(inserted_id=ObjectId(), acknowledged=True))
        yield user_mock


@pytest.fixture
def mock_oauth2_scheme():
    """Mock OAuth2 token to simulate a logged-in user"""

    fake_token = "fake_access_token"
    with patch("app.deps.oauth2_scheme", return_value=fake_token):
        yield fake_token


@pytest.fixture
def mock_logged_in():
    """Mock get_current_user succeeds"""

    fake_user = models.User(id="id", username="username", password_hash="password", sessions=[])
    with patch("app.deps.get_current_user", return_value=fake_user) as mock_logged_in:
        yield mock_logged_in


@pytest.fixture
def mock_logged_out():
    """Mock get_current_user fails"""

    with patch(
        "app.deps.get_current_user",
        side_effect=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED),
    ) as mock_logged_in:
        yield mock_logged_in


def side_effect_auth(username: str, password: str):
    """Mock authenticating user"""

    fake_user = models.User(id="id", username=username, password_hash="password_hash", sessions=[])
    if password == "correct_password" and username == "taken_username":
        return fake_user
    raise ValueError()


@pytest.fixture
def mock_authenticate():
    """Mock authenticating login"""

    with patch(
        "app.routers.auth_routes.authenticate_user", side_effect=side_effect_auth
    ) as authenticate_mock:
        yield authenticate_mock


@pytest.fixture
def mock_access_token():
    """Mock function to create token"""

    with patch("app.auth.create_access_token") as mock_access_token:
        yield mock_access_token
