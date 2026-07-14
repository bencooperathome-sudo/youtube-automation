"""Shared paths for one YouTube-video production run."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = PROJECT_ROOT / "Output"
LOGS_DIR = PROJECT_ROOT / "Logs"
PROMPTS_DIR = PROJECT_ROOT / "Prompts"

RUN_DIRECTORY_VARIABLE = "YOUTUBE_RUN_DIR"


def get_run_dir() -> Path:
    """
    Return the run directory selected by main.py.

    Every pipeline stage must receive the same YOUTUBE_RUN_DIR value.
    """

    configured_path = os.getenv(RUN_DIRECTORY_VARIABLE)

    if not configured_path:
        raise RuntimeError(
            "YOUTUBE_RUN_DIR is not set. Run the pipeline through main.py "
            "after updating it to create and pass a shared run directory."
        )

    run_dir = Path(configured_path).expanduser()

    if not run_dir.is_absolute():
        run_dir = PROJECT_ROOT / run_dir

    run_dir = run_dir.resolve()

    try:
        run_dir.relative_to(OUTPUT_ROOT.resolve())
    except ValueError as error:
        raise RuntimeError(
            f"YOUTUBE_RUN_DIR must be inside {OUTPUT_ROOT}, not {run_dir}."
        ) from error

    return run_dir


OUTPUT_DIR = get_run_dir()
ASSETS_DIR = OUTPUT_DIR / "assets"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Content inputs and outputs
TOPICS_FILE = OUTPUT_DIR / "topics.txt"
TOPIC = OUTPUT_DIR / "topic.txt"
SCRIPT = OUTPUT_DIR / "script.txt"
SHOT_PLAN = OUTPUT_DIR / "shot_plan.json"

# Generated media
VOICE = OUTPUT_DIR / "voice.mp3"
SUBTITLES = OUTPUT_DIR / "subtitles.srt"
FINAL_VIDEO = OUTPUT_DIR / "final_video.mp4"
VIDEO_WITH_SUBTITLES = OUTPUT_DIR / "video_with_subtitles.mp4"
THUMBNAIL = OUTPUT_DIR / "thumbnail.jpg"

# YouTube metadata
TITLE = OUTPUT_DIR / "title.txt"
DESCRIPTION = OUTPUT_DIR / "description.txt"
HASHTAGS = OUTPUT_DIR / "hashtags.txt"
KEYWORDS = OUTPUT_DIR / "keywords.txt"
PINNED_COMMENT = OUTPUT_DIR / "pinned_comment.txt"

# Quality-control outputs
FACT_CHECK_REPORT = OUTPUT_DIR / "fact_check_report.json"
QUALITY_REPORT = OUTPUT_DIR / "quality_report.json"
