"""
Create a structured visual plan for one YouTube Short.

The plan is saved as shot_plan.json and is used by the video downloader
to search for relevant, copyright-safe stock footage.
"""

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

from paths import SCRIPT, SHOT_PLAN
from settings import MODEL, VIDEO_DURATION_SECONDS


MAX_RETRIES = 3
MIN_SHOTS = 5
MAX_SHOTS = 8

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


SHOT_PLAN_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "video_style",
        "target_duration_seconds",
        "shots",
    ],
    "properties": {
        "video_style": {
            "type": "string",
            "description": "A concise description of the overall visual style.",
        },
        "target_duration_seconds": {
            "type": "number",
            "description": "The total planned video duration in seconds.",
        },
        "shots": {
            "type": "array",
            "minItems": MIN_SHOTS,
            "maxItems": MAX_SHOTS,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "shot_number",
                    "start_seconds",
                    "end_seconds",
                    "narration_excerpt",
                    "search_query",
                    "visual_description",
                    "on_screen_text",
                    "transition",
                ],
                "properties": {
                    "shot_number": {"type": "integer"},
                    "start_seconds": {"type": "number"},
                    "end_seconds": {"type": "number"},
                    "narration_excerpt": {"type": "string"},
                    "search_query": {"type": "string"},
                    "visual_description": {"type": "string"},
                    "on_screen_text": {"type": "string"},
                    "transition": {
                        "type": "string",
                        "enum": ["cut", "fade", "zoom"],
                    },
                },
            },
        },
    },
}


def get_client() -> OpenAI:
    """Load the OpenAI key without requiring unrelated service keys."""

    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing from the project's .env file."
        )

    return OpenAI(api_key=api_key)


def load_script() -> str:
    """Load the approved narration script for this production run."""

    if not SCRIPT.exists():
        raise FileNotFoundError(
            f"Script not found: {SCRIPT}. Run script_generator.py first."
        )

    script = SCRIPT.read_text(encoding="utf-8").strip()

    if not script:
        raise ValueError("The narration script is empty.")

    return script


def build_instructions() -> str:
    return f"""
You are a YouTube Shorts visual director.

Create a compelling, practical shot plan for the supplied narration.

Requirements:
- Create between {MIN_SHOTS} and {MAX_SHOTS} shots.
- The total duration must be approximately {VIDEO_DURATION_SECONDS} seconds.
- Each shot should normally last 3 to 7 seconds.
- Cover the narration in order with no major gaps or overlaps.
- Use varied visuals that reinforce the narration and maintain attention.
- Each search_query must be 2 to 6 simple English words suitable for
  searching Pexels stock-video footage.
- Use generic, copyright-safe visual terms. Do not use game titles,
  brand names, character names, celebrities, logos, or copyrighted franchises
  in search_query.
- visual_description may be detailed, but must remain realistic for stock footage.
- on_screen_text must be short, optional, and easy to read on a phone screen.
- Use "cut" for most transitions. Use "fade" or "zoom" only where helpful.
- Do not invent facts or add narration that is not in the supplied script.

Return only JSON that matches the required schema.
""".strip()


def validate_plan(plan: dict) -> None:
    """Perform checks that protect downstream video generation."""

    shots = plan.get("shots")

    if not isinstance(shots, list) or not MIN_SHOTS <= len(shots) <= MAX_SHOTS:
        raise ValueError(
            f"Shot plan must contain {MIN_SHOTS}-{MAX_SHOTS} shots."
        )

    previous_end = 0.0

    for expected_number, shot in enumerate(shots, start=1):
        if shot["shot_number"] != expected_number:
            raise ValueError("Shot numbers must start at 1 and be consecutive.")

        start = float(shot["start_seconds"])
        end = float(shot["end_seconds"])

        if end <= start:
            raise ValueError(
                f"Shot {expected_number} ends before it starts."
            )

        if start < previous_end - 0.5:
            raise ValueError(
                f"Shot {expected_number} overlaps the previous shot."
            )

        if end - start < 2:
            raise ValueError(
                f"Shot {expected_number} is too short for usable footage."
            )

        if len(shot["search_query"].split()) < 2:
            raise ValueError(
                f"Shot {expected_number} needs a more useful search query."
            )

        previous_end = end

    if previous_end < VIDEO_DURATION_SECONDS - 5:
        raise ValueError(
            "Shot plan does not cover enough of the video duration."
        )


def create_shot_plan(client: OpenAI, script: str) -> dict:
    """Ask OpenAI for a validated structured shot plan."""

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.responses.create(
                model=MODEL,
                instructions=build_instructions(),
                input=f"NARRATION SCRIPT:\n\n{script}",
                max_output_tokens=1400,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "youtube_shot_plan",
                        "strict": True,
                        "schema": SHOT_PLAN_SCHEMA,
                    }
                },
            )

            plan = json.loads(response.output_text)
            validate_plan(plan)
            return plan

        except (APIError, APITimeoutError, RateLimitError) as error:
            last_error = error
            delay = attempt * 3
            logger.warning(
                "OpenAI request failed on attempt %s/%s: %s. Retrying in %ss.",
                attempt,
                MAX_RETRIES,
                error,
                delay,
            )
            time.sleep(delay)

        except (json.JSONDecodeError, ValueError) as error:
            last_error = error
            logger.warning(
                "Invalid shot plan on attempt %s/%s: %s",
                attempt,
                MAX_RETRIES,
                error,
            )

    raise RuntimeError(
        f"Could not create a valid shot plan after {MAX_RETRIES} attempts."
    ) from last_error


def save_plan(plan: dict) -> None:
    """Write the plan atomically so later stages never read a partial file."""

    temporary_file = SHOT_PLAN.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary_file.replace(SHOT_PLAN)


def main() -> None:
    logger.info("Starting shot planning.")

    script = load_script()
    plan = create_shot_plan(get_client(), script)
    save_plan(plan)

    logger.info("Shot plan saved to: %s", SHOT_PLAN)

    for shot in plan["shots"]:
        logger.info(
            "Shot %s: %ss-%ss | %s",
            shot["shot_number"],
            shot["start_seconds"],
            shot["end_seconds"],
            shot["search_query"],
        )


if __name__ == "__main__":
    main()  