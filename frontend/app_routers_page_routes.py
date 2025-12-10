"""
Page Routes - Serves Jinja2 HTML templates
Calls the ML Service API for agent queries.

PUT THIS FILE IN: app/routers/page_routes.py
"""

import os
import httpx
from fastapi import APIRouter, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Your existing imports - adjust paths if needed
from app.auth import authenticate_user, create_access_token, get_password_hash, decode_access_token
from app.db import (
    create_user, 
    find_user_by_username, 
    find_user_by_id,
    create_session as db_create_session,
    list_sessions_for_user,
    get_session,
    add_message_to_session,
    add_file_to_session
)
from app.config import get_settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")
settings = get_settings()

# ML Service URL (your service/main.py runs on port 8001)
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001")


# ============================================
# Call ML Service API
# ============================================
async def query_ml_agent(message: str) -> str:
    """Call the ML service API to get a response."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{ML_SERVICE_URL}/query",
                json={"query": message}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("final_explanation", "No response generated.")
            else:
                return f"Error from ML service: {response.status_code}"
                
    except httpx.TimeoutException:
        return "The request timed out. Please try again."
    except httpx.ConnectError:
        return "Could not connect to the ML service. Please ensure it's running."
    except Exception as e:
        return f"An error occurred: {str(e)}"


# ============================================
# Auth Helper
# ============================================
def get_current_user_from_cookie(request: Request):
    """Get current user from session cookie."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id:
            return find_user_by_id(user_id)
    except Exception:
        pass
    return None


# ============================================
# Home Page
# ============================================
@router.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    current_user = get_current_user_from_cookie(request)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
    })


# ============================================
# Auth Pages
# ============================================
@router.get("/login", response_class=HTMLResponse, name="login_page")
async def login_page(request: Request):
    current_user = get_current_user_from_cookie(request)
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "current_user": None,
    })


@router.post("/login", name="login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Process login form."""
    try:
        user = authenticate_user(username, password)
        access_token = create_access_token(data={"sub": user.id})
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            "access_token", 
            access_token, 
            httponly=True,
            max_age=settings.access_token_expire_minutes * 60
        )
        return response
    except ValueError:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Incorrect username or password",
            "username": username,
            "current_user": None,
        })


@router.get("/register", response_class=HTMLResponse, name="register_page")
async def register_page(request: Request):
    current_user = get_current_user_from_cookie(request)
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "current_user": None,
    })


@router.post("/register", name="register")
async def register(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Process registration form."""
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Passwords do not match",
            "username": username,
            "current_user": None,
        })
    
    existing = find_user_by_username(username)
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Username already taken",
            "username": username,
            "current_user": None,
        })
    
    password_hash = get_password_hash(password)
    created = create_user(username, password_hash)
    
    access_token = create_access_token(data={"sub": str(created.inserted_id)})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        "access_token", 
        access_token, 
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60
    )
    return response


@router.post("/logout", name="logout")
async def logout():
    """Log out user."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response


# ============================================
# Dashboard
# ============================================
@router.get("/dashboard", response_class=HTMLResponse, name="dashboard")
async def dashboard(request: Request):
    current_user = get_current_user_from_cookie(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    sessions_data = list_sessions_for_user(current_user.id)
    sessions = []
    for s in sessions_data:
        preview = ""
        if s.get("messages"):
            last_msg = s["messages"][-1]
            preview = last_msg.get("message", "")[:50] + "..."
        
        sessions.append({
            "session_id": s["session_id"],
            "title": s.get("title"),
            "date": s.get("created_at").strftime("%b %d, %Y") if s.get("created_at") else "Today",
            "preview": preview
        })
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": current_user,
        "active_page": "dashboard",
        "sessions": sessions,
    })


@router.post("/sessions/create", name="create_session")
async def create_new_session(request: Request, redirect_to_chat: str = Form(None)):
    """Create a new chat session."""
    current_user = get_current_user_from_cookie(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    import uuid
    session_id = str(uuid.uuid4())
    db_create_session(session_id, current_user.id)
    
    if redirect_to_chat:
        return RedirectResponse(url=f"/chat?session_id={session_id}", status_code=302)
    return RedirectResponse(url="/dashboard", status_code=302)


# ============================================
# Chat Page
# ============================================
@router.get("/chat", response_class=HTMLResponse, name="chat_page")
async def chat_page(request: Request, session_id: str = None):
    current_user = get_current_user_from_cookie(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get sessions for sidebar
    sessions_data = list_sessions_for_user(current_user.id)
    sessions = []
    for s in sessions_data:
        sessions.append({
            "session_id": s["session_id"],
            "title": s.get("title"),
            "date": s.get("created_at").strftime("%b %d") if s.get("created_at") else "Today",
        })
    
    # Create session if needed
    if not session_id:
        if sessions:
            session_id = sessions[0]["session_id"]
        else:
            import uuid
            session_id = str(uuid.uuid4())
            db_create_session(session_id, current_user.id)
            sessions = [{"session_id": session_id, "title": None, "date": "Today"}]
    
    # Get messages
    session_data = get_session(session_id, current_user.id)
    messages = []
    if session_data and session_data.get("messages"):
        for m in session_data["messages"]:
            timestamp = ""
            if m.get("timestamp"):
                timestamp = m["timestamp"].strftime("%I:%M %p")
            messages.append({
                "role": m["role"],
                "message": m["message"],
                "timestamp": timestamp
            })
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "current_user": current_user,
        "active_page": "chat",
        "sessions": sessions,
        "current_session_id": session_id,
        "messages": messages,
    })


@router.post("/chat/send", name="send_message")
async def send_message(request: Request, session_id: str = Form(...), message: str = Form(...)):
    """Send a chat message and get AI response."""
    current_user = get_current_user_from_cookie(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    session = get_session(session_id, current_user.id)
    if not session:
        return RedirectResponse(url="/dashboard", status_code=302)
    
    # Save user message
    add_message_to_session(session_id, "user", message)
    
    # Call ML Service API
    ai_response = await query_ml_agent(message)
    
    # Save AI response
    add_message_to_session(session_id, "assistant", ai_response)
    
    return RedirectResponse(url=f"/chat?session_id={session_id}", status_code=302)


# ============================================
# Upload Page
# ============================================
@router.get("/upload", response_class=HTMLResponse, name="upload_page")
async def upload_page(request: Request, session_id: str = None):
    current_user = get_current_user_from_cookie(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    uploaded_files = []
    if session_id:
        session = get_session(session_id, current_user.id)
        if session:
            uploaded_files = session.get("files", [])
    
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "current_user": current_user,
        "active_page": "upload",
        "session_id": session_id or "",
        "uploaded_files": uploaded_files,
    })


@router.post("/upload", name="upload_file")
async def upload_file_handler(
    request: Request,
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """Handle file upload."""
    current_user = get_current_user_from_cookie(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    filename = f"{session_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    
    add_file_to_session(session_id, file.filename, filepath)
    
    session = get_session(session_id, current_user.id)
    uploaded_files = session.get("files", []) if session else []
    
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "current_user": current_user,
        "active_page": "upload",
        "session_id": session_id,
        "success": f"Successfully uploaded: {file.filename}",
        "uploaded_files": uploaded_files,
    })
