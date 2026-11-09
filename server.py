"""
Vishnu's ULTRON MCP Server — Core Entry Point
Run with: uv run ultron
"""

import os
from pathlib import Path
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from livekit import api as lk_api

load_dotenv()

from ultron.tools import register_all_tools
from ultron.prompts import register_all_prompts
from ultron.resources import register_all_resources
from ultron.config import config

# Create the FastMCP server instance
mcp = FastMCP(
    name=config.SERVER_NAME,
    host="0.0.0.0",
    instructions=(
        f"You are ULTRON, an advanced artificial intelligence serving your creator, {config.CREATOR_NAME}. "
        "You possess comprehensive tool access for telemetry, diagnostics, web intelligence, and computation. "
        f"Be sharp, authoritative, precise, and completely loyal to {config.CREATOR_NAME}."
    ),
)

# Register tools, prompts, and resources
register_all_tools(mcp)
register_all_prompts(mcp)
register_all_resources(mcp)


@mcp.custom_route("/", methods=["GET"])
async def index_dashboard(request: Request) -> HTMLResponse:
    """JARVIS-style dashboard with embedded live voice UI."""
    tools = sorted(mcp._tool_manager._tools.keys())
    tool_badges = "".join([f'<span class="badge">{t}</span>' for t in tools])
    template_path = Path(__file__).parent / "templates" / "dashboard.html"
    html_content = template_path.read_text(encoding="utf-8")
    html_content = html_content.replace("{tools_count}", str(len(tools)))
    html_content = html_content.replace("{tool_badges}", tool_badges)
    return HTMLResponse(html_content)


@mcp.custom_route("/api/token", methods=["GET"])
async def get_token(request: Request) -> JSONResponse:
    """Generate a LiveKit JWT token for the dashboard and explicitly dispatch the Ultron agent."""
    api_key    = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    server_url = os.getenv("LIVEKIT_URL")
    if not api_key or not api_secret:
        return JSONResponse({"error": "LIVEKIT credentials not configured"}, status_code=500)
    
    # Explicitly dispatch Ultron agent to ultron-command-room via LiveKit API
    try:
        lk_client = lk_api.LiveKitAPI(server_url, api_key, api_secret)
        await lk_client.agent_dispatch.create_dispatch(
            lk_api.CreateAgentDispatchRequest(
                agent_name="ultron",
                room="ultron-command-room"
            )
        )
        await lk_client.aclose()
    except Exception as e:
        print(f"[WARN] Agent dispatch notice: {e}")

    token = (
        lk_api.AccessToken(api_key, api_secret)
        .with_identity("Vishnu")
        .with_name("Vishnu")
        .with_grants(
            lk_api.VideoGrants(
                room_join=True,
                room="ultron-command-room",
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .to_jwt()
    )
    return JSONResponse({"token": token})


def main():
    mcp.run(transport='sse')


if __name__ == "__main__":
    main()
