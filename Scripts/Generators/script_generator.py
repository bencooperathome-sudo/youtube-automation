"""
Generate the narration script for the current YouTube Shorts run.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import APIError, APITimeoutError, OpenAI, RateLimitError

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import SCRIPT, TOPICS_FILE
from settings import MODEL, VIDEO_DURATION_SECONDS

MIN_WORDS = 75
MAX_WORDS = 95
MAX_RETRIES = 3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def get_client() -> OpenAI:
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing from the project's .env file."
        )

    return OpenAI(api_key=api_key)


def load_topic() -> str:
    if not TOPICS_FILE.exists():
        raise FileNotFoundError(
            f"Topics file not found: {TOPICS_FILE}. "
            "Run topic_generator.py first."
        )

    for line in TOPICS_FILE.read_text(encoding="utf-8").splitlines():
        topic = line.strip().lstrip("-•0123456789. ").strip()
        if topic:
            return topic

    raise ValueError(f"No usable topic was found in {TOPICS_FILE}.")


def build_instructions() -> str:
    return f"""
You write accurate, compelling YouTube Shorts narration about interesting facts.

Write one narration script about the supplied topic.

Requirements:
- {MIN_WORDS} to {MAX_WORDS} words.
- Target about {VIDEO_DURATION_SECONDS} seconds for a vertical YouTube Short.
- Begin with a strong but truthful hook.
- Use clear, conversational British English.
- Keep sentences short and easy to narrate.
- Explain one genuinely interesting fact with useful context.
- Do not invent, exaggerate, speculate, or present uncertainty as fact.
- Avoid World of Warcraft, gaming-specific content, politics, and advice.
- Do not use bullet points, headings, markdown, emojis, timestamps,
  citations, scene directions, or labels.
- End with a natural call to action, such as:
  "Follow for more surprising facts."

Return only the narration script.
""".strip()


def validate_script(script: str) -> None:
    if not script.strip():
        raise ValueError("The generated script was empty.")

    word_count = len(script.split())
    if not MIN_WORDS <= word_count <= MAX_WORDS:
        raise ValueError(
            f"Script has {word_count} words; expected "
            f"{MIN_WORDS} to {MAX_WORDS}."
        )

    forbidden_markers = ("```", "#", "•", "\n-", "\n*", "Title:", "Script:")
    for marker in forbidden_markers:
        if marker in script:
            raise ValueError(f"Script contains forbidden formatting: {marker}")


def generate_script(client: OpenAI, topic: str) -> str:
    last_error: Exception | None = None
    feedback = ""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.responses.create(
                model=MODEL,
                instructions=build_instructions(),
                input=(
                    f"Topic: {topic}\n\n"
                    f"{feedback}"
                    "Write the finished narration now."
                ),
                max_output_tokens=350,
            )

            script = response.output_text.strip()
            validate_script(script)
            return script

        except (APIError, APITimeoutError, RateLimitError) as error:
            last_error = error
            wait_seconds = attempt * 3
            logger.warning(
                "OpenAI request failed (attempt %s/%s): %s. Retrying in %s seconds.",
                attempt,
                MAX_RETRIES,
                error,
                wait_seconds,
            )
            time.sleep(wait_seconds)

        except ValueError as error:
            last_error = error
            feedback = (
                f"The previous draft was rejected because: {error}\n"
                "Rewrite it and obey every requirement exactly.\n\n"
            )
            logger.warning(
                "Generated draft rejected (attempt %s/%s): %s",
                attempt,
                MAX_RETRIES,
                error,
            )

    raise RuntimeError(
        f"Could not generate a valid script after {MAX_RETRIES} attempts."
    ) from last_error


def main() -> None:
    logger.info("Starting script generation.")

    topic = load_topic()
    logger.info("Using topic: %s", topic)

    script = generate_script(get_client(), topic)

    temporary_file = SCRIPT.with_suffix(".tmp")
    temporary_file.write_text(script + "\n", encoding="utf-8")
    temporary_file.replace(SCRIPT)

    logger.info("Script saved to: %s", SCRIPT)

    print("\nGenerated script:\n")
    print(script)


if __name__ == "__main__":
    main()