"""Authorization helper functions"""

from datetime import datetime, timedelta

from jose import jwt
import bcrypt

from config import get_settings
from db import find_user_by_username
import models

_settings = get_settings()


def get_password_hash(password: str) -> str:
    """Generate a hash for a password"""

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password matches the hash"""

    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def authenticate_user(username: str, password: str) -> models.User:
    """Verify username and password"""

    user = find_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        raise ValueError("Incorrect username or password")
    return models.User.model_validate(user)


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Create JWT access token"""

    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        _settings.jwt_secret_key,
        algorithm=_settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode JWT access token"""

    return jwt.decode(token, _settings.jwt_secret_key, algorithms=[_settings.jwt_algorithm])

# def create_session_id() -> str:
#     return str(uuid.uuid4())
