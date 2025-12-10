from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import authenticate_user, create_access_token, get_password_hash
from app.config import get_settings
from app.db import create_user, find_user_by_username
from app.models import Token, UserCreate
from app.deps import logged_in

router = APIRouter(prefix="/auth", tags=["auth"])
_settings = get_settings()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user: Annotated[UserCreate, Form()], current_user=Depends(logged_in)):
    """Register a new user"""

    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    existing = find_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")

    password_hash = get_password_hash(user.password)
    created = create_user(user.username, password_hash)

    access_token_expires = timedelta(minutes=_settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(created.inserted_id)},
        expires_delta=access_token_expires,
    )
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie("access_token", access_token, httponly=True)
    return response


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], current_user=Depends(logged_in)
):
    """Log in a user"""

    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    try:
        user = authenticate_user(form_data.username, form_data.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password"
        )

    access_token_expires = timedelta(minutes=_settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token)


@router.get("/register")
def register_page():
    """Registration page"""

    return "REGISTER PAGE"


@router.get("/login")
def login_page():
    """Login page"""

    return "LOGIN PAGE"
