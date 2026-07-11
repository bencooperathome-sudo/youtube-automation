from Scripts.APIs.pexels import search_videos
from Scripts.Pipeline.video_downloader import download_video

videos = search_videos("healthy food")

print(f"Found {len(videos)} videos")

download_video(videos[0])
