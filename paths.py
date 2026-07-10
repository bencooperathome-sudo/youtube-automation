"""File paths for the project."""
import os
from datetime import datetime
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "Output" / datetime.now().strftime("%Y%m%d_%H%M%S")
ASSETS_DIR = BASE_DIR / "Assets"
LOGS_DIR = BASE_DIR / "Logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Output files
TOPIC = OUTPUT_DIR / "topic.txt"
SCRIPT = OUTPUT_DIR / "script.txt"
VOICE = OUTPUT_DIR / "voice.mp3"
SUBTITLES = OUTPUT_DIR / "subtitles.srt"
TITLE = OUTPUT_DIR / "title.txt"
DESCRIPTION = OUTPUT_DIR / "description.txt"
HASHTAGS = OUTPUT_DIR / "hashtags.txt"
FINAL_VIDEO = OUTPUT_DIR / "final_video.mp4"
VIDEO_WITH_SUBTITLES = OUTPUT_DIR / "video_with_subtitles.mp4"

# Log files
LOG_FILE = LOGS_DIR / f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Prompts directory
PROMPTS_DIR = BASE_DIR / "Prompts"

print(f"✅ Output directory: {OUTPUT_DIR}")
