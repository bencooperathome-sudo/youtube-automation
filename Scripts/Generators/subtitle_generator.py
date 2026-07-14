"""Create timed SRT subtitles from narration text and generated audio."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from moviepy import AudioFileClip


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import SCRIPT, SUBTITLES, VOICE


MAX_WORDS_PER_CAPTION = 7


def srt_timestamp(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)

    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def split_captions(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    captions: list[str] = []

    for sentence in sentences:
        words = sentence.split()

        while words:
            captions.append(" ".join(words[:MAX_WORDS_PER_CAPTION]))
            words = words[MAX_WORDS_PER_CAPTION:]

    return [caption for caption in captions if caption]


def format_caption(caption: str) -> str:
    words = caption.split()

    if len(words) <= 4:
        return caption

    midpoint = len(words) // 2
    return " ".join(words[:midpoint]) + "\n" + " ".join(words[midpoint:])


def main() -> None:
    if not SCRIPT.exists():
        raise FileNotFoundError(f"Script not found: {SCRIPT}")

    if not VOICE.exists():
        raise FileNotFoundError(
            f"Voice file not found: {VOICE}. Run voice_generator.py first."
        )

    script = SCRIPT.read_text(encoding="utf-8").strip()
    captions = split_captions(script)

    if not captions:
        raise ValueError("No captions could be created from the script.")

    audio = AudioFileClip(str(VOICE))
    total_duration = audio.duration
    audio.close()

    total_words = sum(len(caption.split()) for caption in captions)
    current_time = 0.0
    srt_blocks: list[str] = []

    for number, caption in enumerate(captions, start=1):
        word_count = len(caption.split())
        duration = total_duration * (word_count / total_words)
        end_time = min(current_time + duration, total_duration)

        srt_blocks.append(
            f"{number}\n"
            f"{srt_timestamp(current_time)} --> {srt_timestamp(end_time)}\n"
            f"{format_caption(caption)}\n"
        )

        current_time = end_time

    SUBTITLES.write_text(
        "\n".join(srt_blocks),
        encoding="utf-8",
    )

    print(f"Subtitles saved to: {SUBTITLES}")


if __name__ == "__main__":
    main()