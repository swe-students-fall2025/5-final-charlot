import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from ..db import add_file_to_session, get_session
from ..deps import get_current_user

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    session = get_session(session_id, user_id=current_user["user_id"])
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    filename = f"{session_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    add_file_to_session(session_id, file.filename, filepath)
    return {"session_id": session_id, "filename": file.filename, "path": filepath}
