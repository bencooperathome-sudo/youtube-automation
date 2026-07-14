"""Generate AI narration audio from the approved script."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import OUTPUT_DIR, SCRIPT, VOICE
from settings import VOICE as VOICE_NAME


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing from .env.")

    if not SCRIPT.exists():
        raise FileNotFoundError(f"Script not found: {SCRIPT}")

    narration = SCRIPT.read_text(encoding="utf-8").strip()

    if not narration:
        raise ValueError("Script is empty.")

    client = OpenAI(api_key=api_key)

    print("Generating AI narration...")

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=VOICE_NAME,
        input=narration,
        instructions=(
            "Speak clearly, warmly, and confidently. "
            "Use an engaging but natural pace for a short facts video."
        ),
        response_format="mp3",
    ) as response:
        response.stream_to_file(VOICE)

    (OUTPUT_DIR / "ai_voice_disclosure.txt").write_text(
        "This video uses an AI-generated voice.\n",
        encoding="utf-8",
    )

    print(f"Narration saved to: {VOICE}")


if __name__ == "__main__":
    main()