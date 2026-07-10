"""Download background video clips from Pexels API."""
import os
import requests
from config import PEXELS_API_KEY
from paths import OUTPUT_DIR, ASSETS_DIR

# Read first topic
topics_file = OUTPUT_DIR / "topics.txt"
with open(topics_file, "r", encoding="utf-8") as f:
    topic = f.readline().strip()

print(f"Searching Pexels for: {topic}")

url = "https://api.pexels.com/videos/search"

headers = {
    "Authorization": PEXELS_API_KEY
}

params = {
    "query": topic,
    "per_page": 8,
    "orientation": "portrait"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if "videos" not in data or not data["videos"]:
    print(f"⚠️  No videos found for '{topic}'")
    print("Using generic 'gaming' videos as fallback...")
    params["query"] = "gaming"
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

# Create Assets folder if it doesn't exist
os.makedirs(ASSETS_DIR, exist_ok=True)

# Delete old clips
for file in os.listdir(ASSETS_DIR):
    if file.endswith(".mp4"):
        os.remove(os.path.join(ASSETS_DIR, file))
        print(f"Removed old: {file}")

count = 1

for video in data.get("videos", []):

    # Prefer Full HD videos
    video_files = [
        vf for vf in video["video_files"]
        if vf["width"] >= 1080
    ]

    # If no Full HD version exists, use the best available
    if not video_files:
        video_files = video["video_files"]

    best_video = max(
        video_files,
        key=lambda x: x["width"] * x["height"]
    )

    print(
        f"Downloading clip {count} "
        f"({best_video['width']}x{best_video['height']})"
    )

    video_url = best_video["link"]

    video_data = requests.get(video_url).content

    output_file = os.path.join(ASSETS_DIR, f"clip{count}.mp4")
    with open(output_file, "wb") as f:
        f.write(video_data)

    count += 1

print(f"✅ Downloaded {count-1} videos to {ASSETS_DIR}")