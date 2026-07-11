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
You are an expert YouTube Shorts writer and fitness enthusiast.

Your task is to create ONE YouTube Shorts narration script about this topic:

TOPIC:
{first_topic}

GOAL:
Create a script that maximises viewer retention and feels like it was written by an experienced gaming YouTuber.

STRICT REQUIREMENTS

• Between 115 and 135 words.
• Around 30-35 seconds of narration.
• Every fact MUST be historically accurate according to official Blizzard lore or documented game mechanics.
• Never invent facts.
• Never speculate.
• Never use clickbait that is factually incorrect.
• Use conversational spoken English.
• No bullet points.
• No markdown.
• No emojis.
• No scene directions.
• No timestamps.
• Output ONLY the narration.

SCRIPT STRUCTURE

1. First sentence MUST immediately create curiosity.

Examples:
"Almost every WoW player has walked past this secret..."
"Blizzard accidentally created one of Warcraft's biggest mysteries..."
"Most players never realised this actually happened..."

2. Explain the background in one or two short sentences.

3. Reveal the surprising fact.

4. Explain why this matters in Warcraft lore or gameplay.

5. Finish with a sentence that makes viewers want more.

Example:
"If you enjoyed this fact, follow for another hidden World of Warcraft secret tomorrow."

WRITING STYLE

• Fast paced.
• High curiosity.
• Every sentence should encourage watching the next.
• Avoid repeating information.
• Sound like a knowledgeable gamer.
• Keep sentences short.
• Vary sentence length.
• Use vivid language.
• Avoid filler words.

QUALITY CHECK BEFORE RETURNING

Make sure:

✓ All facts are correct.
✓ No repeated information.
✓ Hook is strong.
✓ Easy for AI voice narration.
✓ Suitable for subtitles.
✓ Suitable for YouTube Shorts.

Return ONLY the finished narration.
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
