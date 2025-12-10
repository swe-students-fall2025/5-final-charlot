from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.routers.auth_routes import router as auth_router

# from .routers.session_routes import router as session_router
from .routers.chat_routes import router as chat_router
# from .routers.upload_routes import router as upload_router


def create_app():
    app = FastAPI(title="Legal Chatbot Backend")

    templates = Jinja2Templates(directory="templates")

    chat_messages = []

    app.include_router(auth_router)
    # app.include_router(session_router)
    app.include_router(chat_router)
    # app.include_router(upload_router)

    @app.get("/", response_class=HTMLResponse)
    async def get_chat_page(request: Request):
        return templates.TemplateResponse("chat.html", {"request": request, "messages": chat_messages})

    @app.post("/chat")
    async def post_message(request: Request, user_message: str = Form(...)):
        chat_messages.append({"sender": "You", "text": user_message})

        bot_response = f"Echo: {user_message}"
        chat_messages.append({"sender": "Bot", "text": bot_response})

        return RedirectResponse("/", status_code=303)

    return app
