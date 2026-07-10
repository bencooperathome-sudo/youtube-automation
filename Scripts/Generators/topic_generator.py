"""
Generate daily WoW facts for YouTube Shorts.
"""

import random
from pathlib import Path

from openai import OpenAI

from config import OPENAI_API_KEY
from paths import OUTPUT_DIR
from settings import MODEL, WOW_TOPICS


# ----------------------------------------
# OpenAI Client
# ----------------------------------------

client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------------------------
# Output file
# ----------------------------------------

output_file = Path(OUTPUT_DIR) / "topics.txt"

# Make sure the output directory exists
output_file.parent.mkdir(parents=True, exist_ok=True)

# ----------------------------------------
# Choose a random topic
# ----------------------------------------

selected_topic = random.choice(WOW_TOPICS)

prompt = f"""
Generate 5 viral, engaging World of Warcraft facts for YouTube Shorts.

Topic:
{selected_topic}

Requirements:
- Each fact should be a complete YouTube Short idea.
- Amazing, surprising WoW facts.
- Under 35 seconds of narration.
- High curiosity and engagement.
- Include lore, mechanics or little-known details.
- One fact per line.
- Format:

[FACT]: [Engaging description]

Make every fact highly viral and interesting.
"""

print(f"Generating WoW topics for: {selected_topic}...")

# ----------------------------------------
# Generate topics
# ----------------------------------------

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
)

topics = response.choices[0].message.content

if not topics:
    raise RuntimeError("OpenAI returned no content.")

# ----------------------------------------
# Save file
# ----------------------------------------

output_file.write_text(topics, encoding="utf-8")

print(f"✅ Topics saved to: {output_file}")

print("Step 1 - Imports successful")
print("Step 2 - Client created")
print("Step 3 - Prompt created")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": prompt}
    ],
)

print("Step 4 - OpenAI responded")

topics = response.choices[0].message.content

print("Step 5 - Topics extracted")

output_file.write_text(topics, encoding="utf-8")

print("Step 6 - File saved")