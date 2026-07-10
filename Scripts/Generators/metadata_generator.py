"""Generate metadata (title, description, hashtags) for YouTube video."""
from openai import OpenAI
from config import OPENAI_API_KEY
from settings import MODEL
from paths import SCRIPT, TITLE, DESCRIPTION, HASHTAGS

client = OpenAI(api_key=OPENAI_API_KEY)

with open(SCRIPT, "r", encoding="utf-8") as f:
    script = f.read()

prompt = f"""
Generate YouTube metadata for this WoW (World of Warcraft) fact video.

Script:
{script}

Generate:
1. A catchy, SEO-optimized TITLE (under 60 characters)
2. A detailed DESCRIPTION (2-3 sentences, include WoW lore/game context)
3. Relevant HASHTAGS (10-15 hashtags for WoW content)

Format your response exactly like this:
TITLE: [Your title here]
DESCRIPTION: [Your description here]
HASHTAGS: [hashtag1] [hashtag2] [hashtag3] ...
"""

print("Generating metadata...")

response = client.messages.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}]
)

metadata = response.choices[0].message.content

# Parse metadata
lines = metadata.strip().split("\n")
title_line = next((l for l in lines if l.startswith("TITLE:")), "").replace("TITLE:", "").strip()
desc_line = next((l for l in lines if l.startswith("DESCRIPTION:")), "").replace("DESCRIPTION:", "").strip()
tags_line = next((l for l in lines if l.startswith("HASHTAGS:")), "").replace("HASHTAGS:", "").strip()

print("Saving metadata...")

with open(TITLE, "w", encoding="utf-8") as f:
    f.write(title_line)

with open(DESCRIPTION, "w", encoding="utf-8") as f:
    f.write(desc_line)

with open(HASHTAGS, "w", encoding="utf-8") as f:
    f.write(tags_line)

print(f"✅ Metadata saved!")
print(f"Title: {title_line}")
print(f"Description: {desc_line}")
print(f"Hashtags: {tags_line}")




