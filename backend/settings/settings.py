import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "background_color": "#FFFFFF",
            "opacity": 1.0,
            "plugins": {}
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default_settings, f)
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)