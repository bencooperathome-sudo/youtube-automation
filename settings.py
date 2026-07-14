"""Settings for the automated Interesting Facts YouTube Shorts channel."""

# OpenAI
MODEL = "gpt-4o-mini"
VOICE = "alloy"
IMAGE_MODEL = "gpt-image-2"

# Video format
VIDEO_DURATION_SECONDS = 35
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# Channel direction
CONTENT_TYPE = "interesting_facts"
TARGET_AUDIENCE = "Curious viewers looking for short, surprising, accurate facts."

# Categories used by the topic generator
FACT_CATEGORIES = [
    "Science and surprising discoveries",
    "Space and astronomy",
    "Human body and health facts",
    "Animals and nature",
    "World history",
    "Geography and unusual places",
    "Psychology and human behaviour",
    "Technology and inventions",
    "Food and culture",
    "Everyday objects and hidden history",
]

# Content rules used by future pipeline stages
CONTENT_REQUIREMENTS = [
    "Prioritise accurate and verifiable facts.",
    "Avoid medical, financial, or legal advice.",
    "Avoid divisive political topics.",
    "Avoid graphic, disturbing, or sensational content.",
    "Explain one interesting idea clearly in each video.",
    "Use simple language suitable for a broad audience.",
]
