"""
Vishnu's ULTRON Configuration
Centralized configuration for MCP Server and Voice Agent.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Server identity
    SERVER_NAME: str = os.getenv("SERVER_NAME", "Vishnu's ULTRON")
    CREATOR_NAME: str = os.getenv("CREATOR_NAME", "Vishnu")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # MCP Network Configuration
    MCP_HOST: str = os.getenv("MCP_HOST", "127.0.0.1")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8000"))

    # External API keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")


config = Config()
