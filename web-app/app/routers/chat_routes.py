"""Chat routes"""

from fastapi import APIRouter, Depends, Form, Request, UploadFile, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import (
    add_message_to_session,
    get_session_info,
    create_session
)
from app.deps import logged_in

router = APIRouter(prefix="/chat", tags=["chat"])
templates = Jinja2Templates(directory="templates")
CLIENT_URL = "http://localhost:5000"


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

    # TODO: call Hyu's ML client here later.
    ai_text = f"(Dummy response) You said: {message}"

    add_message_to_session(session_id, "client", ai_text)

    return status.HTTP_200_OK


@router.post("/file")
def send_file(file: UploadFile, current_user=Depends(logged_in)):
    """Add a file to the chat"""

    if not current_user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    contents = file.file.read()
    session_id = create_session(current_user.id)
    add_message_to_session(session_id, "user", f"You sent a file: {file.filename}")

    # TODO: send file to hyunkyu

    return RedirectResponse(f"/chat/get/{str(session_id)}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/get/{session_id}")
def get_session(request: Request, session_id: str, current_user=Depends(logged_in)):
    """Render page for a chat"""

    if not current_user or session_id not in current_user.sessions:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    session = get_session_info(session_id, user_id=current_user.id)
    if not session:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        request, "chat.html", {"current_user": current_user, "data": session.model_dump()}
    )
