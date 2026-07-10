"""Generate voice narration using OpenAI TTS."""
from openai import OpenAI
from config import OPENAI_API_KEY
from settings import VOICE
from paths import SCRIPT, VOICE as VOICE_OUTPUT

client = OpenAI(api_key=OPENAI_API_KEY)

print("Loading script...")
with open(SCRIPT, "r", encoding="utf-8") as f:
    script = f.read()

print("✅ Script loaded!")
print("Generating voice...")

response = client.audio.speech.create(
    model="tts-1",
    voice=VOICE,
    input=script,
)

print("Voice generated!")
response.write_to_file(VOICE_OUTPUT)

print(f"✅ Voice saved to {VOICE_OUTPUT}")