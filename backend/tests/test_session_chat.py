# import pytest
# from fastapi.testclient import TestClient
# from backend.app.app import app
# from app.db import users_collection, sessions_collection

# client = TestClient(app)


# @pytest.fixture(autouse=True)
# def clean_db():
#     """Clean database before each test"""
#     users_collection.delete_many({})
#     sessions_collection.delete_many({})
#     yield
#     users_collection.delete_many({})
#     sessions_collection.delete_many({})


# @pytest.fixture
# def auth_header():
#     """Create a user and return authorization header"""
#     client.post(
#         "/auth/register",
#         json={"email": "user@example.com", "password": "pass123"},
#     )
#     login_resp = client.post(
#         "/auth/login",
#         data={"username": "user@example.com", "password": "pass123"},
#         headers={"Content-Type": "application/x-www-form-urlencoded"},
#     )
#     token = login_resp.json()["access_token"]
#     return {"Authorization": f"Bearer {token}"}


# def test_create_session(auth_header):
#     """Test creating a new session"""
#     resp = client.post("/sessions/", headers=auth_header)
#     assert resp.status_code == 200
#     data = resp.json()
#     assert "session_id" in data


# def test_create_session_unauthorized():
#     """Test that creating session without auth fails"""
#     resp = client.post("/sessions/")
#     assert resp.status_code == 401


# def test_list_sessions(auth_header):
#     """Test listing user's sessions"""
#     # Create two sessions
#     resp1 = client.post("/sessions/", headers=auth_header)
#     session_id_1 = resp1.json()["session_id"]
    
#     resp2 = client.post("/sessions/", headers=auth_header)
#     session_id_2 = resp2.json()["session_id"]
    
#     # List sessions
#     resp = client.get("/sessions/", headers=auth_header)
#     assert resp.status_code == 200
#     data = resp.json()
#     assert "sessions" in data
#     assert len(data["sessions"]) == 2
    
#     session_ids = [s["session_id"] for s in data["sessions"]]
#     assert session_id_1 in session_ids
#     assert session_id_2 in session_ids


# def test_list_sessions_unauthorized():
#     """Test that listing sessions without auth fails"""
#     resp = client.get("/sessions/")
#     assert resp.status_code == 401


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