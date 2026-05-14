"""
Storage clients — abstraction over local filesystem (dev) and S3 (production).

In local mode, upload URLs point to the /internal/upload/{session_id}/{filename}
endpoint, which mimics the S3 presigned PUT flow.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class StorageClient(ABC):
    @abstractmethod
    def get_upload_url(self, session_id: str, filename: str) -> str:
        pass

    @abstractmethod
    def save_image(self, session_id: str, filename: str, data: bytes) -> Path:
        pass

    @abstractmethod
    def get_image_path(self, session_id: str, filename: str) -> Optional[Path]:
        pass

    @abstractmethod
    def list_images(self, session_id: str) -> list[str]:
        pass


class LocalStorageClient(StorageClient):
    def __init__(self, base_path: str, api_base_url: str = "http://localhost:8000"):
        self.base_path = Path(base_path)
        self.api_base_url = api_base_url.rstrip("/")

    def _session_dir(self, session_id: str) -> Path:
        path = self.base_path / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_upload_url(self, session_id: str, filename: str) -> str:
        # Mimics a presigned URL — client PUTs image body directly to this endpoint
        return f"{self.api_base_url}/internal/upload/{session_id}/{filename}"

    def save_image(self, session_id: str, filename: str, data: bytes) -> Path:
        path = self._session_dir(session_id) / filename
        path.write_bytes(data)
        return path

    def get_image_path(self, session_id: str, filename: str) -> Optional[Path]:
        path = self._session_dir(session_id) / filename
        return path if path.exists() else None

    def list_images(self, session_id: str) -> list[str]:
        session_dir = self._session_dir(session_id)
        return [f.name for f in session_dir.iterdir() if f.is_file()]


class S3StorageClient(StorageClient):
    """Stub — to be implemented in Phase 2 (AWS deployment)."""

    def __init__(self, bucket: str, region: str):
        self.bucket = bucket
        self.region = region

    def get_upload_url(self, session_id: str, filename: str) -> str:
        raise NotImplementedError("S3 client not implemented yet")

    def save_image(self, session_id: str, filename: str, data: bytes) -> Path:
        raise NotImplementedError("S3 client not implemented yet")

    def get_image_path(self, session_id: str, filename: str) -> Optional[Path]:
        raise NotImplementedError("S3 client not implemented yet")

    def list_images(self, session_id: str) -> list[str]:
        raise NotImplementedError("S3 client not implemented yet")
