# backend/core/plugin_base.py

from fastapi import APIRouter

class BasePlugin:
    def __init__(self):
        self.name = "Unnamed Plugin"
        self.icon = ""  # Default icon (Nerd Font code)
        self.description = "No description provided."
        self.version = "0.1"
        self.author = "Unknown"
        self.enabled = True
        self.position = -1  # Default position
        self.router = APIRouter()

        # Register routes when the plugin is initialized
        self.register_routes()

    def register_routes(self):
        # Method to be overridden by plugins to register their routes
        pass

    def update_from_settings(self, settings: dict):
        # Update plugin parameters from settings if they exist
        for attr in ['name', 'icon', 'description', 'version', 'author', 'enabled', 'position']:
            if attr in settings:
                setattr(self, attr, settings[attr])
