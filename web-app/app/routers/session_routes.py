"""Code for manging sessions"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import create_session, get_session_info, list_sessions_for_user
from app.deps import logged_in

router = APIRouter(prefix="/session", tags=["sessions"])
templates = Jinja2Templates(directory="templates")


@router.post("/create")
def create_new_session(current_user=Depends(logged_in)):
    """Create a new chat session for the user"""

    if not current_user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    inserted_id = create_session(current_user.id)
    return RedirectResponse(f"/session/get/{inserted_id}", status_code=status.HTTP_302_FOUND)


@router.get("/dashboard")
def get_sessions(request: Request, current_user=Depends(logged_in)):
    """Get a list of all chat sessions for the user"""

    if not current_user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    sessions = list_sessions_for_user(current_user.id)
    return templates.TemplateResponse(request, "dashboard.html", {"data": sessions})


@router.get("/get/{session_id}")
def get_session(request: Request, session_id: str, current_user=Depends(logged_in)):
    """Render page for a chat"""

    session = get_session_info(session_id, current_user.id)
    if not session:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(request, "session.html", {"data": session.model_dump()})
