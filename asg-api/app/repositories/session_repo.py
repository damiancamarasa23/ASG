"""
Session repository — local JSON files (dev) / DynamoDB stub (production).
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings


class SessionRepo:
    def __init__(self):
        self._base = Path(settings.local_storage_path) / "sessions"
        self._base.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self._base / f"{session_id}.json"

    def create(self, session_id: str, consumer_platform_id: str, user_id: str, brand: str) -> dict:
        session = {
            "session_id": session_id,
            "consumer_platform_id": consumer_platform_id,
            "user_id": user_id,
            "brand": brand,
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "images": [],
        }
        self._path(session_id).write_text(json.dumps(session))
        return session

    def get(self, session_id: str) -> Optional[dict]:
        path = self._path(session_id)
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def update(self, session_id: str, **kwargs) -> Optional[dict]:
        session = self.get(session_id)
        if not session:
            return None
        session.update(kwargs)
        self._path(session_id).write_text(json.dumps(session))
        return session

    def add_image(self, session_id: str, filename: str) -> Optional[dict]:
        session = self.get(session_id)
        if not session:
            return None
        if filename not in session["images"]:
            session["images"].append(filename)
        self._path(session_id).write_text(json.dumps(session))
        return session
