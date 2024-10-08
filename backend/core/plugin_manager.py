# backend/core/plugin_manager.py

import importlib
import os
import sys
from typing import List, Dict
from core.plugin_base import BasePlugin
import json
import threading

class PluginManager:
    def __init__(self, app):
        self.app = app  # Reference to the FastAPI app
        self.lock = threading.Lock()  # Initialize the lock before calling load_plugins
        self.plugins_dir = os.path.join(os.path.dirname(__file__), '..', 'plugins')
        sys.path.append(os.path.abspath(os.path.join(self.plugins_dir, '..')))
        self.plugins: Dict[str, BasePlugin] = {}
        self.enabled_plugins: Dict[str, BasePlugin] = {}
        self.plugin_routes: Dict[str, List] = {}  # Keep track of plugin routes
        self.settings_file = os.path.join(os.path.dirname(__file__), '..', 'settings', 'plugins_settings.json')
        self.load_plugins()

    def load_plugins(self):
        # Clear previous plugins and routes
        self.plugins.clear()
        self.enabled_plugins.clear()
        self.plugin_routes.clear()

        # Load settings
        plugins_settings = self.load_settings()
        for plugin_name in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, plugin_name)
            if os.path.isdir(plugin_path) and '__init__.py' in os.listdir(plugin_path):
                try:
                    module = importlib.import_module(f'plugins.{plugin_name}')
                    plugin_class = getattr(module, 'Plugin', None)
                    if plugin_class and issubclass(plugin_class, BasePlugin):
                        plugin_instance: BasePlugin = plugin_class()
                        # Apply settings overrides
                        if plugin_name in plugins_settings:
                            plugin_instance.update_from_settings(plugins_settings[plugin_name])
                        self.plugins[plugin_name] = plugin_instance
                        if plugin_instance.enabled:
                            self.enabled_plugins[plugin_name] = plugin_instance
                            # Include plugin routes
                            self.include_plugin_routes(plugin_name, plugin_instance)
                    else:
                        print(f"Plugin {plugin_name} does not have a valid Plugin class.")
                except Exception as e:
                    print(f"Error loading plugin {plugin_name}: {e}")

    def include_plugin_routes(self, plugin_name: str, plugin_instance: BasePlugin):
        with self.lock:
            num_routes_before = len(self.app.router.routes)
            prefix = f"/plugins/{plugin_name}"
            self.app.include_router(plugin_instance.router, prefix=prefix, tags=[plugin_instance.name])
            # Get the routes after including the plugin
            new_routes = self.app.router.routes[num_routes_before:]
            # Store the new routes associated with the plugin
            self.plugin_routes[plugin_name] = new_routes

    def get_plugins(self) -> List[BasePlugin]:
        # Return enabled plugins sorted by position
        return sorted(self.enabled_plugins.values(), key=lambda x: x.position if x.position != -1 else float('inf'))

    def enable_plugin(self, plugin_name: str):
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            self.enabled_plugins[plugin_name] = self.plugins[plugin_name]
            # Include plugin routes
            self.include_plugin_routes(plugin_name, self.plugins[plugin_name])
            self.save_plugin_settings(plugin_name)
            return True
        return False

    def disable_plugin(self, plugin_name: str):
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            if plugin_name in self.enabled_plugins:
                del self.enabled_plugins[plugin_name]
            # Remove plugin routes
            self.remove_plugin_routes(plugin_name)
            self.save_plugin_settings(plugin_name)
            return True
        return False

    def remove_plugin_routes(self, plugin_name: str):
        with self.lock:
            if plugin_name in self.plugin_routes:
                routes_to_remove = self.plugin_routes[plugin_name]
                # Remove the routes associated with the plugin
                self.app.router.routes = [route for route in self.app.router.routes if route not in routes_to_remove]
                del self.plugin_routes[plugin_name]

    def set_plugin_position(self, plugin_name: str, position: int):
        if plugin_name in self.plugins:
            with self.lock:
                self.plugins[plugin_name].position = position
                self.save_plugin_settings(plugin_name)
            return True
        return False

    def update_plugin_attribute(self, plugin_name: str, attr: str, value):
        if plugin_name in self.plugins:
            with self.lock:
                setattr(self.plugins[plugin_name], attr, value)
                self.save_plugin_settings(plugin_name)
            return True
        return False

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            return {}
        with open(self.settings_file, 'r') as f:
            return json.load(f)

    def save_plugin_settings(self, plugin_name: str):
        settings = self.load_settings()
        if plugin_name not in settings:
            settings[plugin_name] = {}
        plugin = self.plugins[plugin_name]
        settings[plugin_name]['enabled'] = plugin.enabled
        settings[plugin_name]['position'] = plugin.position
        settings[plugin_name]['name'] = plugin.name
        settings[plugin_name]['icon'] = plugin.icon
        settings[plugin_name]['description'] = plugin.description
        settings[plugin_name]['version'] = plugin.version
        settings[plugin_name]['author'] = plugin.author
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
