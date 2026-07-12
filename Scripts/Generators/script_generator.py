"""
Generate narration scripts for YouTube Shorts.

Production-ready version with:
- Error handling
- Logging
- Retry logic
- Script validation
- Type hints
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from openai import OpenAI

from config import OPENAI_API_KEY
from paths import OUTPUT_DIR, SCRIPT
from settings import MODEL

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

MIN_WORDS = 115
MAX_WORDS = 135

MAX_RETRIES = 3

TOPICS_FILE = OUTPUT_DIR / "topics.txt"

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------

def load_topic() -> str:
    """Load the first topic from topics.txt."""

    if not TOPICS_FILE.exists():
        raise FileNotFoundError(
            f"Topic file not found: {TOPICS_FILE}"
        )

    with open(TOPICS_FILE, "r", encoding="utf-8") as file:
        topic = file.readline().strip()

    if not topic:
        raise ValueError("No topics found inside topics.txt")

    return topic

# ------------------------------------------------------------------
# Prompt Template
# ------------------------------------------------------------------

PROMPT_TEMPLATE = """
You are an expert YouTube Shorts writer and fitness enthusiast.

Your task is to create ONE YouTube Shorts narration script about this topic:

TOPIC:
{topic}

GOAL:
Create a script that maximises viewer retention and feels like it was written by an experienced gaming YouTuber.

STRICT REQUIREMENTS

• Between 115 and 135 words.
• Around 30-35 seconds of narration.
• Every fact MUST be historically accurate according to official Blizzard lore or documented game mechanics.
• Never invent facts.
• Never speculate.
• Never use clickbait that is factually incorrect.
• Use conversational spoken English.
• No bullet points.
• No markdown.
• No emojis.
• No scene directions.
• No timestamps.
• Output ONLY the narration.

SCRIPT STRUCTURE

1. First sentence MUST immediately create curiosity.

Examples:

"Almost every WoW player has walked past this secret..."
"Blizzard accidentally created one of Warcraft's biggest mysteries..."
"Most players never realised this actually happened..."

2. Explain the background in one or two short sentences.

3. Reveal the surprising fact.

4. Explain why this matters in Warcraft lore or gameplay.

5. Finish with a sentence that makes viewers want more.

Example:

"If you enjoyed this fact, follow for another hidden World of Warcraft secret tomorrow."

WRITING STYLE

• Fast paced.
• High curiosity.
• Every sentence should encourage watching the next.
• Avoid repeating information.
• Sound like a knowledgeable gamer.
• Keep sentences short.
• Vary sentence length.
• Use vivid language.
• Avoid filler words.

QUALITY CHECK BEFORE RETURNING

✓ All facts are correct.
✓ No repeated information.
✓ Hook is strong.
✓ Easy for AI voice narration.
✓ Suitable for subtitles.
✓ Suitable for YouTube Shorts.

Return ONLY the finished narration.
"""
# ------------------------------------------------------------------
# Prompt Builder
# ------------------------------------------------------------------

def build_prompt(topic: str) -> str:
    """Insert the topic into the prompt template."""
    return PROMPT_TEMPLATE.format(topic=topic)


# ------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------

def validate_script(script: str) -> None:
    """
    Validate the generated narration before saving.
    Raises ValueError if validation fails.
    """

    if not script:
        raise ValueError("OpenAI returned an empty script.")

    words = script.split()

    if len(words) < MIN_WORDS:
        raise ValueError(
            f"Script too short ({len(words)} words)."
        )

    if len(words) > MAX_WORDS:
        raise ValueError(
            f"Script too long ({len(words)} words)."
        )

    forbidden = [
        "#",
        "* ",
        "- ",
        "•",
        "```",
    ]

    for item in forbidden:
        if item in script:
            raise ValueError(
                f"Forbidden formatting detected: {item}"
            )