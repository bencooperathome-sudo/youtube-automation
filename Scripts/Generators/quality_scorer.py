"""
Quality scorer for YouTube Shorts.

Scores every generated script before the expensive
voice generation and video editing stages.

Author: Benjamin Cooper Project
"""

from pathlib import Path
import json
from openai import OpenAI

from config import OPENAI_API_KEY
from settings import MODEL
from paths import OUTPUT_DIR, SCRIPT

client = OpenAI(api_key=OPENAI_API_KEY)

QUALITY_REPORT = OUTPUT_DIR / "quality_report.json"

PASS_SCORE = 34


def load_script():

    with open(SCRIPT, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(script: str):

    return f"""
You are an expert YouTube Shorts consultant.

Your job is to score this script.

SCRIPT

{script}

Evaluate the following:

1. Hook
Does the opening immediately create curiosity?

2. Accuracy
Are the claims believable and internally consistent?

3. Viewer Retention
Does each sentence encourage the viewer to continue?

4. Virality
Would this likely perform well on YouTube Shorts?

Score each category from 1-10.

Be critical.

Return ONLY valid JSON.

Example:

{{
    "hook": 9,
    "accuracy": 10,
    "retention": 8,
    "virality": 9,
    "total": 36,
    "feedback": [
        "Excellent hook",
        "Sentence three could be shorter",
        "Ending could be stronger"
    ]
}}
"""


def score_script(script):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": build_prompt(script)
            }
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(
        response.choices[0].message.content
    )


def save_report(report):

    with open(
        QUALITY_REPORT,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            indent=4
        )


def print_results(report):

    print()

    print("=" * 60)
    print("QUALITY REPORT")
    print("=" * 60)

    print(f"Hook       : {report['hook']}/10")
    print(f"Accuracy   : {report['accuracy']}/10")
    print(f"Retention  : {report['retention']}/10")
    print(f"Virality   : {report['virality']}/10")

    print("-" * 60)

    print(f"TOTAL SCORE : {report['total']}/40")

    print()

    print("Feedback:")

    for item in report["feedback"]:
        print(f"• {item}")

    print()

    if report["total"] >= PASS_SCORE:
        print("✅ Script PASSED quality check.")
    else:
        print("❌ Script FAILED quality check.")


def main():

    print("=" * 60)
    print("Quality Scorer")
    print("=" * 60)

    script = load_script()

    report = score_script(script)

    save_report(report)

    print_results(report)

    if report["total"] < PASS_SCORE:
        raise RuntimeError(
            f"Quality score too low ({report['total']}/40)"
        )


if __name__ == "__main__":
    main()