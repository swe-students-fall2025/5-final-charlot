"""Session tests"""

from unittest.mock import patch


def test_create_session(test_client, mock_logged_in):
    """Test creating a new session"""

    with patch(
        "app.routers.session_routes.create_session", return_value="12345"
    ) as mock_create_session:
        resp = test_client.post("/session/create", follow_redirects=False)
        assert resp.status_code == 302
        resp.headers["location"] == "/session/get/12345"
        mock_create_session.asserT_called_once()


def test_create_session_unauthorized(test_client):
    """Test that creating session without auth fails"""

    with patch("app.db.create_session") as mock_create_session:
        resp = test_client.post("/session/create", follow_redirects=False)
        assert resp.status_code == 302
        resp.headers["location"] == "/"
        mock_create_session.assert_not_called()


def test_dashboard_unauthorized(test_client):
    """Test that viewing dashboard without auth fails"""

    with patch("app.db.list_sessions_for_user") as mock_list_sessions:
        resp = test_client.get("/session/dashboard", follow_redirects=False)
        assert resp.status_code == 302
        resp.headers["location"] == "/"
        mock_list_sessions.assert_not_called()


def test_chat(test_client, mock_logged_in):
    """Test adding message to a chat"""

    with patch("app.routers.chat_routes.add_message_to_session"), patch("app.routers.chat_routes.get_session_info"):
        resp = test_client.post(
            "/chat/session_id/message", json={"message": "Hello"}, follow_redirects=False
        )
        assert resp.status_code == 200


def test_chat_msg_unauthorized(test_client):
    """Test that chatting without auth fails"""

    with patch("app.routers.chat_routes.add_message_to_session") as mock_add_message:
        resp = test_client.post(
            "/chat/session_id/message", json={"message": "Hello"}, follow_redirects=False
        )
        assert resp.status_code == 302
        resp.headers["location"] == "/"
        mock_add_message.assert_not_called()


def test_chat_without_session(test_client):
    """Test trying to chat without a session"""

    with patch("app.routers.chat_routes.add_message_to_session") as mock_add_message, patch(
        "app.routers.session_routes.get_session_info", return_value=None
    ):
        resp = test_client.post(
            "/chat/session_id/message", json={"message": "Hello"}, follow_redirects=False
        )
        assert resp.status_code == 302
        resp.headers["location"] == "/"
        mock_add_message.assert_not_called()


def test_chat_unknown_session(test_client, mock_logged_in):
    """Test trying to chat in a session that isn't yours"""

    with patch("app.routers.chat_routes.add_message_to_session") as mock_add_message:
        resp = test_client.post(
            "/chat/unknown_session/message", json={"message": "Hello"}, follow_redirects=False
        )
        assert resp.status_code == 302
        resp.headers["location"] == "/"
        mock_add_message.assert_not_called()
