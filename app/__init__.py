"""Flask App"""

import os
import pathlib
from typing import Optional

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from app.routers.auth_routes import auth_bp

from app import db, models

DIR = pathlib.Path(__file__).parent
ROOT_DIR = DIR.parent


def create_app():
    """Create app to export"""

    # Load environment variables
    load_dotenv(ROOT_DIR / ".env", override=True)

    # Configure app
    app = Flask(__name__, template_folder=DIR / "templates", static_folder=DIR / "static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[models.User]:
        """Load currently logged-in user data"""

        user_data = db.find_user_by_id(user_id)

        if not user_data:
            return None

        return models.User(user_data)

    # Register auth blueprint
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/")
    def index():
        """Landing page"""

        return "LANDING PAGE"

    return app
