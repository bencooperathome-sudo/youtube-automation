"""
Download one portrait stock-video clip for each shot in shot_plan.json.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import ASSETS_DIR, OUTPUT_DIR, SHOT_PLAN


PEXELS_SEARCH_URL = "https://api.pexels.com/v1/videos/search"
REQUEST_TIMEOUT_SECONDS = 45
DOWNLOAD_TIMEOUT_SECONDS = 180
SEARCH_RESULTS_PER_SHOT = 10

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def get_pexels_headers() -> dict[str, str]:
    """Load the Pexels API key from the project's .env file."""

    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("PEXELS_API_KEY")

    if not api_key:
        raise RuntimeError(
            "PEXELS_API_KEY is missing from the project's .env file."
        )

    return {"Authorization": api_key}


def load_shot_plan() -> dict[str, Any]:
    """Load the plan created by shot_planner.py."""

    if not SHOT_PLAN.exists():
        raise FileNotFoundError(
            f"Shot plan not found: {SHOT_PLAN}. Run shot_planner.py first."
        )

    plan = json.loads(SHOT_PLAN.read_text(encoding="utf-8"))

    if not plan.get("shots"):
        raise ValueError("shot_plan.json does not contain any shots.")

    return plan


def search_videos(query: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    """Search Pexels for portrait stock-video footage."""

    response = requests.get(
        PEXELS_SEARCH_URL,
        headers=headers,
        params={
            "query": query,
            "orientation": "portrait",
            "size": "medium",
            "per_page": SEARCH_RESULTS_PER_SHOT,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    return response.json().get("videos", [])


def choose_best_video(
    videos: list[dict[str, Any]],
    required_duration: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Choose a usable MP4 video file, preferring portrait HD footage."""

    candidates: list[tuple[tuple[float, float, float], dict, dict]] = []

    for video in videos:
        duration = float(video.get("duration", 0))

        for video_file in video.get("video_files", []):
            if video_file.get("file_type") != "video/mp4":
                continue

            width = int(video_file.get("width") or 0)
            height = int(video_file.get("height") or 0)

            if width <= 0 or height <= 0 or not video_file.get("link"):
                continue

            portrait_score = 1 if height > width else 0
            quality_score = 1 if video_file.get("quality") == "hd" else 0
            enough_duration_score = 1 if duration >= required_duration else 0
            resolution_score = width * height

            score = (
                enough_duration_score,
                portrait_score + quality_score,
                resolution_score,
            )
            candidates.append((score, video, video_file))

    if not candidates:
        raise RuntimeError("Pexels returned no usable MP4 files.")

    _, selected_video, selected_file = max(candidates, key=lambda item: item[0])
    return selected_video, selected_file


def download_video(
    url: str,
    destination: Path,
) -> None:
    """Download one video file safely to the current run's assets folder."""

    temporary_file = destination.with_suffix(".part")

    with requests.get(
        url,
        stream=True,
        timeout=DOWNLOAD_TIMEOUT_SECONDS,
    ) as response:
        response.raise_for_status()

        with temporary_file.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)

    if not temporary_file.exists() or temporary_file.stat().st_size == 0:
        raise RuntimeError(f"Download failed or was empty: {destination.name}")

    temporary_file.replace(destination)


def find_video_for_shot(
    shot: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any], str]:
    """Search using the planned query, then safe fallback queries if needed."""

    required_duration = (
        float(shot["end_seconds"]) - float(shot["start_seconds"])
    )

    queries = [
        shot["search_query"],
        "cinematic technology",
        "abstract motion background",
    ]

    for query in queries:
        try:
            videos = search_videos(query, headers)

            if videos:
                video, video_file = choose_best_video(
                    videos,
                    required_duration,
                )
                return video, video_file, query

        except requests.RequestException as error:
            logger.warning("Pexels search failed for %r: %s", query, error)

    raise RuntimeError(
        f"No usable Pexels footage found for shot {shot['shot_number']}."
    )


def save_attribution(records: list[dict[str, Any]]) -> None:
    """Save source and creator details for proper Pexels attribution."""

    manifest_file = OUTPUT_DIR / "footage_manifest.json"
    credits_file = OUTPUT_DIR / "pexels_attribution.txt"

    manifest_file.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    credit_lines = ["Stock footage provided by Pexels.", ""]

    for record in records:
        credit_lines.append(
            f"Shot {record['shot_number']}: "
            f"{record['creator_name']} — {record['video_url']}"
        )

    credits_file.write_text(
        "\n".join(credit_lines) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    logger.info("Starting video download.")

    plan = load_shot_plan()
    headers = get_pexels_headers()

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []

    for shot in plan["shots"]:
        shot_number = int(shot["shot_number"])
        destination = ASSETS_DIR / f"shot_{shot_number:02d}.mp4"

        if destination.exists() and destination.stat().st_size > 0:
            logger.info("Reusing existing clip: %s", destination.name)
            continue

        video, video_file, used_query = find_video_for_shot(shot, headers)

        logger.info(
            "Downloading shot %s using query %r.",
            shot_number,
            used_query,
        )

        download_video(video_file["link"], destination)

        creator = video.get("user", {})

        records.append(
            {
                "shot_number": shot_number,
                "local_file": str(destination),
                "search_query": used_query,
                "video_id": video.get("id"),
                "video_url": video.get("url"),
                "creator_name": creator.get("name", "Unknown creator"),
                "creator_url": creator.get("url"),
                "duration_seconds": video.get("duration"),
            }
        )

        logger.info("Saved: %s", destination)

    save_attribution(records)

    logger.info("Video download complete.")
    logger.info("Assets folder: %s", ASSETS_DIR)


if __name__ == "__main__":
    main()