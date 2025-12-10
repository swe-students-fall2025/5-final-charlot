"""Test authorization"""

from unittest.mock import patch


def test_register_success(test_client, mock_settings, mock_user, mock_access_token):
    """Test successful user registration"""

    with patch("app.auth.get_password_hash"):
        resp = test_client.post(
            "/auth/register",
            data={"username": "random_username", "password": "random_password"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert "set-cookie" in resp.headers
        assert "access_token" in resp.headers["set-cookie"]
        assert resp.headers.get("location") == "/"


def test_register_duplicate_email(test_client, mock_settings, mock_user, mock_access_token):
    """Test that duplicate email registration fails"""

    resp = test_client.post(
        "/auth/register",
        data={"username": "taken_username", "password": "random_password"},
    )
    assert resp.status_code == 409
    html = resp.text
    assert "Username already registered" in html
    mock_access_token.assert_not_called()


def test_register_no_input(test_client, mock_access_token):
    """Test that no input fails"""

    resp = test_client.post(
        "/auth/register",
        data={},
    )
    assert resp.status_code == 422
    mock_access_token.assert_not_called()


def test_logged_in_register(test_client, mock_logged_in, mock_access_token):
    """Test register when already logged in"""

    resp = test_client.post(
        "/auth/register",
        data={"username": "random_username", "password": "random_password"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["location"] == "/"
    mock_access_token.assert_not_called()


def test_login_success(test_client, mock_settings, mock_authenticate):
    """Test successful login"""

    resp = test_client.post(
        "/auth/login",
        data={"username": "taken_username", "password": "correct_password"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "set-cookie" in resp.headers
    assert "access_token" in resp.headers["set-cookie"]
    assert resp.headers.get("location") == "/"


def test_login_bad_uname(test_client, mock_settings, mock_authenticate, mock_access_token):
    """Test incorrect login"""

    resp = test_client.post(
        "/auth/login", data={"username": "random_username", "password": "correct_password"}
    )
    assert resp.status_code == 401
    html = resp.text
    assert "Incorrect username or password" in html
    mock_access_token.assert_not_called()


def test_login_bad_pw(test_client, mock_settings, mock_authenticate, mock_access_token):
    """Test incorrect login"""

    resp = test_client.post(
        "/auth/login", data={"username": "taken_username", "password": "incorrect_password"}
    )
    assert resp.status_code == 401
    html = resp.text
    assert "Incorrect username or password" in html
    mock_access_token.assert_not_called()


def test_logged_in_login(test_client, mock_logged_in, mock_access_token):
    """Test login when already logged in"""

    resp = test_client.post(
        "/auth/login",
        data={"username": "random_username", "password": "random_password"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["location"] == "/"
    mock_access_token.assert_not_called()


def test_login_no_input(test_client, mock_access_token):
    """Test that no input fails"""

    resp = test_client.post(
        "/auth/login",
        data={},
    )
    assert resp.status_code == 422
    mock_access_token.assert_not_called()
