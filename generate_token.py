"""
Quick Token Generator for LiveKit Playground
Generates an authenticated participant token for Vishnu.
"""

import os
from dotenv import load_dotenv
from livekit import api

load_dotenv()

def generate():
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    server_url = os.getenv("LIVEKIT_URL")

    if not api_key or not api_secret:
        print("[!] Error: LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be configured in .env")
        return

    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity("Vishnu")
        .with_name("Vishnu")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room="ultron-command-room",
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .to_jwt()
    )

    print("=" * 70)
    print("           VISHNU'S ULTRON -- LIVEKIT CONNECTION TOKEN")
    print("=" * 70)
    print(f"Server URL : {server_url}")
    print(f"Room Name  : ultron-command-room")
    print(f"Identity   : Vishnu")
    print("-" * 70)
    print("Copy & paste this Token into the LiveKit Playground:")
    print("-" * 70)
    print(token)
    print("=" * 70)

if __name__ == "__main__":
    generate()
