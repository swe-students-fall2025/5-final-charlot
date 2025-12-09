"""Models used throughout the web-app"""

from dataclasses import dataclass

import bcrypt
from flask_login import UserMixin


class User(UserMixin):
    """User model wrapper"""

    def __init__(self, user_data: dict):
        self.id: str = str(user_data.get("_id", ""))
        self.username: str = user_data.get("username", "")
        self.password_hash: str = user_data.get("password_hash", "")

    def set_password(self, password: str):
        """Hash password and update both object + underlying dict"""
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.password_hash = hashed

    def check_password(self, password: str) -> bool:
        """Check the password provided against the stored password"""
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))


@dataclass
class ChatRequest:
    session_id: str
    message: str


@dataclass
class Message:
    role: str
    message: str
    timestamp: str


@dataclass
class ChatResponse:
    session_id: str
    messages: list[Message]


@dataclass
class SessionCreateResponse:
    session_id: str


@dataclass
class SessionSummary:
    session_id: str


@dataclass
class SessionListResponse:
    sessions: list[SessionSummary]
