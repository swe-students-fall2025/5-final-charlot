"""Authorization routes"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.auth import authenticate_user, create_access_token, get_password_hash
from app.config import get_settings
from app.db import create_user, find_user_by_username
from app.deps import logged_in
from app.models import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])
_settings = get_settings()
templates = Jinja2Templates(directory="templates")


@router.post("/register")
def register(
    request: Request, user: Annotated[UserCreate, Form()], current_user=Depends(logged_in)
):
    """Register a new user"""

    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    existing = find_user_by_username(user.username)
    if existing:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"error": "Username already registered"},
            status_code=409,
        )

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


@router.post("/login")
def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    current_user=Depends(logged_in),
):
    """Log in a user"""

    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    try:
        user = authenticate_user(form_data.username, form_data.password)
    except ValueError:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Incorrect username or password"},
            status_code=401,
        )

    access_token_expires = timedelta(minutes=_settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires,
    )
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie("access_token", access_token, httponly=True)
    return response


@router.get("/register")
def register_page(request: Request):
    """Registration page"""

    return templates.TemplateResponse(request, "register.html")


@router.get("/login")
def login_page(request: Request):
    """Login page"""

    return templates.TemplateResponse(request, "login.html")
