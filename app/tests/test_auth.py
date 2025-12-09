# """Test authorization"""

# from unittest.mock import patch


# def test_register_success(test_client, mock_settings, mock_user):
#     """Test successful user registration"""

#     with patch("app.auth.get_password_hash"), patch("app.auth.create_access_token") as mock_token:
#         mock_token.return_value = str()
#         resp = test_client.post(
#             "/auth/register",
#             data={"username": "random_username", "password": "random_password"},
#         )
#         assert resp.status_code == 201
#         json = resp.json()
#         assert "access_token" in json
#         assert json.get("token_type") == "bearer"


# def test_register_duplicate_email(test_client, mock_settings, mock_user):
#     """Test that duplicate email registration fails"""

#     resp = test_client.post(
#         "/auth/register",
#         data={"username": "taken_username", "password": "random_password"},
#     )
#     assert resp.status_code == 409
#     json = resp.json()
#     assert json.get("detail") == "Username already registered"


# def test_register_no_input(test_client):
#     """Test that no input fails"""

#     resp = test_client.post(
#         "/auth/register",
#         data={},
#     )
#     assert resp.status_code == 422


# def test_logged_in_register(test_client, mock_oauth2_scheme, mock_logged_in):
#     """Test register when already logged in"""

#     resp = test_client.post(
#         "/auth/register",
#         data={"username": "random_username", "password": "random_password"},
#         follow_redirects=False
#     )
#     assert resp.status_code == 302
#     assert resp.headers["location"] == "/"


# def test_login_success(test_client, mock_settings, mock_authenticate):
#     """Test successful login"""

#     resp = test_client.post(
#         "/auth/login",
#         data={"username": "taken_username", "password": "correct_password"}
#     )
#     assert resp.status_code == 200
#     json = resp.json()
#     assert "access_token" in json
#     assert json.get("token_type") == "bearer"


# def test_login_bad_uname(test_client, mock_settings, mock_authenticate):
#     """Test incorrect login"""

#     resp = test_client.post(
#         "/auth/login",
#         data={"username": "random_username", "password": "correct_password"}
#     )
#     assert resp.status_code == 401
#     json = resp.json()
#     assert json.get("detail") == "Incorrect username or password"


# def test_login_bad_pw(test_client, mock_settings, mock_authenticate):
#     """Test incorrect login"""

#     resp = test_client.post(
#         "/auth/login",
#         data={"username": "taken_username", "password": "incorrect_password"}
#     )
#     assert resp.status_code == 401
#     json = resp.json()
#     assert json.get("detail") == "Incorrect username or password"


# def test_logged_in_login(test_client, mock_oauth2_scheme, mock_logged_in):
#     """Test regiloginster when already logged in"""

#     resp = test_client.post(
#         "/auth/login",
#         data={"username": "random_username", "password": "random_password"},
#         follow_redirects=False
#     )
#     assert resp.status_code == 302
#     assert resp.headers["location"] == "/"


# def test_login_no_input(test_client):
#     """Test that no input fails"""

#     resp = test_client.post(
#         "/auth/login",
#         data={},
#     )
#     assert resp.status_code == 422
