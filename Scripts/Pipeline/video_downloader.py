import os
import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

if not PEXELS_API_KEY:
    raise ValueError("PEXELS_API_KEY not found in .env file.")

HEADERS = {
    "Authorization": str(PEXELS_API_KEY)
}


def search_videos(query, per_page=5):

    url = "https://api.pexels.com/videos/search"

    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "portrait"
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params
    )

    response.raise_for_status()

    data = response.json()

    return data["videos"]


def download_video(video, save_folder="Downloaded_Videos"):

    os.makedirs(save_folder, exist_ok=True)

    best_quality = max(
        video["video_files"],
        key=lambda x: x.get("width", 0)
    )

    file_url = best_quality["link"]

    filename = os.path.join(
        save_folder,
        f'{video["id"]}.mp4'
    )

    print("Downloading")
    print(filename)

    response = requests.get(file_url, stream=True)
    response.raise_for_status()

    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return filename