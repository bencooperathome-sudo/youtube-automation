"""Run the YouTube automation pipeline once per day."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAIN_FILE = PROJECT_ROOT / "main.py"


def run_pipeline(upload: bool) -> None:
    """Start one new production run."""

    command = [sys.executable, str(MAIN_FILE)]

    if upload:
        command.append("--upload")

    print(
        f"{datetime.now():%Y-%m-%d %H:%M:%S} | "
        "Starting scheduled pipeline run."
    )

    result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)

    if result.returncode == 0:
        print("Scheduled pipeline run completed successfully.")
    else:
        print(f"Scheduled pipeline run failed with code {result.returncode}.")


def validate_time(value: str) -> str:
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "Time must use 24-hour HH:MM format, for example 09:00."
        ) from error

    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Schedule one YouTube Shorts production run per day."
    )
    parser.add_argument(
        "--time",
        required=True,
        type=validate_time,
        help="Daily time in 24-hour HH:MM format.",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload the finished video after the production run.",
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run once immediately before starting the daily schedule.",
    )

    args = parser.parse_args()

    if args.run_now:
        run_pipeline(upload=args.upload)

    schedule.every().day.at(args.time).do(
        run_pipeline,
        upload=args.upload,
    )

    print(
        f"Scheduler running. Daily time: {args.time}. "
        "Keep this terminal window open."
    )

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()