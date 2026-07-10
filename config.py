"""Configuration file for YouTube Shorts automation."""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")
if not PEXELS_API_KEY:
    raise ValueError("PEXELS_API_KEY not found in .env file")
