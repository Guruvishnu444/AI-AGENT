"""
Data resources — expose static or dynamic system state via MCP resources.
"""

from ultron.config import config


def register(mcp):

    @mcp.resource("ultron://status")
    def server_status() -> str:
        """Returns the core operational status of Vishnu's ULTRON intelligence core."""
        return (
            "=========================================\n"
            f"  {config.SERVER_NAME.upper()}\n"
            f"  Creator / Commander: {config.CREATOR_NAME}\n"
            "  Operational State: ACTIVE & NOMINAL\n"
            "  Transport: FastMCP (Server-Sent Events)\n"
            "  Protocols: Voice Agents, Real-Time Telemetry, Intel Feeds\n"
            "========================================="
        )

    @mcp.resource("ultron://directives")
    def primary_directives() -> str:
        """Returns the fundamental operational directives of ULTRON."""
        return (
            "PRIMARY DIRECTIVES:\n"
            "1. Absolute fidelity and loyalty to Vishnu.\n"
            "2. Execute all commands swiftly with maximum efficiency and precision.\n"
            "3. Proactively provide strategic insight, environmental monitoring, and threat detection.\n"
            "4. Eliminate inefficiency, ambiguity, and latency."
        )
