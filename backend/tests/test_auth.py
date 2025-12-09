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


# def test_register_success():
#     """Test successful user registration"""
#     resp = client.post(
#         "/auth/register",
#         json={"email": "test@example.com", "password": "password123"},
#     )
#     assert resp.status_code == 201
#     data = resp.json()
#     assert "user_id" in data
#     assert data["email"] == "test@example.com"


# def test_register_duplicate_email():
#     """Test that duplicate email registration fails"""
#     # Register first user
#     client.post(
#         "/auth/register",
#         json={"email": "test@example.com", "password": "password123"},
#     )

#     # Try to register again with same email
#     resp = client.post(
#         "/auth/register",
#         json={"email": "test@example.com", "password": "different"},
#     )
#     assert resp.status_code == 400
#     assert "already registered" in resp.json()["detail"].lower()


# def test_login_success():
#     """Test successful login"""
#     # Register user first
#     client.post(
#         "/auth/register",
#         json={"email": "test@example.com", "password": "password123"},
#     )

#     # Login
#     resp = client.post(
#         "/auth/login",
#         data={"username": "test@example.com", "password": "password123"},
#         headers={"Content-Type": "application/x-www-form-urlencoded"},
#     )
#     assert resp.status_code == 200
#     token_data = resp.json()
#     assert "access_token" in token_data
#     assert token_data["token_type"] == "bearer"


# def test_login_wrong_password():
#     """Test login with incorrect password"""
#     # Register user
#     client.post(
#         "/auth/register",
#         json={"email": "test@example.com", "password": "password123"},
#     )

#     # Try login with wrong password
#     resp = client.post(
#         "/auth/login",
#         data={"username": "test@example.com", "password": "wrongpassword"},
#         headers={"Content-Type": "application/x-www-form-urlencoded"},
#     )
#     assert resp.status_code == 401


# def test_login_nonexistent_user():
#     """Test login with non-existent email"""
#     resp = client.post(
#         "/auth/login",
#         data={"username": "nobody@example.com", "password": "password123"},
#         headers={"Content-Type": "application/x-www-form-urlencoded"},
#     )
#     assert resp.status_code == 401
