"""
Generate YouTube Shorts topics using OpenAI.
"""

from pathlib import Path
import sys
import random

# -------------------------------------------------------
# Make project root importable
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# -------------------------------------------------------
# Imports
# -------------------------------------------------------

from openai import OpenAI

from config import OPENAI_API_KEY
from settings import MODEL, WOW_TOPICS
from paths import OUTPUT_DIR

# -------------------------------------------------------
# OpenAI Client
# -------------------------------------------------------

client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------------------------------------
# Output File
# -------------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TOPICS_FILE = OUTPUT_DIR / "topics.txt"

# -------------------------------------------------------
# Prompt Builder
# -------------------------------------------------------

def build_prompt(topic: str) -> str:

    return f"""
Generate FIVE YouTube Shorts ideas.

CATEGORY

{topic}

Rules

- Every idea must be completely factual.
- Every idea must be surprising.
- Make viewers think "I never knew that."
- Suitable for a 30–40 second YouTube Short.
- One idea per line.
- No numbering.
- No explanations.
- Avoid clickbait.
- Avoid common facts.
"""

# -------------------------------------------------------
# Topic Generation
# -------------------------------------------------------

def generate_topics():

    selected_topic = random.choice(WOW_TOPICS)

    print("=" * 60)
    print("Generating Topics")
    print("=" * 60)
    print(f"Category: {selected_topic}")

    prompt = build_prompt(selected_topic)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    topics = response.choices[0].message.content

    if not topics:
        raise RuntimeError("OpenAI returned no topics.")

    TOPICS_FILE.write_text(
        topics.strip(),
        encoding="utf-8"
    )

    print()
    print("Generated topics:")
    print("----------------------------")
    print(topics)
    print("----------------------------")
    print()
    print(f"Saved to:")
    print(TOPICS_FILE)

    return topics


# -------------------------------------------------------
# Main
# -------------------------------------------------------

if __name__ == "__main__":

    try:

        generate_topics()

        print()
        print("Topic generation completed successfully.")

    except Exception as e:

        print()
        print("Topic generation failed.")
        print(e)

        raise