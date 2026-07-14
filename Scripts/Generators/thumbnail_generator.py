"""Generate an accurate, high-impact YouTube thumbnail for the current run."""

from __future__ import annotations

import base64
import io
import os
import sys
from pathlib import Path
from typing import Literal, cast

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import SCRIPT, THUMBNAIL, TITLE
from settings import IMAGE_MODEL


YOUTUBE_SIZE = (1280, 720)
MAX_FILE_SIZE = 2 * 1024 * 1024
ImageQuality = Literal["standard", "hd", "low", "medium", "high", "auto"]
VALID_IMAGE_QUALITIES = {"standard", "hd", "low", "medium", "high", "auto"}


def read_required(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Required thumbnail input not found: {path}")
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise ValueError(f"Required thumbnail input is empty: {path}")
    return value


def get_image_quality() -> ImageQuality:
    value = os.getenv("THUMBNAIL_QUALITY", "medium").strip().lower()
    if value not in VALID_IMAGE_QUALITIES:
        choices = ", ".join(sorted(VALID_IMAGE_QUALITIES))
        raise ValueError(f"THUMBNAIL_QUALITY must be one of: {choices}.")
    return cast(ImageQuality, value)


def build_prompt(title: str, script: str) -> str:
    return f"""
Create a bold, curiosity-driven YouTube thumbnail for this factual Short.

TITLE: {title}
NARRATION: {script}

Requirements:
- Depict the single most surprising concrete subject from the narration.
- Dramatic lighting, vivid contrast, crisp detail, and a clear focal point.
- Compose for a 16:9 crop, keeping important details in the central 80%.
- Add one short, highly legible hook of 2 to 4 words in large bold lettering.
- The hook must be truthful and supported by the narration; no invented claims.
- Keep the layout uncluttered and readable on a phone.
- No logos, watermarks, UI, borders, gore, or unrelated objects.
""".strip()


def crop_to_youtube(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    target_ratio = YOUTUBE_SIZE[0] / YOUTUBE_SIZE[1]
    source_ratio = image.width / image.height

    if source_ratio > target_ratio:
        width = round(image.height * target_ratio)
        left = (image.width - width) // 2
        image = image.crop((left, 0, left + width, image.height))
    else:
        height = round(image.width / target_ratio)
        top = (image.height - height) // 2
        image = image.crop((0, top, image.width, top + height))

    return image.resize(YOUTUBE_SIZE, Image.Resampling.LANCZOS)


def save_jpeg(image: Image.Image) -> None:
    for quality in (92, 86, 80, 74):
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=quality, optimize=True, progressive=True)
        if buffer.tell() <= MAX_FILE_SIZE:
            THUMBNAIL.write_bytes(buffer.getvalue())
            return
    raise ValueError("Thumbnail could not be compressed below YouTube's 2 MB limit.")


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing from .env.")

    title = read_required(TITLE)
    script = read_required(SCRIPT)
    result = OpenAI(api_key=api_key).images.generate(
        model=os.getenv("OPENAI_IMAGE_MODEL", IMAGE_MODEL),
        prompt=build_prompt(title, script),
        size="1536x1024",
        quality=get_image_quality(),
        output_format="png",
    )

    if not result.data or not result.data[0].b64_json:
        raise RuntimeError("The image API returned no thumbnail data.")

    raw_image = base64.b64decode(result.data[0].b64_json)
    with Image.open(io.BytesIO(raw_image)) as generated:
        save_jpeg(crop_to_youtube(generated))

    print(f"Thumbnail generated: {THUMBNAIL}")


if __name__ == "__main__":
    main()
