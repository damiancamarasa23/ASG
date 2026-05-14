"""
Scoring service — orchestrates parallel image analysis and score aggregation.

Each criterion is scored concurrently via asyncio.gather + asyncio.to_thread
(since the vision clients use blocking HTTP calls).
"""

import asyncio
import io
import json
import math
import pathlib
from pathlib import Path
from typing import Optional

from PIL import Image

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


COHERENCE_PROMPT = (
    "Se te muestra un collage con todas las fotos enviadas para autenticar un producto de lujo. "
    "Tu tarea es determinar si todas las fotos pertenecen al mismo objeto físico.\n\n"
    "Analizá:\n"
    "1. ¿El color y material del producto es consistente entre las fotos?\n"
    "2. ¿El nivel de desgaste y envejecimiento es coherente en todas?\n"
    "3. ¿El modelo y las proporciones corresponden al mismo producto?\n"
    "4. ¿Hay alguna foto que claramente no pertenece al mismo objeto?\n\n"
    "Respondé SOLAMENTE con este JSON exacto:\n"
    '{\"score\": <0-100>, \"observaciones\": \"<texto breve>\"}\n'
    "score=100 significa que todas las fotos son claramente del mismo producto. "
    "score=0 significa que hay fotos de productos diferentes."
)


def _build_collage(image_paths: list[Path], cell_size: int = 400) -> Path:
    """Arrange images in a grid and save as a temp file."""
    n = len(image_paths)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    collage = Image.new("RGB", (cols * cell_size, rows * cell_size), (240, 240, 240))

    for idx, path in enumerate(image_paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((cell_size, cell_size), Image.LANCZOS)
        # Center in cell
        x = (idx % cols) * cell_size + (cell_size - img.width) // 2
        y = (idx // cols) * cell_size + (cell_size - img.height) // 2
        collage.paste(img, (x, y))

    tmp = pathlib.Path("/tmp") / f"collage_{id(image_paths)}.jpg"
    collage.save(tmp, format="JPEG", quality=85)
    return tmp


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
            raw_score = (
                int(sum(r["score"] * r["weight"] for r in found) / total_weight)
                if total_weight > 0
                else 0
            )

            # Coherence check — send collage of all found images
            image_paths = [
                _find_image(self.storage_client, session_id, c["filename"])
                for c in active
            ]
            image_paths = [p for p in image_paths if p is not None]

            coherence = {"score": 100, "observaciones": "Solo se encontró una imagen, no se puede verificar coherencia."}
            if len(image_paths) >= 2:
                collage_path = _build_collage(image_paths)
                coherence = await asyncio.to_thread(
                    self.vision_client.analyze, collage_path, COHERENCE_PROMPT
                )
                coherence["score"] = max(0, min(100, int(coherence.get("score", 100))))
                collage_path.unlink(missing_ok=True)

            # Apply coherence penalty
            coherence_score = coherence["score"]
            if coherence_score < 50:
                final_score = min(raw_score, 50)
                coherence_flag = "sospechoso"
            elif coherence_score < 75:
                final_score = min(raw_score, 75)
                coherence_flag = "advertencia"
            else:
                final_score = raw_score
                coherence_flag = "ok"

            self.scoring_repo.update(
                session_id,
                status="completed",
                final_score=final_score,
                criteria=[dict(r) for r in criteria_results],
                coherence={
                    "score": coherence_score,
                    "flag": coherence_flag,
                    "observaciones": coherence.get("observaciones", ""),
                },
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
