from fastapi import APIRouter

router = APIRouter()

@router.get("/info")
async def plugin_info():
    return {
        "name": "Sample Plugin",
        "icon": "",  # Nerd Font icon code
        "description": "This is a sample plugin."
    }