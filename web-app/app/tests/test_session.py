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


# def test_chat_nonexistent_session(auth_header):
#     """Test that chatting in non-existent session fails"""
#     resp = client.post(
#         "/chat/",
#         json={"session_id": "fake-session-id", "message": "Hello"},
#         headers=auth_header,
#     )
#     assert resp.status_code == 404


# def test_chat_unauthorized():
#     """Test that chatting without auth fails"""
#     resp = client.post(
#         "/chat/",
#         json={"session_id": "some-id", "message": "Hello"},
#     )
#     assert resp.status_code == 401


# def test_multiple_messages_in_session(auth_header):
#     """Test sending multiple messages builds conversation history"""
#     # Create session
#     resp = client.post("/sessions/", headers=auth_header)
#     session_id = resp.json()["session_id"]

#     # Send first message
#     client.post(
#         "/chat/",
#         json={"session_id": session_id, "message": "First message"},
#         headers=auth_header,
#     )

#     # Send second message
#     resp2 = client.post(
#         "/chat/",
#         json={"session_id": session_id, "message": "Second message"},
#         headers=auth_header,
#     )

#     # Should have 4 messages total (2 user + 2 ai)
#     assert len(resp2.json()["messages"]) == 4


# def test_upload_file_to_session(auth_header):
#     """Test uploading a file to a session"""
#     # Create session
#     resp = client.post("/sessions/", headers=auth_header)
#     session_id = resp.json()["session_id"]

#     # Create a test file
#     file_content = b"Test file content"
#     files = {"file": ("test.txt", file_content, "text/plain")}
#     data = {"session_id": session_id}

#     # Upload file
#     upload_resp = client.post(
#         "/upload/",
#         files=files,
#         data=data,
#         headers=auth_header,
#     )
#     assert upload_resp.status_code == 200
#     upload_data = upload_resp.json()
#     assert upload_data["session_id"] == session_id
#     assert upload_data["filename"] == "test.txt"
#     assert "path" in upload_data


# def test_upload_unauthorized():
#     """Test that uploading without auth fails"""
#     files = {"file": ("test.txt", b"content", "text/plain")}
#     data = {"session_id": "fake-id"}

#     resp = client.post("/upload/", files=files, data=data)
#     assert resp.status_code == 401


# def test_upload_to_nonexistent_session(auth_header):
#     """Test that uploading to non-existent session fails"""
#     files = {"file": ("test.txt", b"content", "text/plain")}
#     data = {"session_id": "fake-session-id"}

#     resp = client.post(
#         "/upload/",
#         files=files,
#         data=data,
#         headers=auth_header,
#     )
#     assert resp.status_code == 404
