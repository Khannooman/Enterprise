from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.constants.route_paths import RoutePaths
from app.constants.route_tags import RouteTags
from threading import Lock
import os

class HealthRouter:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:  # Double-checked locking
                    cls._instance = super(HealthRouter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "router"):  # Prevents reinitialization
            self.router = APIRouter()
            self.setup_routes()

    def setup_routes(self):
        @self.router.get(RoutePaths.ROOT, tags=[RouteTags.PING])
        @self.router.get(RoutePaths.PING, tags=[RouteTags.PING])
        async def ping():
            # Serve the chatbot UI HTML
            return HTMLResponse(content=self.get_chatbot_ui_html())

    def get_chatbot_ui_html(self):
        """Loads the chatbot UI HTML from a file."""
        try:
            with open("app/templates/chatbot_ui.html", "r") as file:
                return file.read()
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Chatbot UI template not found.")