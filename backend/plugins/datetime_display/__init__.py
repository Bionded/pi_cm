# backend/plugins/datetime_display/__init__.py

from core.plugin_base import BasePlugin
from fastapi import WebSocket, WebSocketDisconnect
import datetime
import asyncio

class Plugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "Date & Time"
        self.icon = ""  # Nerd Font code for clock icon
        self.description = "Display current date and time."
        self.version = "1.0"
        self.author = "Your Name"
        self.enabled = True
        self.position = 5

    def register_routes(self):
        @self.router.websocket("/ws/datetime")
        async def datetime_websocket(websocket: WebSocket):
            await websocket.accept()
            try:
                while True:
                    now = datetime.datetime.now()
                    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
                    await websocket.send_text(datetime_str)
                    await asyncio.sleep(1)
            except WebSocketDisconnect:
                print("Client disconnected from datetime websocket.")

        @self.router.get("/current_datetime")
        async def get_current_datetime():
            now = datetime.datetime.now()
            datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
            return {"current_datetime": datetime_str}
