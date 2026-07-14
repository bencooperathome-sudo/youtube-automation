"""
Research and fact-check a generated YouTube Shorts script.

Web research and JSON scoring must be separate OpenAI requests:
web search cannot be used with JSON mode in one request.
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

from paths import FACT_CHECK_REPORT, OUTPUT_DIR, SCRIPT

FACT_CHECK_MODEL = os.getenv("FACT_CHECK_MODEL", "gpt-4.1-mini")
MIN_WORDS = 70
MAX_WORDS = 95
MAX_RETRIES = 3
MAX_CORRECTION_ROUNDS = 1

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


def load_script() -> str:
    if not SCRIPT.exists():
        raise FileNotFoundError(
            f"Script not found: {SCRIPT}. Run script_generator.py first."
        )

    script = SCRIPT.read_text(encoding="utf-8").strip()

    if not script:
        raise ValueError("The script file is empty.")

    return script


def validate_narration(script: str) -> None:
    if not script.strip():
        raise ValueError("Corrected script was empty.")

    word_count = len(script.split())

    if not MIN_WORDS <= word_count <= MAX_WORDS:
        raise ValueError(
            f"Corrected script has {word_count} words; expected "
            f"{MIN_WORDS} to {MAX_WORDS}."
        )

    forbidden_markers = ("```", "TITLE:", "SCRIPT:", "•", "\n-", "\n*")

    for marker in forbidden_markers:
        if marker in script:
            raise ValueError(
                f"Corrected script contains forbidden formatting: {marker}"
            )


def research_script(client: OpenAI, script: str) -> str:
    """Use web search and return readable research notes."""

    response = client.responses.create(
        model=FACT_CHECK_MODEL,
        tools=[{"type": "web_search"}],
        tool_choice="required",
        input=f"""
Research the important factual claims in this YouTube Shorts narration.

NARRATION:
{script}

Search the web before answering. Prefer primary and reputable sources,
such as scientific organisations, museums, universities, government
sources, or established publications.

Write concise research notes in plain text. For every important claim,
state whether the available evidence supports it, contradicts it, or
leaves it uncertain. Include source names and links where possible.
Do not write JSON.
""".strip(),
        max_output_tokens=1800,
    )

    return response.output_text.strip()


def assess_research(
    client: OpenAI,
    script: str,
    research_notes: str,
) -> dict:
    """Convert research notes into a consistent machine-readable report."""

    response = client.responses.create(
        model=FACT_CHECK_MODEL,
        input=f"""
You are the final editor for an accurate interesting-facts YouTube channel.

Review the narration and the research notes below.

NARRATION:
{script}

RESEARCH NOTES:
{research_notes}

Return valid JSON only, using exactly this structure:

{{
  "status": "PASS or FAIL",
  "summary": "short explanation",
  "claims": [
    {{
      "claim": "important claim from the narration",
      "verdict": "SUPPORTED, UNSUPPORTED, MISLEADING, or UNCERTAIN",
      "note": "brief explanation"
    }}
  ],
  "corrected_script": "empty string if PASS; otherwise a corrected 75-95 word narration"
}}

Rules:
- PASS only if all important claims are supported and not misleading.
- FAIL if an important claim is unsupported, exaggerated, contradicted,
  misleading, or too uncertain.
- If status is FAIL, provide a replacement script using only well-supported
  claims from the research notes.
- The corrected script must be 75 to 95 words, natural British English,
  include no citations or headings, and end with a gentle follow request.
""".strip(),
        text={"format": {"type": "json_object"}},
        max_output_tokens=1200,
    )

    report = json.loads(response.output_text)

    if not isinstance(report, dict):
        raise ValueError("Fact-check response was not a JSON object.")

    status = str(report.get("status", "")).upper().strip()

    if status not in {"PASS", "FAIL"}:
        raise ValueError("Fact-check status must be PASS or FAIL.")

    if not isinstance(report.get("claims"), list):
        raise ValueError("Fact-check report did not contain claims.")

    report["status"] = status
    return report


def fact_check(
    client: OpenAI,
    script: str,
    round_number: int,
) -> dict:
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "Researching factual claims (round %s, attempt %s/%s).",
                round_number,
                attempt,
                MAX_RETRIES,
            )

            research_notes = research_script(client, script)

            if not research_notes:
                raise ValueError("Web research returned no usable notes.")

            evidence_file = (
                OUTPUT_DIR / f"fact_check_research_round_{round_number}.txt"
            )
            evidence_file.write_text(research_notes, encoding="utf-8")

            report = assess_research(client, script, research_notes)
            report["round"] = round_number
            report["research_file"] = str(evidence_file)

            return report

        except (
            APIError,
            APITimeoutError,
            RateLimitError,
            json.JSONDecodeError,
            ValueError,
        ) as error:
            last_error = error
            wait_seconds = attempt * 3

            logger.warning(
                "Fact-check attempt %s/%s failed: %s. Retrying in %s seconds.",
                attempt,
                MAX_RETRIES,
                error,
                wait_seconds,
            )

            time.sleep(wait_seconds)

    raise RuntimeError(
        f"Fact checking failed after {MAX_RETRIES} attempts."
    ) from last_error


def save_report(report: dict) -> None:
    temporary_file = FACT_CHECK_REPORT.with_suffix(".tmp")

    temporary_file.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    temporary_file.replace(FACT_CHECK_REPORT)


def main() -> None:
    logger.info("Starting researched fact check.")

    client = get_client()
    current_script = load_script()

    for round_number in range(1, MAX_CORRECTION_ROUNDS + 2):
        report = fact_check(client, current_script, round_number)

        logger.info(
            "Fact-check round %s result: %s",
            round_number,
            report["status"],
        )

        if report["status"] == "PASS":
            report["final_status"] = "passed"
            save_report(report)

            logger.info("Fact check passed.")
            return

        corrected_script = str(report.get("corrected_script", "")).strip()

        if round_number > MAX_CORRECTION_ROUNDS:
            report["final_status"] = "failed_after_correction"
            save_report(report)

            raise RuntimeError(
                "The script could not be verified after correction."
            )

        try:
            validate_narration(corrected_script)

        except ValueError as error:
            report["final_status"] = "failed_without_usable_correction"
            report["correction_error"] = str(error)
            save_report(report)

            raise RuntimeError(
                "The fact checker could not produce a usable correction."
            ) from error

        SCRIPT.write_text(corrected_script + "\n", encoding="utf-8")

        logger.warning(
            "Fact checker corrected the script. Re-checking the new version."
        )

        current_script = corrected_script


if __name__ == "__main__":
    main()