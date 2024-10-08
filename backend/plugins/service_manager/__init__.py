# backend/plugins/service_manager/__init__.py

from core.plugin_base import BasePlugin
from fastapi import HTTPException
import subprocess
import re

class Plugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "Service Manager"
        self.icon = ""  # Nerd Font code for service icon
        self.description = "Manage system services."
        self.version = "1.0"
        self.author = "Your Name"
        self.enabled = True
        self.position = 3
        self.EXCLUDED_SERVICES = ["ssh", "networking"]

    def is_valid_service_name(self, service_name):
        pattern = r'^[a-zA-Z0-9_\-\.@]+$'
        return re.match(pattern, service_name) is not None

    def is_service_excluded(self, service_name):
        return service_name in self.EXCLUDED_SERVICES

    def register_routes(self):
        @self.router.get("/services")
        async def list_services():
            try:
                result = subprocess.run(
                    ["systemctl", "list-units", "--type=service", "--all", "--no-pager", "--no-legend"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                services = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        service_name = parts[0]
                        service_load = parts[1]
                        service_active = parts[2]
                        service_sub = parts[3]
                        service_description = ' '.join(parts[4:])
                        if not self.is_service_excluded(service_name):
                            services.append({
                                "name": service_name,
                                "load": service_load,
                                "active": service_active,
                                "sub": service_sub,
                                "description": service_description
                            })
                return {"services": services}
            except subprocess.CalledProcessError as e:
                raise HTTPException(status_code=500, detail="Failed to list services.")

        @self.router.post("/services/{service_name}/{action}")
        async def control_service(service_name: str, action: str):
            if not self.is_valid_service_name(service_name):
                raise HTTPException(status_code=400, detail="Invalid service name.")

            if self.is_service_excluded(service_name):
                raise HTTPException(status_code=403, detail="Control of this service is not allowed.")

            if action not in ["start", "stop", "restart"]:
                raise HTTPException(status_code=400, detail="Invalid action.")

            try:
                subprocess.run(
                    ["sudo", "systemctl", action, service_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                return {"status": f"Service {service_name} {action}ed successfully."}
            except subprocess.CalledProcessError as e:
                raise HTTPException(status_code=500, detail=f"Failed to {action} service {service_name}.")
