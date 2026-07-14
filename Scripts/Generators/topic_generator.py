"""Generate general-interest fact topics for YouTube Shorts."""

from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import OUTPUT_DIR, TOPICS_FILE
from settings import CONTENT_REQUIREMENTS, FACT_CATEGORIES, MODEL


def get_client() -> OpenAI:
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing from .env.")

    return OpenAI(api_key=api_key)


def main() -> None:
    category = random.choice(FACT_CATEGORIES)

    prompt = f"""
Generate exactly five original YouTube Shorts topic ideas.

Category: {category}

Channel requirements:
{chr(10).join(f"- {item}" for item in CONTENT_REQUIREMENTS)}

Return valid JSON only:

{{
  "topics": [
    "One specific, surprising, factual video topic",
    "..."
  ]
}}

Rules:
- Every topic must focus on one interesting fact or discovery.
- Avoid World of Warcraft, gaming-specific content, politics, and advice.
- Avoid vague topics such as "interesting space facts".
- Make each topic specific enough for a 35-second video.
- Do not number the topics.
""".strip()

    response = get_client().responses.create(
        model=MODEL,
        input=prompt,
        text={"format": {"type": "json_object"}},
        max_output_tokens=500,
    )

    data = json.loads(response.output_text)
    topics = data.get("topics", [])

    if not isinstance(topics, list) or len(topics) != 5:
        raise RuntimeError("Topic generator did not return exactly five topics.")

    clean_topics = [str(topic).strip() for topic in topics if str(topic).strip()]

    if len(clean_topics) != 5:
        raise RuntimeError("Topic generator returned empty topics.")

    TOPICS_FILE.write_text(
        "\n".join(clean_topics) + "\n",
        encoding="utf-8",
    )

    (OUTPUT_DIR / "topic_candidates.json").write_text(
        json.dumps(
            {"category": category, "topics": clean_topics},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Category: {category}\n")
    print("Generated topics:")
    for number, topic in enumerate(clean_topics, start=1):
        print(f"{number}. {topic}")

    print(f"\nSaved to: {TOPICS_FILE}")


if __name__ == "__main__":
    main()