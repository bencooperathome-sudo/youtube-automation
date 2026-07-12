"""
Generate SRT subtitles for the narration script.
"""

from pathlib import Path
import sys

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
from settings import MODEL
from paths import SCRIPT, SUBTITLES

client = OpenAI(api_key=OPENAI_API_KEY)


def load_script():

    if not SCRIPT.exists():
        raise FileNotFoundError(
            f"Cannot find script file:\n{SCRIPT}"
        )

    return SCRIPT.read_text(encoding="utf-8")


def generate_subtitles(script):

    prompt = f"""
Create subtitles in standard SRT format.

SCRIPT

{script}

Rules

- Return ONLY valid SRT.
- Number every subtitle.
- Maximum two lines per subtitle.
- Keep subtitles easy to read.
- Synchronise naturally with spoken narration.
- Duration approximately 2-4 seconds each.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    subtitles = response.choices[0].message.content

    if not subtitles:
        raise RuntimeError(
            "OpenAI returned empty subtitles."
        )

    return subtitles.strip()


def save_subtitles(subtitles):

    with open(
        SUBTITLES,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(subtitles)


def main():

    print("=" * 60)
    print("Generating Subtitles")
    print("=" * 60)

    script = load_script()

    subtitles = generate_subtitles(script)

    save_subtitles(subtitles)

    print()
    print("✅ Subtitles generated successfully.")
    print(f"Saved to:\n{SUBTITLES}")


if __name__ == "__main__":

    main()