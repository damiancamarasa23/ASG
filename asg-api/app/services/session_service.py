import uuid
from typing import Optional

from app.clients.storage_client import StorageClient
from app.repositories.session_repo import SessionRepo


class SessionService:
    def __init__(self, session_repo: SessionRepo, storage_client: StorageClient):
        self.session_repo = session_repo
        self.storage_client = storage_client

    def create_session(self, consumer_platform_id: str, user_id: str, brand: str) -> dict:
        session_id = str(uuid.uuid4())[:8].upper()
        return self.session_repo.create(session_id, consumer_platform_id, user_id, brand)

    def get_upload_url(self, session_id: str, filename: str) -> Optional[dict]:
        session = self.session_repo.get(session_id)
        if not session:
            return None
        upload_url = self.storage_client.get_upload_url(session_id, filename)
        return {"upload_url": upload_url, "filename": filename}

    def confirm_upload(self, session_id: str, filename: str) -> Optional[dict]:
        session = self.session_repo.add_image(session_id, filename)
        if not session:
            return None
        image_path = self.storage_client.get_image_path(session_id, filename)
        return {
            "session_id": session_id,
            "filename": filename,
            "confirmed": image_path is not None,
        }
