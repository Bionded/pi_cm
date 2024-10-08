import os
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from core.plugin_manager import PluginManager

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check environment variable to decide whether to load plugins
LOAD_PLUGINS = os.getenv("LOAD_PLUGINS", "true").lower() == "true"

if LOAD_PLUGINS:
    # Initialize the plugin manager with the app
    plugin_manager = PluginManager(app)
else:
    plugin_manager = None  # Plugins are not loaded

@app.get("/")
async def root():
    return {"message": "Backend is running"}

@app.get("/plugins")
async def list_plugins():
    plugins_info = []
    for plugin_name, plugin in plugin_manager.plugins.items():
        plugins_info.append({
            "id": plugin_name,
            "name": plugin.name,
            "icon": plugin.icon,
            "description": plugin.description,
            "version": plugin.version,
            "author": plugin.author,
            "enabled": plugin.enabled,
            "position": plugin.position,
        })
    return {"plugins": plugins_info}

@app.post("/plugins/{plugin_id}/enable")
async def enable_plugin(plugin_id: str):
    success = plugin_manager.enable_plugin(plugin_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found.")
    return {"status": f"Plugin '{plugin_id}' has been enabled."}

@app.post("/plugins/{plugin_id}/disable")
async def disable_plugin(plugin_id: str):
    success = plugin_manager.disable_plugin(plugin_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found.")
    return {"status": f"Plugin '{plugin_id}' has been disabled."}

@app.post("/plugins/{plugin_id}/position/{position}")
async def set_plugin_position(plugin_id: str, position: int):
    success = plugin_manager.set_plugin_position(plugin_id, position)
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found.")
    return {"status": f"Plugin '{plugin_id}' position set to {position}."}

@app.post("/plugins/{plugin_id}/update")
async def update_plugin(plugin_id: str, data: dict = Body(...)):
    allowed_attrs = ['name', 'icon', 'description', 'version', 'author', 'enabled', 'position']
    success = False
    for attr, value in data.items():
        if attr in allowed_attrs:
            success = plugin_manager.update_plugin_attribute(plugin_id, attr, value)
        else:
            raise HTTPException(status_code=400, detail=f"Attribute '{attr}' is not allowed.")
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found.")
    return {"status": f"Plugin '{plugin_id}' updated successfully."}
