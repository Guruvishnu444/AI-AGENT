"""
Vishnu's ULTRON Tool Registry
Registers all operational tool modules with the MCP server.
"""

from ultron.tools import web, system, utils


def register_all_tools(mcp):
    """Register all tool groups onto the FastMCP server instance."""
    web.register(mcp)
    system.register(mcp)
    utils.register(mcp)
