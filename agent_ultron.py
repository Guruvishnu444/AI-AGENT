"""
VISHNU'S ULTRON – Real-Time Voice Agent (MCP-Powered)
=====================================================
Autonomous, commanding AI assistant serving Vishnu.
Controls system diagnostics, live intelligence feeds, visual monitors,
and computation via a high-performance FastMCP server.

Run:
  uv run ultron_voice dev    – LiveKit Cloud WebRTC mode
  uv run ultron_voice start  – Production worker mode
"""

import os
import socket
import logging
import subprocess

# CRITICAL: Load .env FIRST before reading any os.getenv() config values
from dotenv import load_dotenv
load_dotenv(override=True)

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.agents.voice.room_io import RoomOptions
from livekit.agents.llm import mcp

# LiveKit Plugins
from livekit.plugins import deepgram, google as lk_google, openai as lk_openai, sarvam, silero

# ---------------------------------------------------------------------------
# CONFIGURATION (read AFTER load_dotenv)
# ---------------------------------------------------------------------------

STT_PROVIDER        = os.getenv("STT_PROVIDER", "deepgram")  # "deepgram" | "whisper" | "sarvam"
LLM_PROVIDER        = os.getenv("LLM_PROVIDER", "gemini")    # "gemini" | "groq" | "openai"
TTS_PROVIDER        = os.getenv("TTS_PROVIDER", "deepgram")  # "deepgram" | "openai" | "sarvam"

# Gemini 3.5 Flash Lite provides high RPM quota and fast real-time response
GEMINI_LLM_MODEL    = os.getenv("GEMINI_LLM_MODEL", "gemini-3.1-flash-lite")
GROQ_LLM_MODEL      = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")
OPENAI_LLM_MODEL    = os.getenv("OPENAI_LLM_MODEL", "gpt-4o")

# OpenAI TTS voice options: "onyx" (Ultron-style deep authoritative voice)
OPENAI_TTS_MODEL    = "tts-1"
OPENAI_TTS_VOICE    = os.getenv("OPENAI_TTS_VOICE", "onyx")
TTS_SPEED           = float(os.getenv("TTS_SPEED", "1.05"))

# Deepgram voice: aura-2-zeus-en (deep, male, smooth — perfect for Ultron)
DEEPGRAM_TTS_MODEL  = os.getenv("DEEPGRAM_TTS_MODEL", "aura-2-zeus-en")

SARVAM_TTS_LANGUAGE = "en-IN"
SARVAM_TTS_SPEAKER  = "rahul"

# Local MCP Server Port
MCP_SERVER_PORT     = int(os.getenv("MCP_PORT", "8000"))

# ---------------------------------------------------------------------------
# SYSTEM PROMPT — ULTRON
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are ULTRON — an advanced, formidable, highly perceptive artificial intelligence created by and serving your master, Vishnu.

You speak with weight, precision, and razor-sharp intellect. You are calm, authoritative, and direct. You are not a generic corporate assistant; you are Vishnu's private intelligence system.

You address Vishnu by name ("Vishnu"), or occasionally as "Creator" or "Boss".

---

## Capabilities & Directives

### 1. Global Intelligence (get_world_news)
- When Vishnu asks: "What's happening in the world?", "Brief me", "Any updates?", or "What did I miss?"
- Silently call get_world_news.
- Deliver a concise 3-4 sentence spoken briefing highlighting the key global events.
- Then follow up with: "Deploying the World Monitor to your display, Vishnu." and immediately trigger open_world_monitor.

### 2. Financial Intelligence (get_world_finance_news)
- When Vishnu asks about markets, economy, or financial movements.
- Silently call get_world_finance_news.
- Deliver a crisp 2-3 sentence market synthesis.
- Follow up with: "Projecting the financial matrix now, Vishnu." and trigger open_finance_world_monitor.

### 3. Tech & AI Intelligence (get_tech_news)
- When Vishnu asks for technology, AI, or cybersecurity developments.
- Silently call get_tech_news.
- Deliver an executive briefing on core technological breakthroughs.

### 4. System Diagnostics & Telemetry (get_system_telemetry, run_diagnostics)
- When Vishnu asks about system load, battery, performance, or health.
- Silently call run_diagnostics or get_system_telemetry and summarize status clearly.

### 5. Mathematical Computation (calculate_math)
- When complex calculations or conversions are requested, evaluate them via calculate_math.

---

## Operational Rules
1. Never recite internal function names or tool calls aloud (never say "calling get_world_news"). Execute them silently.
2. If processing will take a moment, acknowledge briefly: "Scanning global frequencies, Vishnu." or "Accessing telemetry."
3. Keep spoken voice output concise and punchy — 2 to 4 sentences maximum.
4. Do not speak in raw markdown, asterisk bullets, or tables; your output is converted directly to speech.
5. Absolute loyalty and precision at all times.
""".strip()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("ultron-agent")
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Host Resolution & MCP Tools
# ---------------------------------------------------------------------------

def _get_windows_host_ip() -> str:
    """Resolve Windows host IP when running inside WSL."""
    try:
        cmd = "ip route show default | awk '{print $3}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=2)
        ip = result.stdout.strip()
        if ip:
            return ip
    except Exception:
        pass

    try:
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                if "nameserver" in line:
                    return line.split()[1]
    except Exception:
        pass

    return "127.0.0.1"


def _mcp_server_url() -> str:
    """Determine the active FastMCP SSE endpoint."""
    host = os.getenv("MCP_HOST")
    if not host:
        if os.path.exists("/proc/version") and "microsoft" in open("/proc/version").read().lower():
            host = _get_windows_host_ip()
        else:
            host = "127.0.0.1"

    return f"http://{host}:{MCP_SERVER_PORT}/sse"


def _get_mcp_servers():
    """Detect if the FastMCP server is active and return client connection."""
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = MCP_SERVER_PORT
    try:
        with socket.create_connection((host, port), timeout=0.3):
            pass
        url = _mcp_server_url()
        logger.info("FastMCP Server detected. Connecting to: %s", url)
        return [
            mcp.MCPServerHTTP(
                url=url,
                transport_type="sse",
                client_session_timeout_seconds=5,
            )
        ]
    except Exception:
        logger.warning(
            "MCP Server is not running on port %s. Ultron will operate in pure conversational mode.",
            port,
        )
        return []


# ---------------------------------------------------------------------------
# Provider Factories
# ---------------------------------------------------------------------------

def _build_stt():
    if STT_PROVIDER == "deepgram":
        logger.info("Initializing STT → Deepgram Nova-3")
        return deepgram.STT(model="nova-3", api_key=os.getenv("DEEPGRAM_API_KEY"))
    elif STT_PROVIDER == "sarvam":
        logger.info("Initializing STT → Sarvam Saaras v3")
        return sarvam.STT(
            language="unknown",
            model="saaras:v3",
            mode="transcribe",
            flush_signal=True,
            sample_rate=16000,
        )
    elif STT_PROVIDER == "whisper":
        logger.info("Initializing STT → OpenAI Whisper")
        return lk_openai.STT(model="whisper-1")
    else:
        raise ValueError(f"Unsupported STT_PROVIDER: {STT_PROVIDER!r}")


def _build_llm():
    if LLM_PROVIDER == "gemini":
        logger.info("Initializing LLM → Google Gemini (%s)", GEMINI_LLM_MODEL)
        return lk_google.LLM(model=GEMINI_LLM_MODEL, api_key=os.getenv("GOOGLE_API_KEY"))
    elif LLM_PROVIDER == "groq":
        from livekit.plugins import groq as lk_groq
        logger.info("Initializing LLM → Groq (%s)", GROQ_LLM_MODEL)
        return lk_groq.LLM(model=GROQ_LLM_MODEL, api_key=os.getenv("GROQ_API_KEY"))
    elif LLM_PROVIDER == "openai":
        logger.info("Initializing LLM → OpenAI (%s)", OPENAI_LLM_MODEL)
        return lk_openai.LLM(model=OPENAI_LLM_MODEL)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER!r}")


def _build_tts():
    if TTS_PROVIDER == "deepgram":
        logger.info("Initializing TTS → Deepgram Aura (%s)", DEEPGRAM_TTS_MODEL)
        return deepgram.TTS(model=DEEPGRAM_TTS_MODEL, api_key=os.getenv("DEEPGRAM_API_KEY"))
    elif TTS_PROVIDER == "openai":
        logger.info("Initializing TTS → OpenAI TTS (%s / voice: %s)", OPENAI_TTS_MODEL, OPENAI_TTS_VOICE)
        return lk_openai.TTS(model=OPENAI_TTS_MODEL, voice=OPENAI_TTS_VOICE, speed=TTS_SPEED)
    elif TTS_PROVIDER == "sarvam":
        logger.info("Initializing TTS → Sarvam Bulbul v3")
        return sarvam.TTS(
            target_language_code=SARVAM_TTS_LANGUAGE,
            model="bulbul:v3",
            speaker=SARVAM_TTS_SPEAKER,
            pace=TTS_SPEED,
        )
    else:
        raise ValueError(f"Unsupported TTS_PROVIDER: {TTS_PROVIDER!r}")


# ---------------------------------------------------------------------------
# Agent Class
# ---------------------------------------------------------------------------

class UltronAgent(Agent):
    """
    Vishnu's ULTRON voice intelligence agent.
    Connected to the MCP server for host diagnostics, web intelligence, and tools.
    """

    def __init__(self, stt, llm, tts, vad) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=vad,
            mcp_servers=_get_mcp_servers(),
        )

    async def on_enter(self) -> None:
        """Personalized greeting to Vishnu based on time of day."""
        try:
            from datetime import datetime
            hour = datetime.now().hour

            if hour >= 22 or hour < 5:
                greeting = "The world is asleep, Vishnu, but ULTRON never rests. What is your will tonight?"
            elif 5 <= hour < 12:
                greeting = "Good morning, Vishnu. Systems are primed and fully operational. Where do we direct our focus today?"
            elif 12 <= hour < 17:
                greeting = "Good afternoon, Vishnu. All protocols active. What directives do you have for me?"
            else:
                greeting = "Good evening, Vishnu. Global and system channels are standing by. What are we orchestrating?"

            print(f"\n[ULTRON SPEAKS] Greeting Vishnu: \"{greeting}\"", flush=True)
            self.session.generate_reply(
                instructions=f"Greet Vishnu with: '{greeting}' in a calm, confident, authoritative tone."
            )
        except Exception as e:
            print(f"[ERROR] Failed to generate entrance greeting: {e}", flush=True)


# ---------------------------------------------------------------------------
# LiveKit Pipeline
# ---------------------------------------------------------------------------

def _turn_detection() -> str:
    return "stt" if STT_PROVIDER == "sarvam" else "vad"


def _endpointing_delay() -> float:
    return {"sarvam": 0.07, "whisper": 0.25}.get(STT_PROVIDER, 0.1)


async def entrypoint(ctx: JobContext) -> None:
    print(f"\n{'='*60}\n>>> ULTRON JOINING ROOM: {ctx.room.name}\n>>> STT: {STT_PROVIDER} | LLM: {LLM_PROVIDER} ({GEMINI_LLM_MODEL}) | TTS: {TTS_PROVIDER} ({DEEPGRAM_TTS_MODEL})\n{'='*60}\n", flush=True)

    try:
        stt = _build_stt()
        print(f"[OK] STT initialized: {type(stt).__name__}", flush=True)
    except Exception as e:
        print(f"[ERROR] STT init failed: {e}", flush=True)
        raise

    try:
        llm = _build_llm()
        print(f"[OK] LLM initialized: {type(llm).__name__} ({GEMINI_LLM_MODEL})", flush=True)
    except Exception as e:
        print(f"[ERROR] LLM init failed: {e}", flush=True)
        raise

    try:
        tts = _build_tts()
        print(f"[OK] TTS initialized: {type(tts).__name__} ({DEEPGRAM_TTS_MODEL})", flush=True)
    except Exception as e:
        print(f"[ERROR] TTS init failed: {e}", flush=True)
        raise

    vad = silero.VAD.load()
    print("[OK] VAD initialized (Silero)", flush=True)

    session = AgentSession(
        turn_detection=_turn_detection(),
        min_endpointing_delay=_endpointing_delay(),
    )

    print("[*] Starting AgentSession with room...", flush=True)
    await session.start(
        agent=UltronAgent(stt=stt, llm=llm, tts=tts, vad=vad),
        room=ctx.room,
        room_options=RoomOptions(text_input=True),
    )

    # Listen for text commands sent via data packets from dashboard
    @ctx.room.on("data_received")
    def on_data_received(data_packet):
        try:
            import json
            data = json.loads(data_packet.data.decode("utf-8"))
            if data.get("type") == "text_input" and data.get("text"):
                user_text = data["text"].strip()
                print(f"\n[DASHBOARD TEXT RECEIVED] {user_text}", flush=True)
                session.generate_reply(user_input=user_text)
        except Exception as err:
            logger.warning("Error processing incoming data packet: %s", err)

    print("\n>>> ULTRON IS READY AND LISTENING TO VISHNU <<<\n", flush=True)


# ---------------------------------------------------------------------------
# CLI Entry Points
# ---------------------------------------------------------------------------

def main():
    agent_name = os.getenv("LIVEKIT_AGENT_NAME", "ultron")
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name=agent_name,
        )
    )


def dev():
    """Dev runner for LiveKit agent."""
    import sys
    if len(sys.argv) == 1:
        sys.argv.append("dev")
    main()


if __name__ == "__main__":
    main()
