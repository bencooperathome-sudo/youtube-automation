"""Generate narration script for YouTube Short."""
from settings import MODEL
from openai import OpenAI
from config import OPENAI_API_KEY
from paths import OUTPUT_DIR, SCRIPT

client = OpenAI(api_key=OPENAI_API_KEY)

# Read topic
topics_file = OUTPUT_DIR / "topics.txt"
with open(topics_file, "r", encoding="utf-8") as f:
    first_topic = f.readline().strip()

prompt = f"""
You are an expert YouTube Shorts script writer.

Topic: {first_topic}

Create a 20–30 second YouTube Short script about World of Warcraft.

Requirements:
- Start with an irresistible hook in the first sentence
- Keep every sentence under 15 words
- Build curiosity throughout
- Be accurate about WoW lore, mechanics, or facts
- Explain simply enough for anyone to understand
- End with: "Follow for more WoW facts!"
- Return only the narration (no stage directions)
"""

print(f"Generating script for topic: {first_topic}...")

response = client.messages.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}]
)

print("✅ OpenAI response received.")

script = response.choices[0].message.content

print("Saving script...")

with open(SCRIPT, "w", encoding="utf-8") as f:
    f.write(script)

print(f"✅ Script saved to {SCRIPT}")
