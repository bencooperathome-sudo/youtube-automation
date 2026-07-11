"""
Main entry point for the YouTube Shorts automation project.
Runs each stage of the pipeline in sequence.
"""

import subprocess
import sys
import logging
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------
# Project Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent

LOGS_DIR = PROJECT_ROOT / "Logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOGS_DIR / f"automation_{datetime.now():%Y%m%d_%H%M%S}.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def run_script(relative_path: str, step_name: str):
    """
    Execute a Python script and stop if it fails.
    """

    script = PROJECT_ROOT / relative_path

    if not script.exists():
        raise FileNotFoundError(f"Cannot find: {script}")

    logger.info(f"Running {step_name}")

    subprocess.run(
        [sys.executable, str(script)],
        check=True
    )

    logger.info(f"{step_name} completed.")


# ---------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------

def run_pipeline(upload=False):

    logger.info("=" * 60)
    logger.info("YouTube Shorts Automation Started")
    logger.info("=" * 60)

    try:

        run_script(
            "Scripts/Generators/topic_generator.py",
            "Topic Generator"
        )

        run_script(
            "Scripts/Pipeline/video_downloader.py",
            "Video Downloader"
        )

        run_script(
            "Scripts/Generators/script_generator.py",
            "Script Generator"
        )

        run_script(
            "Scripts/Generators/fact_checker.py",
            "Fact Checker"
         )

        run_script(
            "Scripts/Generators/quality_scorer.py",
            "Quality Scorer"
         )

        run_script(
           "Scripts/Generators/voice_generator.py",
           "Voice Generator"
         )

        run_script(
            "Scripts/Generators/subtitle_generator.py",
            "Subtitle Generator"
        )

        run_script(
            "Scripts/Generators/metadata_generator.py",
            "Metadata Generator"
        )

        run_script(
            "Scripts/Pipeline/video_editor.py",
            "Video Editor"
        )

        if upload:

            run_script(
                "Scripts/Pipeline/youtube_upload.py",
                "YouTube Upload"
            )

        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 60)

        return True

    except subprocess.CalledProcessError as e:

        logger.exception(f"Script failed with exit code {e.returncode}")
        return False

    except Exception:

        logger.exception("Unexpected error")
        return False


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload to YouTube after creating the video."
    )

    args = parser.parse_args()

    success = run_pipeline(upload=args.upload)

    sys.exit(0 if success else 1)