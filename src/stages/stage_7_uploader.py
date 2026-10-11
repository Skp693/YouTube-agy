"""Stage 7: YouTube Data API v3 Video and Thumbnail Upload."""

import os
from pathlib import Path
from typing import Optional
from config.settings import settings
from src.models import ProjectState
from src.stages.base import BaseStage

class YouTubeUploadStage(BaseStage):
    """Uploads final video, sets thumbnail, and publishes metadata via YouTube Data API v3."""

    stage_number = 7
    stage_name = "youtube_upload"

    def validate_prerequisites(self, state: ProjectState) -> None:
        """Verify video, metadata, and thumbnail exist."""
        if not state.final_video_path or not Path(state.final_video_path).exists():
            raise ValueError("Cannot upload: final_video_path does not exist")
        if not state.metadata:
            raise ValueError("Cannot upload: metadata is missing")

    def execute(self, state: ProjectState) -> ProjectState:
        """Uploads video to YouTube or logs dry-run staging information."""
        secrets_file = settings.YOUTUBE_CLIENT_SECRETS_FILE

        if not settings.YOUTUBE_AUTO_UPLOAD:
            self.logger.info(
                "YOUTUBE_AUTO_UPLOAD is disabled. Video is ready in 'videos/' and metadata in 'metadata/'."
            )
            state.status = "completed"
            return state

        if not secrets_file.exists():
            self.logger.warning(
                f"YouTube client secrets file not found at '{secrets_file}'. "
                "Skipping live upload. Download your client_secrets.json from Google Cloud Console "
                "and place it in config/client_secrets.json to enable automatic uploads."
            )
            state.status = "completed"
            return state

        # Execute OAuth and upload
        try:
            video_id = self._upload_to_youtube(state)
            state.youtube_video_id = video_id
            state.youtube_video_url = f"https://youtu.be/{video_id}"
            state.status = "completed"
            self.logger.info(f"Video uploaded successfully! URL: {state.youtube_video_url}")
        except Exception as e:
            self.logger.error(f"YouTube upload failed: {e}")
            raise

        return state

    def validate_output(self, state: ProjectState) -> None:
        """Verify upload status."""
        self.logger.info(f"Pipeline finished with status: {state.status}")

    def _upload_to_youtube(self, state: ProjectState) -> str:
        """Performs Google API OAuth2 authentication and resumable upload."""
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        creds = None
        token_file = settings.YOUTUBE_TOKEN_FILE

        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(settings.YOUTUBE_CLIENT_SECRETS_FILE), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(token_file, "w") as token:
                token.write(creds.to_json())

        youtube = build("youtube", "v3", credentials=creds)

        # Upload video snippet and status
        body = {
            "snippet": {
                "title": state.metadata.title,
                "description": state.metadata.description,
                "tags": state.metadata.tags,
                "categoryId": state.metadata.category_id
            },
            "status": {
                "privacyStatus": state.metadata.privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(
            state.final_video_path,
            chunksize=-1,
            resumable=True,
            mimetype="video/mp4"
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = request.execute()
        video_id = response.get("id")

        # Upload custom thumbnail if exists
        if state.thumbnail_path and Path(state.thumbnail_path).exists():
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(state.thumbnail_path, mimetype="image/png")
                ).execute()
                self.logger.info("Custom thumbnail uploaded successfully.")
            except Exception as thumb_err:
                self.logger.warning(f"Thumbnail upload failed: {thumb_err}")

        return video_id
