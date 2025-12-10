"""Chat routes"""
from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import RedirectResponse

from app.db import add_message_to_session, get_session_info, add_file_to_session
from app.deps import logged_in

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{session_id}/message")
def add_message(session_id: str, message: str, current_user=Depends(logged_in)):
    """Add a message to the current chat"""

    if not current_user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    session = get_session_info(session_id, user_id=current_user.id)
    if not session:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    add_message_to_session(session_id, "user", message)

    # TODO: call Hyu's ML client here later.
    ai_text = f"(Dummy response) You said: {message}"

    add_message_to_session(session_id, "client", ai_text)

    return status.HTTP_200_OK


@router.post("/{session_id}/file")
def add_file(session_id: str, file: UploadFile, current_user=Depends(logged_in)):
    """Add a file to the chat"""

    if not current_user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    session = get_session_info(session_id, user_id=current_user.id)
    if not session:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    # add_file_to_session(session_id, file.filename, filepath)
    # return {"session_id": session_id, "filename": file.filename, "path": filepath}

    return status.HTTP_200_OK
