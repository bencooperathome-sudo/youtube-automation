from Scripts.APIs.pexels import search_videos

print("Searching Pexels...")

videos = search_videos("healthy food")

print()

print("Returned:", len(videos))

print()

for video in videos:

    print(video["url"])

print()

print("Finished.")