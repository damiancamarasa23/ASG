"""
Scoring service — orchestrates parallel image analysis and score aggregation.

Each criterion is scored concurrently via asyncio.gather + asyncio.to_thread
(since the vision clients use blocking HTTP calls).
"""

import asyncio
import json
import pathlib
from pathlib import Path
from typing import Optional

from app.clients.storage_client import StorageClient
from app.clients.vision_client import VisionClient
from app.repositories.scoring_repo import ScoringRepo
from app.repositories.session_repo import SessionRepo

PRODUCTS_PATH = pathlib.Path(__file__).parent.parent.parent / "gucci" / "products.json"


def _active_criteria(all_criteria: list, product_id: Optional[str]) -> list:
    if not product_id:
        return all_criteria
    try:
        products = json.loads(PRODUCTS_PATH.read_text())
        active_keys = set(products[product_id]["criteria"])
        return [c for c in all_criteria if c["key"] in active_keys]
    except (KeyError, FileNotFoundError):
        return all_criteria

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _find_image(storage: StorageClient, session_id: str, filename_base: str) -> Optional[Path]:
    for ext in SUPPORTED_EXTENSIONS:
        path = storage.get_image_path(session_id, f"{filename_base}{ext}")
        if path:
            return path
    return None


class ScoringService:
    def __init__(
        self,
        scoring_repo: ScoringRepo,
        session_repo: SessionRepo,
        vision_client: VisionClient,
        storage_client: StorageClient,
        criteria: list,
    ):
        self.scoring_repo = scoring_repo
        self.session_repo = session_repo
        self.vision_client = vision_client
        self.storage_client = storage_client
        self.criteria = criteria

    async def start_scoring(self, session_id: str, product_id: Optional[str] = None) -> Optional[dict]:
        session = self.session_repo.get(session_id)
        if not session:
            return None
        self.scoring_repo.create(session_id)
        # Fire and forget — runs in background while client polls /scoring_status/
        asyncio.create_task(self._run_scoring(session_id, product_id))
        return {"session_id": session_id, "status": "pending"}

    def get_status(self, session_id: str) -> Optional[dict]:
        return self.scoring_repo.get(session_id)

    async def _run_scoring(self, session_id: str, product_id: Optional[str] = None):
        self.scoring_repo.update(session_id, status="processing")
        try:
            active = _active_criteria(self.criteria, product_id)
            # Ollama processes requests sequentially — run criteria one by one
            # Gemini supports parallel requests — use asyncio.gather
            if getattr(self.vision_client, "concurrent", True):
                tasks = [self._score_criterion(session_id, c) for c in active]
                criteria_results = await asyncio.gather(*tasks)
            else:
                criteria_results = []
                for c in active:
                    criteria_results.append(await self._score_criterion(session_id, c))

            found = [r for r in criteria_results if r["image_found"]]
            total_weight = sum(r["weight"] for r in found)
            final_score = (
                int(sum(r["score"] * r["weight"] for r in found) / total_weight)
                if total_weight > 0
                else 0
            )

            self.scoring_repo.update(
                session_id,
                status="completed",
                final_score=final_score,
                criteria=[dict(r) for r in criteria_results],
            )
        except Exception as e:
            self.scoring_repo.update(session_id, status="failed", error=str(e))

    async def _score_criterion(self, session_id: str, criterion: dict) -> dict:
        image_path = _find_image(self.storage_client, session_id, criterion["filename"])

        if not image_path:
            return {
                "key": criterion["key"],
                "label": criterion["label"],
                "weight": criterion["weight"],
                "score": 0,
                "observaciones": "Imagen no encontrada",
                "image_found": False,
            }

        # asyncio.to_thread runs the blocking HTTP call in a thread pool
        result = await asyncio.to_thread(
            self.vision_client.analyze, image_path, criterion["prompt"]
        )

        return {
            "key": criterion["key"],
            "label": criterion["label"],
            "weight": criterion["weight"],
            "score": max(0, min(100, int(result.get("score", 0)))),
            "observaciones": result.get("observaciones", "Sin observaciones"),
            "image_found": True,
        }
