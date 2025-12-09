"""Authorization routes for the web app"""

from flask import Blueprint, request
from flask_login import current_user, login_required, login_user, logout_user

from app import models
from app.db import create_user, find_user_by_id, find_user_by_username

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Registration route"""

    if current_user.is_authenticated:
        return "User already logged in"

    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return "No user name or password"

    existing = find_user_by_username(username)
    if existing:
        return "Username already registered"

    new_user = models.User({"username": username})
    new_user.set_password(password)

    inserted = create_user(new_user)
    new_user = find_user_by_id(inserted.inserted_id)

    login_user(models.User(new_user))

    return "Registered and logged in!"


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login route"""

    if current_user.is_authenticated:
        return "User already logged in"

    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return "No user name or password"

    user_data = find_user_by_username(username)

    if not user_data:
        return f"No user with username {username} found"

    user = models.User(user_data)

    if user.check_password(password):
        login_user(user)
        return "Login successful"

    return "Incorrect password"


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Logout current logged in user"""

    logout_user()
    return "Logged out"
