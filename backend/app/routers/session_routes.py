from fastapi import APIRouter, Depends

from ..auth import create_session_id
from ..db import create_session, list_sessions_for_user
from ..deps import get_current_user
from ..models import SessionCreateResponse, SessionListResponse, SessionSummary

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionCreateResponse)
def create_new_session(current_user=Depends(get_current_user)):
    session_id = create_session_id()
    create_session(session_id, current_user["user_id"])
    return SessionCreateResponse(session_id=session_id)


@router.get("/", response_model=SessionListResponse)
def get_sessions(current_user=Depends(get_current_user)):
    sessions = list_sessions_for_user(current_user["user_id"])
    summaries = [SessionSummary(session_id=s["session_id"]) for s in sessions]
    return SessionListResponse(sessions=summaries)
