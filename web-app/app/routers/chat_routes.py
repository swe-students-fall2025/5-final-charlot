"""Chat routes"""

from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request, UploadFile, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import requests

from app.db import (
    add_message_to_session,
    get_session_info,
    create_session,
    list_sessions_for_user,
    delete_session
)
from app.deps import logged_in
from app.config import get_settings

router = APIRouter(prefix="/chat", tags=["chat"])
_settings = get_settings()

# Get the templates directory path
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
CLIENT_URL = _settings.ml_service_url


@router.post("/{session_id}/message")
def add_message(
    session_id: str, message: str = Form(...), current_user=Depends(logged_in)
):
    """Add a message to the current chat"""

    if not current_user or session_id not in current_user.sessions:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    session = get_session_info(session_id, user_id=current_user.id)
    if not session:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    add_message_to_session(session_id, "user", message)

    resp = requests.post(
        url=f"{CLIENT_URL}/query",
        json={"query": message}
    )
    json = resp.json()

    response = json["final_explanation"]

    add_message_to_session(session_id, "client", response)

    return JSONResponse({"response": response})


@router.post("/file")
def send_file(request: Request, file: UploadFile, current_user=Depends(logged_in)):
    """Add a file to the chat"""

    if not current_user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    session_id = create_session(current_user.id, file.filename)
    add_message_to_session(session_id, "user", f"You sent a file: {file.filename}")

    files = {"file": (file.filename, file.file, file.content_type)}
    resp = requests.post(
        url=f"{CLIENT_URL}/index-document",
        files=files,
        data={"user_id": current_user.id, "session_id": session_id}
    )

    if resp.status_code != status.HTTP_200_OK:
        return templates.TemplateResponse(request, "upload.html", {"error": "Please try again"})

    return RedirectResponse(f"/chat/get/{str(session_id)}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/get/{session_id}")
def get_session(request: Request, session_id: str, current_user=Depends(logged_in)):
    """Render page for a chat"""

    if not current_user or session_id not in current_user.sessions:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    session = get_session_info(session_id, user_id=current_user.id)
    if not session:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    sessions = list_sessions_for_user(current_user.id)

    return templates.TemplateResponse(
        request, "chat.html", {"current_user": current_user, "sessions": sessions, "data": session}
    )


@router.post("/{session_id}/delete")
def remove_session(session_id: str, current_user=Depends(logged_in)):
    """Delete a chat session for the current user"""
    if not current_user or session_id not in current_user.sessions:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    deleted = delete_session(user_id=current_user.id, session_id=session_id)
    if not deleted:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
