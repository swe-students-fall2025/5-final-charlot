"""Direct app import"""

from fastapi import FastAPI

from app.routers.auth_routes import router as auth_router

# from .routers.session_routes import router as session_router
# from .routers.chat_routes import router as chat_router
# from .routers.upload_routes import router as upload_router


def create_app():
    """Create fastAPI app instance"""

    app = FastAPI(title="Legal Chatbot Backend")

    app.include_router(auth_router)
    # app.include_router(session_router)
    # app.include_router(chat_router)
    # app.include_router(upload_router)

    @app.get("/")
    def root():
        return "LANDING PAGE"

    return app
