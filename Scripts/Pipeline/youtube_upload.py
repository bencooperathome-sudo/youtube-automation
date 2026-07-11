"""Upload video to YouTube."""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from paths import TITLE, DESCRIPTION, VIDEO_WITH_SUBTITLES, HASHTAGS

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def authenticate():
    """Authenticate with Google API."""
    credentials = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

    if not credentials:
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json",
            SCOPES
        )

        credentials = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)


def upload_video():
    """Upload video to YouTube."""
    
    print("Reading title...")
    with open(TITLE, "r", encoding="utf-8") as f:
        title = f.read().strip()

    print("Reading description...")
    with open(DESCRIPTION, "r", encoding="utf-8") as f:
        description = f.read().strip()

    print("Reading hashtags...")
    with open(HASHTAGS, "r", encoding="utf-8") as f:
        hashtags = f.read().strip()

    # Append hashtags to description
    full_description = f"{description}\n\n{hashtags}"

    youtube = authenticate()

    print("Uploading video...")

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": full_description,
                "categoryId": "27"  # Gaming category
            },
            "status": {
                "privacyStatus": "private",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(
            str(VIDEO_WITH_SUBTITLES),
            chunksize=-1,
            resumable=True
        )
    )

    response = request.execute()

    print("✅ Upload complete!")
    print(f"Video ID: {response['id']}")
    print(f"URL: https://www.youtube.com/watch?v={response['id']}")


if __name__ == "__main__":
    upload_video()