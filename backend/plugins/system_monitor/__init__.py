# backend/plugins/system_monitor/__init__.py

from core.plugin_base import BasePlugin
from fastapi import WebSocket, WebSocketDisconnect
import psutil
import asyncio

class Plugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "System Monitor"
        self.icon = ""  # Nerd Font code for system monitor icon
        self.description = "Monitor CPU, memory, disk, and network usage."
        self.version = "1.0"
        self.author = "Your Name"
        self.enabled = True
        self.position = 1  # Set default position

    def register_routes(self):
        @self.router.get("/metrics")
        async def get_metrics():
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()

            metrics = {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'used': memory.used,
                    'available': memory.available,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            }

            return metrics

        @self.router.websocket("/ws/metrics")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            try:
                while True:
                    cpu_percent = psutil.cpu_percent(interval=None)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    net_io = psutil.net_io_counters()

                    metrics = {
                        'cpu_percent': cpu_percent,
                        'memory': {
                            'total': memory.total,
                            'used': memory.used,
                            'available': memory.available,
                            'percent': memory.percent
                        },
                        'disk': {
                            'total': disk.total,
                            'used': disk.used,
                            'free': disk.free,
                            'percent': disk.percent
                        },
                        'network': {
                            'bytes_sent': net_io.bytes_sent,
                            'bytes_recv': net_io.bytes_recv,
                            'packets_sent': net_io.packets_sent,
                            'packets_recv': net_io.packets_recv
                        }
                    }

                    await websocket.send_json(metrics)
                    await asyncio.sleep(1)
            except WebSocketDisconnect:
                print("Client disconnected from system_monitor websocket.")
