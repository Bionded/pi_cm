from core.plugin_base import BasePlugin
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
import os
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from queue import Queue
import urllib.parse

class Plugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "Log Viewer"
        self.icon = ""  # Nerd Font code for log icon
        self.description = "View logs in real-time."
        self.version = "1.0"
        self.author = "Your Name"
        self.enabled = True
        self.position = 2
        # Define allowed log directories and excluded files
        self.ALLOWED_LOG_DIRS = ["/var/log", "/home/ykovrigin/logs"]
        self.EXCLUDED_FILES = ["/var/log/secure", "/var/log/auth.log"]

    def is_allowed_file(self, file_path):
        real_path = os.path.realpath(file_path)
        for allowed_dir in self.ALLOWED_LOG_DIRS:
            if real_path.startswith(os.path.realpath(allowed_dir)):
                if real_path not in self.EXCLUDED_FILES:
                    return True
        return False

    def register_routes(self):
        @self.router.get("/logs")
        async def list_logs():
            log_files = []
            for log_dir in self.ALLOWED_LOG_DIRS:
                for root, dirs, files in os.walk(log_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self.is_allowed_file(file_path):
                            log_files.append(file_path)
            return {"log_files": log_files}

        @self.router.websocket("/ws/logs")
        async def websocket_log_stream(websocket: WebSocket):
            await websocket.accept()
            try:
                data = await websocket.receive_text()
                log_file = urllib.parse.unquote(data)

                if not self.is_allowed_file(log_file):
                    await websocket.close(code=1008)
                    raise HTTPException(status_code=403, detail="Access to this file is forbidden.")

                await self.tail_log_file(log_file, websocket)

            except WebSocketDisconnect:
                print("Client disconnected from log viewer websocket.")
            except Exception as e:
                print(f"Error: {e}")
                await websocket.close(code=1011)

    async def tail_log_file(self, log_file, websocket):
        loop = asyncio.get_event_loop()
        q = Queue()

        class TailHandler(FileSystemEventHandler):
            def __init__(self, file_path):
                self.file_path = file_path
                self.file = open(self.file_path, 'r')
                self.file.seek(0, os.SEEK_END)

            def on_modified(self, event):
                if event.src_path == self.file_path:
                    line = self.file.readline()
                    if line:
                        q.put(line)

            def on_deleted(self, event):
                if event.src_path == self.file_path:
                    q.put(None)

        event_handler = TailHandler(log_file)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(log_file), recursive=False)
        observer.start()

        try:
            while True:
                if not q.empty():
                    line = q.get()
                    if line is None:
                        await websocket.send_text("Log file deleted.")
                        break
                    await websocket.send_text(line)
                await asyncio.sleep(0.1)
        finally:
            observer.stop()
            observer.join()
            event_handler.file.close()
