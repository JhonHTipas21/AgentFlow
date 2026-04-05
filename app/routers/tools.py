"""
AgentFlow Tools Router
Endpoints for viewing available tools.
"""
from fastapi import APIRouter
from typing import List

from app import schemas
from app.tools import AVAILABLE_TOOLS

router = APIRouter()


@router.get("/", response_model=List[schemas.ToolInfo])
def list_tools():
    """
    List all available tools in the registry.

    These tools can be assigned to agents during creation or update.
    """
    return [
        schemas.ToolInfo(
            name=tool.name,
            description=tool.description,
            category=tool.category,
        )
        for tool in AVAILABLE_TOOLS.values()
    ]


@router.get("/{tool_name}")
def get_tool_details(tool_name: str):
    """Get detailed information about a specific tool."""
    tool = AVAILABLE_TOOLS.get(tool_name)
    if not tool:
        return {"error": f"Tool '{tool_name}' not found"}
    return tool.to_dict()
