# tests/test_main.py

import pytest
from httpx import AsyncClient
import os

# Set the environment variable to prevent loading plugins
os.environ["LOAD_PLUGINS"] = "false"

from main import app  # Import after setting the environment variable

@pytest.mark.anyio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend is running"}

@pytest.mark.anyio
async def test_plugins_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/plugins")
    assert response.status_code == 404  # Since plugins are not loaded
