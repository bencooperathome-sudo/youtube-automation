"""
Main entry point for the YouTube Shorts automation pipeline.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = PROJECT_ROOT / "Output"
LOGS_DIR = PROJECT_ROOT / "Logs"
RUN_DIRECTORY_VARIABLE = "YOUTUBE_RUN_DIR"

LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOGS_DIR / f"automation_{datetime.now():%Y%m%d_%H%M%S}.log",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


PIPELINE_STEPS = [
    ("Scripts/Generators/topic_generator.py", "Topic Generator"),
    ("Scripts/Generators/script_generator.py", "Script Generator"),
    ("Scripts/Generators/fact_checker.py", "Fact Checker"),
    ("Scripts/Generators/quality_scorer.py", "Quality Scorer"),
    ("Scripts/Generators/shot_planner.py", "Shot Planner"),
    ("Scripts/Pipeline/video_downloader.py", "Video Downloader"),
    ("Scripts/Generators/voice_generator.py", "Voice Generator"),
    ("Scripts/Generators/subtitle_generator.py", "Subtitle Generator"),
    ("Scripts/Generators/metadata_generator.py", "Metadata Generator"),
    ("Scripts/Generators/thumbnail_generator.py", "Thumbnail Generator"),
    ("Scripts/Pipeline/video_editor.py", "Video Editor"),
]


def create_run_directory(run_name: str | None) -> Path:
    """Create or reuse a single output directory for one video run."""

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    if run_name:
        run_dir = Path(run_name)
        if not run_dir.is_absolute():
            run_dir = OUTPUT_ROOT / run_dir
    else:
        run_dir = OUTPUT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")

    run_dir = run_dir.resolve()

    try:
        run_dir.relative_to(OUTPUT_ROOT.resolve())
    except ValueError as error:
        raise ValueError(
            f"Run directory must be inside {OUTPUT_ROOT}."
        ) from error

    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_manifest(run_dir: Path, status: str, **extra: object) -> None:
    """Record the run state for troubleshooting and later review."""

    manifest = {
        "status": status,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(run_dir),
        **extra,
    }

    (run_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def run_script(
    relative_path: str,
    step_name: str,
    environment: dict[str, str],
) -> None:
    """Run one pipeline stage and stop the pipeline on failure."""

    script_path = PROJECT_ROOT / relative_path

    if not script_path.is_file():
        raise FileNotFoundError(
            f"{step_name} is missing: {script_path}"
        )

    logger.info("Starting: %s", step_name)

    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        env=environment,
        check=True,
    )

    logger.info("Completed: %s", step_name)


def run_pipeline(upload: bool, run_name: str | None) -> bool:
    """Run every production stage in the required order."""

    run_dir = create_run_directory(run_name)

    environment = os.environ.copy()
    environment[RUN_DIRECTORY_VARIABLE] = str(run_dir)

    write_manifest(
        run_dir,
        "running",
        upload_requested=upload,
        steps=[step_name for _, step_name in PIPELINE_STEPS],
    )

    logger.info("=" * 60)
    logger.info("YouTube automation started")
    logger.info("Run folder: %s", run_dir)
    logger.info("=" * 60)

    try:
        for relative_path, step_name in PIPELINE_STEPS:
            run_script(relative_path, step_name, environment)

        if upload:
            run_script(
                "Scripts/Pipeline/youtube_upload.py",
                "YouTube Upload",
                environment,
            )

        write_manifest(run_dir, "complete", upload_requested=upload)

        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info("Output: %s", run_dir)
        logger.info("=" * 60)
        return True

    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as error:
        write_manifest(
            run_dir,
            "failed",
            failed_step=str(error),
            upload_requested=upload,
        )
        logger.exception("Pipeline failed: %s", error)
        return False

    except Exception as error:
        write_manifest(
            run_dir,
            "failed",
            unexpected_error=str(error),
            upload_requested=upload,
        )
        logger.exception("Unexpected pipeline failure")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an automated YouTube Shorts video."
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload to YouTube after the video is created.",
    )
    parser.add_argument(
        "--run-name",
        help=(
            "Optional existing or custom folder name inside Output "
            "to resume a run."
        ),
    )

    args = parser.parse_args()

    success = run_pipeline(
        upload=args.upload,
        run_name=args.run_name,
    )

    raise SystemExit(0 if success else 1)


if __name__ == "__main__":
    main()
