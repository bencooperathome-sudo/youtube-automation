"""Settings and models for YouTube Shorts generation."""

# OpenAI Configuration
MODEL = "gpt-4o-mini"
VOICE = "alloy"  # Options: alloy, echo, fused, onyx, nova, shimmer

# Video Configuration
VIDEO_DURATION_SECONDS = 35
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# Content Type (can be 'wow', 'fitness', 'geography', etc.)
CONTENT_TYPE = "facts"

FACT_CATEGORIES = [
    "Science",
    "History",
    "Space",
    "Nature",
    "Geography",
    "Technology",
    "Psychology",
    "Human Body",
    "Animals",
    "Economics"
]

# WoW-Specific Settings
WOW_TOPICS = [
    "World of Warcraft lore",
    "WoW raids and dungeons",
    "WoW character builds",
    "WoW economy and gold making",
    "WoW PvP strategies",
    "WoW expansions history",
    "WoW Easter eggs",
    "WoW achievements",
]
