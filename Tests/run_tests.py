"""Preflight checks for the YouTube automation project.

This script does not call any paid APIs and does not upload anything.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SCRIPTS = [
    "main.py",
    "paths.py",
    "Scripts/Generators/topic_generator.py",
    "Scripts/Generators/script_generator.py",
    "Scripts/Generators/fact_checker.py",
    "Scripts/Generators/quality_scorer.py",
    "Scripts/Generators/shot_planner.py",
    "Scripts/Generators/voice_generator.py",
    "Scripts/Generators/subtitle_generator.py",
    "Scripts/Generators/metadata_generator.py",
    "Scripts/Pipeline/video_downloader.py",
    "Scripts/Pipeline/video_editor.py",
    "Scripts/Pipeline/youtube_upload.py",
    "Scripts/Pipeline/scheduler.py",
]

REQUIRED_PACKAGES = [
    "dotenv",
    "openai",
    "requests",
    "moviepy",
    "google_auth_oauthlib",
    "googleapiclient",
    "schedule",
]


def check(name: str, passed: bool, detail: str = "") -> bool:
    symbol = "PASS" if passed else "FAIL"
    print(f"[{symbol}] {name}" + (f" — {detail}" if detail else ""))
    return passed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Also check YouTube upload credentials.",
    )
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env")
    all_passed = True

    print("YouTube Automation Preflight\n")

    for relative_path in REQUIRED_SCRIPTS:
        path = PROJECT_ROOT / relative_path
        exists = path.is_file()
        all_passed &= check(relative_path, exists)

        if exists:
            try:
                ast.parse(path.read_text(encoding="utf-8"))
                all_passed &= check(
                    f"{relative_path} syntax",
                    True,
                )
            except SyntaxError as error:
                all_passed &= check(
                    f"{relative_path} syntax",
                    False,
                    str(error),
                )

    for package in REQUIRED_PACKAGES:
        installed = importlib.util.find_spec(package) is not None
        all_passed &= check(f"Python package: {package}", installed)

    all_passed &= check(
        "OPENAI_API_KEY in .env",
        bool(os.getenv("OPENAI_API_KEY")),
    )
    all_passed &= check(
        "PEXELS_API_KEY in .env",
        bool(os.getenv("PEXELS_API_KEY")),
    )
    all_passed &= check(
        "FFmpeg available",
        shutil.which("ffmpeg") is not None,
    )

    if args.upload:
        all_passed &= check(
            "client_secret.json exists",
            (PROJECT_ROOT / "client_secret.json").is_file(),
        )

    if all_passed:
        print("\nPreflight complete: the project is ready for testing.")
        raise SystemExit(0)

    print("\nPreflight failed: fix the items marked FAIL.")
    raise SystemExit(1)


if __name__ == "__main__":
    main()