"""
Fact checks generated YouTube Shorts scripts using OpenAI.
"""

from openai import OpenAI

from config import OPENAI_API_KEY
from settings import MODEL
from paths import SCRIPT

client = OpenAI(api_key=OPENAI_API_KEY)

print("Loading script...")

with open(SCRIPT, "r", encoding="utf-8") as f:
    script = f.read()

prompt = f"""
You are a professional fact checker.

Review this YouTube Shorts narration.

SCRIPT

{script}

Your job is to verify every factual claim.

For each claim:

• Is it true?
• Is it misleading?
• Is it unverifiable?
• Does it exaggerate?

If everything is accurate reply exactly:

PASS

If there are problems reply in this format:

FAIL

Reason:
...

Corrected Script:

...

Only rewrite the script if necessary.
"""

print("Checking facts...")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

result = response.choices[0].message.content

print(result)

if result.startswith("PASS"):
    print("✅ Script passed fact checking.")

else:
    print("❌ Script requires correction.")