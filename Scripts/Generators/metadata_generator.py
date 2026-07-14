"""Create YouTube title, description, keywords, hashtags, and pinned comment."""

from __future__ import annotations

import json
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

from paths import DESCRIPTION, HASHTAGS, KEYWORDS, PINNED_COMMENT, SCRIPT, TITLE
from settings import MODEL

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
        raise RuntimeError("OPENAI_API_KEY is missing from the .env file.")

    return OpenAI(
        api_key=api_key,
        timeout=90.0,
        max_retries=2,
    )


def load_script() -> str:
    if not SCRIPT.exists():
        raise FileNotFoundError(
            f"Script not found: {SCRIPT}. Run script_generator.py first."
        )

    script = SCRIPT.read_text(encoding="utf-8").strip()

    if not script:
        raise ValueError("The narration script is empty.")

    return script


def validate_metadata(metadata: dict) -> None:
    for name in ("title", "description", "pinned_comment"):
        if not isinstance(metadata.get(name), str) or not metadata[name].strip():
            raise ValueError(f"Metadata field '{name}' is missing or empty.")

    if len(metadata["title"]) > 60:
        raise ValueError("Title exceeds YouTube's 60-character target.")

    for name in ("keywords", "hashtags"):
        if not isinstance(metadata.get(name), list) or not metadata[name]:
            raise ValueError(f"Metadata list '{name}' is missing or empty.")


def generate_metadata(client: OpenAI, script: str) -> dict:
    prompt = f"""
Create accurate, engaging YouTube Shorts metadata for this narration.

NARRATION:
{script}

Return valid JSON only in this format:

{{
  "title": "Title under 60 characters",
  "description": "Two concise sentences, including a natural call to action.",
  "keywords": ["keyword one", "keyword two"],
  "hashtags": ["#InterestingFacts", "#Science"],
  "pinned_comment": "One friendly question encouraging viewers to comment."
}}

Rules:
- Make no claim that is not supported by the narration.
- Avoid misleading clickbait.
- Provide 8 to 12 keywords.
- Provide 3 to 5 hashtags.
- Do not use World of Warcraft, gaming, or unrelated hashtags.
""".strip()

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.responses.create(
                model=MODEL,
                input=prompt,
                text={"format": {"type": "json_object"}},
                max_output_tokens=700,
            )

            metadata = json.loads(response.output_text)
            validate_metadata(metadata)
            return metadata

        except (
            APIError,
            APITimeoutError,
            RateLimitError,
            json.JSONDecodeError,
            ValueError,
        ) as error:
            last_error = error
            wait_seconds = attempt * 5

            logger.warning(
                "Metadata attempt %s/%s failed: %s. Retrying in %s seconds.",
                attempt,
                MAX_RETRIES,
                error,
                wait_seconds,
            )

            time.sleep(wait_seconds)

    raise RuntimeError(
        f"Could not generate metadata after {MAX_RETRIES} attempts."
    ) from last_error


def main() -> None:
    logger.info("Starting metadata generation.")

    metadata = generate_metadata(get_client(), load_script())

    TITLE.write_text(metadata["title"].strip() + "\n", encoding="utf-8")
    DESCRIPTION.write_text(
        metadata["description"].strip() + "\n",
        encoding="utf-8",
    )
    KEYWORDS.write_text(
        ", ".join(str(item).strip() for item in metadata["keywords"]) + "\n",
        encoding="utf-8",
    )
    HASHTAGS.write_text(
        " ".join(str(item).strip() for item in metadata["hashtags"]) + "\n",
        encoding="utf-8",
    )
    PINNED_COMMENT.write_text(
        metadata["pinned_comment"].strip() + "\n",
        encoding="utf-8",
    )

    logger.info("Metadata saved to: %s", TITLE.parent)
    print(f"\nTitle: {metadata['title']}")
    print(f"Hashtags: {' '.join(metadata['hashtags'])}")


if __name__ == "__main__":
    main()