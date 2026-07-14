"""Score an approved YouTube Shorts script before production."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import QUALITY_REPORT, SCRIPT
from settings import MODEL


PASS_SCORE = 30


def get_client() -> OpenAI:
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing from .env.")

    return OpenAI(api_key=api_key)


def load_script() -> str:
    if not SCRIPT.exists():
        raise FileNotFoundError(
            f"Script not found: {SCRIPT}. Run the earlier stages first."
        )

    script = SCRIPT.read_text(encoding="utf-8").strip()

    if not script:
        raise ValueError("Script is empty.")

    return script


def validate_report(report: dict[str, Any]) -> None:
    required_scores = ["hook", "clarity", "retention", "shareability"]

    for name in required_scores:
        value = report.get(name)

        if not isinstance(value, int) or not 1 <= value <= 10:
            raise ValueError(f"Invalid {name} score.")

    if not isinstance(report.get("feedback"), list):
        raise ValueError("Quality report must include feedback.")

    report["total"] = sum(report[name] for name in required_scores)


def main() -> None:
    script = load_script()

    prompt = f"""
You are a strict YouTube Shorts editor.

Score this narration from 1 to 10 for:
- hook
- clarity
- retention
- shareability

Do not fact-check it; that has already happened.
Judge only the writing quality and viewer experience.

SCRIPT:
{script}

Return valid JSON only:

{{
  "hook": 1,
  "clarity": 1,
  "retention": 1,
  "shareability": 1,
  "feedback": [
    "Specific, practical improvement",
    "Specific, practical improvement"
  ]
}}
""".strip()

    response = get_client().responses.create(
        model=MODEL,
        input=prompt,
        text={"format": {"type": "json_object"}},
        max_output_tokens=500,
    )

    report = json.loads(response.output_text)
    validate_report(report)

    report["pass_score"] = PASS_SCORE
    report["passed"] = report["total"] >= PASS_SCORE

    QUALITY_REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nQUALITY REPORT")
    print(f"Hook:         {report['hook']}/10")
    print(f"Clarity:      {report['clarity']}/10")
    print(f"Retention:    {report['retention']}/10")
    print(f"Shareability: {report['shareability']}/10")
    print(f"Total:        {report['total']}/40")

    if report["passed"]:
        print("\nScript passed quality scoring.")
        return

    raise RuntimeError(
        f"Script scored below {PASS_SCORE}/40. "
        f"See {QUALITY_REPORT} for improvements."
    )


if __name__ == "__main__":
    main()