"""Test authorization"""

from unittest.mock import Mock, patch


def test_register_success(test_client, mock_user_collection):
    """Test successful user registration"""

    with patch("app.routers.auth_routes.login_user") as mock_login:
        resp = test_client.post(
            "/auth/register", data={"username": "random_username", "password": "random_password"}
        )
        assert resp.status_code == 201
        mock_login.assert_called_once()


def test_register_duplicate_email(test_client, mock_user_collection):
    """Test that duplicate email registration fails"""

    resp = test_client.post(
        "/auth/register",
        data={"username": "taken_username", "password": "random_password"},
    )
    assert resp.status_code == 409


def test_logged_in_register(test_client):
    """Test register when already logged in"""

    mock_user = Mock()
    mock_user.is_authenticated = True
    with (
        patch("app.routers.auth_routes.create_user") as mock_create_user,
        patch("app.routers.auth_routes.current_user", mock_user),
    ):
        resp = test_client.post(
            "/auth/register",
            data={"username": "random_username", "password": "random_password"},
        )
        assert resp.status_code == 409
        mock_create_user.assert_not_called()


def test_login_success(test_client, mock_user_collection, mock_user):
    """Test successful login"""

    with patch("app.routers.auth_routes.login_user") as mock_login:
        resp = test_client.post(
            "/auth/login",
            data={"username": "taken_username", "password": "correct_password"},
        )
        assert resp.status_code == 200
        mock_login.assert_called_once()


def test_login_wrong_password(test_client, mock_user_collection, mock_user):
    """Test login with incorrect password"""

    with patch("app.routers.auth_routes.login_user") as mock_login:
        resp = test_client.post(
            "/auth/login",
            data={"username": "taken_username", "password": "incorrect_password"},
        )
        assert resp.status_code == 401
        mock_login.assert_not_called()


def test_login_nonexistent_user(test_client, mock_user_collection):
    """Test login with non-existent email"""

    with patch("app.routers.auth_routes.login_user") as mock_login:
        resp = test_client.post(
            "/auth/login",
            data={"username": "nonexistent_username", "password": "random_password"},
        )
        assert resp.status_code == 401
        mock_login.assert_not_called()


def test_logged_in_login(test_client):
    """Test login when already logged in"""

    mock_user = Mock()
    mock_user.is_authenticated = True
    with (
        patch("app.routers.auth_routes.login_user") as mock_login,
        patch("app.routers.auth_routes.current_user", mock_user),
    ):
        resp = test_client.post(
            "/auth/login",
            data={"username": "random_username", "password": "random_password"},
        )
        assert resp.status_code == 409
        mock_login.assert_not_called()


def test_logged_in_logout(test_client):
    with patch("app.routers.auth_routes.logout_user") as mock_logout:
        resp = test_client.get("/auth/logout")
        assert resp.status_code == 401
        mock_logout.assert_not_called()


def test_logout(test_client):
    mock_user = Mock()
    mock_user.is_authenticated = True
    with (
        patch("app.routers.auth_routes.logout_user") as mock_logout,
        patch("flask_login.utils.current_user", mock_user),
    ):
        resp = test_client.get("/auth/logout")
        assert resp.status_code == 204
        mock_logout.assert_called_once()
