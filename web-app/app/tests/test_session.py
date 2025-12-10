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


# def test_chat_in_session(auth_header):
#     """Test sending a chat message in a session"""
#     # Create session
#     resp = client.post("/sessions/", headers=auth_header)
#     session_id = resp.json()["session_id"]

#     # Send chat message
#     chat_resp = client.post(
#         "/chat/",
#         json={"session_id": session_id, "message": "Hello, I have a legal question"},
#         headers=auth_header,
#     )
#     assert chat_resp.status_code == 200
#     chat_data = chat_resp.json()
#     assert chat_data["session_id"] == session_id
#     assert len(chat_data["messages"]) >= 2  # user message + ai response
#     assert chat_data["messages"][0]["role"] == "user"
#     assert chat_data["messages"][0]["message"] == "Hello, I have a legal question"
#     assert chat_data["messages"][1]["role"] == "ai"
#     assert "You said:" in chat_data["messages"][1]["message"]


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
