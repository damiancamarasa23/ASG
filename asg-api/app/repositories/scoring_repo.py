"""
Scoring repository — local JSON files (dev) / DynamoDB stub (production).
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings


class ScoringRepo:
    def __init__(self):
        self._base = Path(settings.local_storage_path) / "scoring"
        self._base.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self._base / f"{session_id}.json"

    def create(self, session_id: str) -> dict:
        result = {
            "session_id": session_id,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "final_score": None,
            "criteria": [],
            "overall_observations": None,
            "error": None,
        }
        self._path(session_id).write_text(json.dumps(result))
        return result

    def get(self, session_id: str) -> Optional[dict]:
        path = self._path(session_id)
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def update(self, session_id: str, **kwargs) -> Optional[dict]:
        result = self.get(session_id)
        if not result:
            return None
        result.update(kwargs)
        self._path(session_id).write_text(json.dumps(result))
        return result
