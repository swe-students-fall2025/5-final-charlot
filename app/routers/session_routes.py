"""Routes to manage sessions"""

from app.db import create_session
from flask import Blueprint
from flask_login import current_user, login_required

session_bp = Blueprint("session", __name__, url_prefix="/session")


@session_bp.route("/create", methods=["POST"])
@login_required
def create_new_session():
    """Create new chat session for currently logged in user"""

    res = create_session(current_user.id)

    return f"Session created: {str(res.inserted_id)}"


# @router.get("/", response_model=SessionListResponse)
# def get_sessions(current_user=Depends(get_current_user)):
#     sessions = list_sessions_for_user(current_user["user_id"])
#     summaries = [SessionSummary(session_id=s["session_id"]) for s in sessions]
#     return SessionListResponse(sessions=summaries)
