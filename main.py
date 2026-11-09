"""
=============================================================================
                          VISHNU'S ULTRON
         Autonomous Private Voice AI & FastMCP Architecture
=============================================================================
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def check_environment():
    """Verify essential environment keys."""
    keys = {
        "LIVEKIT_URL": os.getenv("LIVEKIT_URL"),
        "LIVEKIT_API_KEY": os.getenv("LIVEKIT_API_KEY"),
        "LIVEKIT_API_SECRET": os.getenv("LIVEKIT_API_SECRET"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }

    print("\n[ULTRON KEY INTEGRITY CHECK]")
    for key, val in keys.items():
        is_set = bool(val and "xxxx" not in val and not val.startswith("your-"))
        status = "CONFIGURED [OK]" if is_set else "ACTION REQUIRED [!]"
        print(f"  * {key.ljust(22)} : {status}")


def main():
    banner = """
===============================================================================
  _   _ _     _____ ____   ___  _   _ 
 | | | | |   |_   _|  _ \ / _ \| \ | |
 | | | | |     | | | |_) | | | |  \| |
 | |_| | |___  | | |  _ <| |_| | |\  |
  \___/|_____| |_| |_| \_\\___/|_| \_|
       >> Vishnu's Autonomous Voice AI Architecture <<
===============================================================================
"""
    print(banner)
    check_environment()
    print("\n[DEPLOYMENT COMMANDS]")
    print("  Terminal 1 (MCP Tool Server) : uv run ultron")
    print("  Terminal 2 (Voice Agent)     : uv run ultron_voice")
    print("\nTo connect and speak, launch the LiveKit Agents Playground:")
    print("  https://agents-playground.livekit.io/\n")


if __name__ == "__main__":
    main()
