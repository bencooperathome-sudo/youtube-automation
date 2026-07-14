"""Upload a completed video to YouTube as private by default."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import (
    DESCRIPTION,
    HASHTAGS,
    KEYWORDS,
    OUTPUT_DIR,
    TITLE,
    THUMBNAIL,
    VIDEO_WITH_SUBTITLES,
)


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = PROJECT_ROOT / "client_secret.json"
TOKEN_FILE = PROJECT_ROOT / "youtube_token.json"
PRIVACY_STATUS = os.getenv("YOUTUBE_PRIVACY", "private")


def authenticate():
    """Authenticate once in a browser, then reuse the saved token."""

    credentials = None

    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        if not CLIENT_SECRET_FILE.exists():
            raise FileNotFoundError(
                "client_secret.json is missing from the project root."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            SCOPES,
        )
        credentials = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")

    return build("youtube", "v3", credentials=credentials)


def read_required_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    value = path.read_text(encoding="utf-8").strip()

    if not value:
        raise ValueError(f"Required file is empty: {path}")

    return value


def main() -> None:
    if PRIVACY_STATUS not in {"private", "unlisted", "public"}:
        raise ValueError(
            "YOUTUBE_PRIVACY must be private, unlisted, or public."
        )

    if not VIDEO_WITH_SUBTITLES.exists():
        raise FileNotFoundError(
            f"Final video not found: {VIDEO_WITH_SUBTITLES}"
        )

    title = read_required_file(TITLE)
    description = read_required_file(DESCRIPTION)
    hashtags = read_required_file(HASHTAGS)
    keywords = read_required_file(KEYWORDS)

    full_description = (
        f"{description}\n\n{hashtags}\n\n"
        "Narration in this video uses an AI-generated voice.\n"
        "Stock footage provided by Pexels."
    )

    tags = [
        item.strip()
        for item in keywords.split(",")
        if item.strip()
    ]

    youtube = authenticate()

    print(f"Uploading as: {PRIVACY_STATUS}")

    request = youtube.videos().insert(
        part="snippet,status",
        notifySubscribers=False,
        body={
            "snippet": {
                "title": title[:100],
                "description": full_description,
                "tags": tags,
                "categoryId": "27",
            },
            "status": {
                "privacyStatus": PRIVACY_STATUS,
                "selfDeclaredMadeForKids": False,
                "containsSyntheticMedia": True,
            },
        },
        media_body=MediaFileUpload(
            str(VIDEO_WITH_SUBTITLES),
            mimetype="video/mp4",
            resumable=True,
        ),
    )

    response = request.execute()

    thumbnail_uploaded = False
    if THUMBNAIL.exists():
        youtube.thumbnails().set(
            videoId=response["id"],
            media_body=MediaFileUpload(
                str(THUMBNAIL),
                mimetype="image/jpeg",
                resumable=False,
            ),
        ).execute()
        thumbnail_uploaded = True

    result = {
        "video_id": response["id"],
        "url": f"https://www.youtube.com/watch?v={response['id']}",
        "privacy_status": PRIVACY_STATUS,
        "thumbnail_uploaded": thumbnail_uploaded,
    }

    (OUTPUT_DIR / "youtube_upload_result.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print(f"Upload complete: {result['url']}")


if __name__ == "__main__":
    main()
