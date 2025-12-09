"""Authorization routes for the web app"""

from flask import Blueprint, request
from flask_login import current_user, login_required, login_user, logout_user

from app import models
from app.db import create_user, find_user_by_username

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Registration route"""

    if current_user.is_authenticated:
        return "User already logged in", 409

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    if not username or not password:
        return "No user name or password", 400

    existing = find_user_by_username(username)
    if existing:
        return "Username already registered", 409

    new_user = models.User({"username": username})
    new_user.set_password(password)

    inserted = create_user(new_user)
    new_user.id = inserted.inserted_id

    login_user(new_user)

    return "Registered and logged in!", 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login route"""

    if current_user.is_authenticated:
        return "User already logged in", 409

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        return "No user name or password", 400

    user_data = find_user_by_username(username)
    user = models.User(user_data) if user_data else None

    if not user or not user.check_password(password):
        return "Invalid username or password", 401

    login_user(user)
    return "Logged in!", 200


@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout current logged in user"""

    logout_user()
    return "Logged out", 204
