# tests/test_plugins.py

import pytest
from httpx import AsyncClient
import os

# Ensure plugins are loaded
os.environ["LOAD_PLUGINS"] = "true"

from main import app

@pytest.mark.anyio
async def test_list_plugins():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/plugins")
    assert response.status_code == 200
    json_data = response.json()
    assert "plugins" in json_data
    assert isinstance(json_data["plugins"], list)
    # Optionally, check that the plugins are as expected
    plugin_ids = [plugin["id"] for plugin in json_data["plugins"]]
    expected_plugins = ["system_monitor", "log_viewer", "service_manager", "command_executor", "datetime_display"]
    for plugin_id in expected_plugins:
        assert plugin_id in plugin_ids

@pytest.mark.anyio
async def test_system_monitor_metrics():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/plugins/system_monitor/metrics")
    assert response.status_code == 200
    json_data = response.json()
    assert "cpu_percent" in json_data

@pytest.mark.anyio
async def test_log_viewer_logs():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/plugins/log_viewer/logs")
    assert response.status_code == 200
    json_data = response.json()
    assert "log_files" in json_data

@pytest.mark.anyio
async def test_service_manager_services():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/plugins/service_manager/services")
    assert response.status_code == 200
    json_data = response.json()
    assert "services" in json_data

@pytest.mark.anyio
async def test_command_executor_commands():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/plugins/command_executor/commands")
    assert response.status_code == 200
    json_data = response.json()
    assert "commands" in json_data

@pytest.mark.anyio
async def test_datetime_display_current_datetime():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/plugins/datetime_display/current_datetime")
    assert response.status_code == 200
    json_data = response.json()
    assert "current_datetime" in json_data
