from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ..auth import (
    create_user_id,
    get_password_hash,
    authenticate_user,
    create_access_token,
)
from ..config import get_settings
from ..db import create_user, find_user_by_email
from ..models import UserCreate, Token

router = APIRouter(prefix="/auth", tags=["auth"])
_settings = get_settings()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    existing = find_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = create_user_id()
    password_hash = get_password_hash(user.password)
    create_user(user_id, user.email, password_hash)

    return {"user_id": user_id, "email": user.email}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token_expires = timedelta(
        minutes=_settings.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user["user_id"]},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token)
