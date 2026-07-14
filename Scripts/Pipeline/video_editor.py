"""Build a vertical YouTube Short from planned footage, narration, and subtitles."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from moviepy import AudioFileClip, VideoFileClip, concatenate_videoclips


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import (
    ASSETS_DIR,
    FINAL_VIDEO,
    SHOT_PLAN,
    SUBTITLES,
    VIDEO_WITH_SUBTITLES,
    VOICE,
)
from settings import VIDEO_FPS, VIDEO_HEIGHT, VIDEO_WIDTH


def load_shots() -> list[dict]:
    if not SHOT_PLAN.exists():
        raise FileNotFoundError(f"Shot plan not found: {SHOT_PLAN}")

    plan = json.loads(SHOT_PLAN.read_text(encoding="utf-8"))
    shots = plan.get("shots", [])

    if not shots:
        raise ValueError("Shot plan contains no shots.")

    return shots


def make_vertical_clip(source_file: Path, duration: float) -> VideoFileClip:
    """Scale and crop one source video to fill a 1080x1920 frame."""

    clip = VideoFileClip(str(source_file))

    if clip.duration < duration:
        clip.close()
        raise RuntimeError(
            f"{source_file.name} is too short ({clip.duration:.1f}s). "
            f"Required: {duration:.1f}s."
        )

    clip = clip.subclipped(0, duration)

    scale = max(VIDEO_WIDTH / clip.w, VIDEO_HEIGHT / clip.h)
    clip = clip.resized(scale)

    return clip.cropped(
        width=VIDEO_WIDTH,
        height=VIDEO_HEIGHT,
        x_center=clip.w / 2,
        y_center=clip.h / 2,
    )


def subtitle_filter_path(path: Path) -> str:
    """Escape a Windows path for FFmpeg's subtitles filter."""

    value = str(path.resolve()).replace("\\", "/")
    return value.replace(":", r"\:").replace("'", r"\'")


def main() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "FFmpeg is not available. Install FFmpeg and add it to PATH."
        )

    if not VOICE.exists():
        raise FileNotFoundError(f"Voice file not found: {VOICE}")

    if not SUBTITLES.exists():
        raise FileNotFoundError(f"Subtitle file not found: {SUBTITLES}")

    shots = load_shots()
    clips: list[VideoFileClip] = []

    try:
        print("Preparing footage...")

        for shot in shots:
            shot_number = int(shot["shot_number"])
            source_file = ASSETS_DIR / f"shot_{shot_number:02d}.mp4"

            if not source_file.exists():
                raise FileNotFoundError(
                    f"Missing footage for shot {shot_number}: {source_file}"
                )

            duration = (
                float(shot["end_seconds"])
                - float(shot["start_seconds"])
            )

            clips.append(make_vertical_clip(source_file, duration))

        video = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(str(VOICE))

        if video.duration < audio.duration:
            raise RuntimeError(
                "Footage is shorter than the narration. "
                "Create a longer shot plan or download longer clips."
            )

        video = video.subclipped(0, audio.duration).with_audio(audio)

        print("Writing video...")
        video.write_videofile(
            str(FINAL_VIDEO),
            fps=VIDEO_FPS,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        )

        video.close()
        audio.close()

        print("Burning subtitles...")

        filter_value = (
            f"subtitles=filename='{subtitle_filter_path(SUBTITLES)}':"
            "charenc=UTF-8"
        )

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(FINAL_VIDEO),
                "-vf",
                filter_value,
                "-c:a",
                "copy",
                "-movflags",
                "+faststart",
                str(VIDEO_WITH_SUBTITLES),
            ],
            check=True,
        )

        print(f"Final video saved to: {VIDEO_WITH_SUBTITLES}")

    finally:
        for clip in clips:
            clip.close()


if __name__ == "__main__":
    main()