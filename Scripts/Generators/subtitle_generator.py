"""Generate SRT subtitles for the script."""
from openai import OpenAI
from config import OPENAI_API_KEY
from paths import SCRIPT, SUBTITLES

client = OpenAI(api_key=OPENAI_API_KEY)

with open(SCRIPT, "r", encoding="utf-8") as f:
    script = f.read()

prompt = f"""
Create subtitles in SRT format for this script.

Script:
{script}

Requirements:
- Standard .srt format with numbering
- Each subtitle 2-4 seconds duration
- Match the spoken words exactly
- Proper timing for sync with voice
- Return ONLY the SRT content

Example format:
1
00:00:00,000 --> 00:00:03,000
First subtitle line

2
00:00:03,000 --> 00:00:06,000
Second subtitle line
"""

print("Generating subtitles...")

response = client.messages.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

subtitles = response.choices[0].message.content

with open(SUBTITLES, "w", encoding="utf-8") as f:
    f.write(subtitles)

print(f"✅ Subtitles saved to {SUBTITLES}")