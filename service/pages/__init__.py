"""
Gradio page modules
Each module creates a separate page mounted at different routes
"""

from .home import create_home_page
from .dashboard import create_dashboard_page
from .chat import create_chat_page
from .upload import create_upload_page

__all__ = [
    "create_home_page",
    "create_dashboard_page",
    "create_chat_page",
    "create_upload_page"
]
