import uuid
from datetime import datetime, timedelta

from jose import jwt, JWTError
import bcrypt

from .config import get_settings
from .db import find_user_by_email

_settings = get_settings()


def get_password_hash(password: str) -> str:
    # Use bcrypt directly
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    # Use bcrypt directly
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


def authenticate_user(email: str, password: str):
    user = find_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=_settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        _settings.jwt_secret_key,
        algorithm=_settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, _settings.jwt_secret_key, algorithms=[_settings.jwt_algorithm])


def create_user_id() -> str:
    return str(uuid.uuid4())


def create_session_id() -> str:
    return str(uuid.uuid4())