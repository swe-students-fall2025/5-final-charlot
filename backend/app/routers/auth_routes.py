from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
)
from backend.app.config import get_settings
from backend.app.db import create_user, find_user_by_username
from backend.app.models import UserCreate, Token

router = APIRouter(prefix="/auth", tags=["auth"])
_settings = get_settings()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    """Register a new user"""

    existing = find_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    password_hash = get_password_hash(user.password)
    created = create_user(user.username, password_hash)

    access_token_expires = timedelta(minutes=_settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(created.inserted_id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        user = authenticate_user(form_data.username, form_data.password)
    except ValueError:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=_settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["user_id"]},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token)
