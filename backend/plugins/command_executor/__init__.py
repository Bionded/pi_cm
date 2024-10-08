# backend/plugins/command_executor/__init__.py

from core.plugin_base import BasePlugin
from fastapi import HTTPException, BackgroundTasks
import subprocess
import asyncio
import datetime
import uuid
from typing import Dict, List

class Plugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "Command Executor"
        self.icon = ""  # Nerd Font code for terminal icon
        self.description = "Execute predefined shell commands."
        self.version = "1.0"
        self.author = "Your Name"
        self.enabled = True
        self.position = 4
        # Define allowed commands
        self.ALLOWED_COMMANDS = {
            "update_system": {
                "command": ["sudo", "apt-get", "update"],
                "description": "Update the system package list"
            },
            "upgrade_system": {
                "command": ["sudo", "apt-get", "upgrade", "-y"],
                "description": "Upgrade all packages to the newest version"
            },
            "reboot_system": {
                "command": ["sudo", "reboot"],
                "description": "Reboot the system"
            },
        }
        # Command statuses
        self.command_statuses: Dict[str, Dict] = {}

    def register_routes(self):
        @self.router.get("/commands")
        async def list_commands():
            commands = []
            for key, value in self.ALLOWED_COMMANDS.items():
                commands.append({
                    "key": key,
                    "description": value["description"]
                })
            return {"commands": commands}

        @self.router.post("/commands/{command_key}")
        async def execute_command(command_key: str, background_tasks: BackgroundTasks):
            if command_key not in self.ALLOWED_COMMANDS:
                raise HTTPException(status_code=400, detail="Invalid command.")

            command_info = self.ALLOWED_COMMANDS[command_key]
            command = command_info["command"]

            task_id = str(uuid.uuid4())
            self.command_statuses[task_id] = {
                "status": "pending",
                "command_key": command_key,
                "started_at": datetime.datetime.utcnow().isoformat(),
                "completed_at": None,
                "success": None,
                "error": None
            }

            background_tasks.add_task(self.run_command, task_id, command)

            return {"task_id": task_id, "status": "Command execution started."}

        @self.router.get("/commands/status/{task_id}")
        async def get_command_status(task_id: str):
            status = self.command_statuses.get(task_id)
            if not status:
                raise HTTPException(status_code=404, detail="Task ID not found.")
            return status

    async def run_command(self, task_id: str, command: List[str]):
        try:
            self.command_statuses[task_id]["status"] = "running"

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await process.communicate()

            if process.returncode == 0:
                self.command_statuses[task_id]["status"] = "completed"
                self.command_statuses[task_id]["success"] = True
            else:
                self.command_statuses[task_id]["status"] = "failed"
                self.command_statuses[task_id]["success"] = False
                self.command_statuses[task_id]["error"] = f"Return code: {process.returncode}"
        except Exception as e:
            self.command_statuses[task_id]["status"] = "failed"
            self.command_statuses[task_id]["success"] = False
            self.command_statuses[task_id]["error"] = str(e)
        finally:
            self.command_statuses[task_id]["completed_at"] = datetime.datetime.utcnow().isoformat()
