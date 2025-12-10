"""Direct app import"""

from pathlib import Path

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.routers.auth_routes import router as auth_router
from app.routers.chat_routes import router as chat_router
from app.deps import logged_in
from app.db import list_sessions_for_user

# Get the directory where this file lives
BASE_DIR = Path(__file__).resolve().parent


def create_app():
    """Create fastAPI app instance"""

    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
    app = FastAPI(title="Legal Chatbot Backend")

    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    app.include_router(auth_router)
    app.include_router(chat_router)

    @app.get("/")
    def root(request: Request, current_user=Depends(logged_in)):
        return templates.TemplateResponse(request, "index.html", {"current_user": current_user})

    @app.get("/dashboard")
    def dashboard(request: Request, current_user=Depends(logged_in)):
        """Get a list of all chat sessions for the user"""

        if not current_user:
            return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

        sessions = list_sessions_for_user(current_user.id)
        return templates.TemplateResponse(
            request, "dashboard.html", {"current_user": current_user, "sessions": sessions}
        )

    @app.get("/upload")
    def upload_page(request: Request, current_user=Depends(logged_in)):
        """Get a list of all chat sessions for the user"""

        if not current_user:
            return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

        return templates.TemplateResponse(request, "upload.html", {"current_user": current_user})

    return app
