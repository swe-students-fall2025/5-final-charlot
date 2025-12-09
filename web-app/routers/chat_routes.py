from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from ..deps import get_current_user
from ..db import add_message_to_session, get_session
from ..models import ChatRequest, ChatResponse, Message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, current_user=Depends(get_current_user)):
    session = get_session(request.session_id, user_id=current_user["user_id"])
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Save user message
    add_message_to_session(request.session_id, "user", request.message)

    # TODO: call Hyu's ML client here later.
    ai_text = f"(Dummy response) You said: {request.message}"
    add_message_to_session(request.session_id, "ai", ai_text)

    updated_session = get_session(request.session_id, user_id=current_user["user_id"])
    messages = [
        Message(
            role=m["role"],
            message=m["message"],
            timestamp=m["timestamp"].isoformat(),
        )
        for m in updated_session.get("messages", [])
    ]

    return ChatResponse(session_id=request.session_id, messages=messages)
