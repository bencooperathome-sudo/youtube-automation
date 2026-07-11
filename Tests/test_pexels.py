import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PEXELS_API_KEY")

headers = {
    "Authorization": API_KEY
}

response = requests.get(
    "https://api.pexels.com/videos/search",
    headers=headers,
    params={
        "query": "healthy food",
        "per_page": 3
    }
)

print("Status:", response.status_code)

if response.status_code == 200:

    videos = response.json()["videos"]

    print(f"\nFound {len(videos)} videos\n")

    for video in videos:

        print(video["url"])

else:

    print(response.text)