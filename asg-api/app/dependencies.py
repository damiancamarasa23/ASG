"""
Dependency injection — wires together clients, repos, and services.
FastAPI resolves these via Depends() in the route handlers.
"""

from functools import lru_cache

from app.clients.storage_client import LocalStorageClient, StorageClient
from app.clients.vision_client import GeminiClient, OllamaClient, VisionClient
from app.config import settings
from app.repositories.scoring_repo import ScoringRepo
from app.repositories.session_repo import SessionRepo
from app.services.scoring_service import ScoringService
from app.services.session_service import SessionService


@lru_cache
def get_vision_client() -> VisionClient:
    if settings.backend == "ollama":
        return OllamaClient(settings.ollama_url, settings.ollama_model)
    return GeminiClient(settings.gemini_api_key)


@lru_cache
def get_storage_client() -> StorageClient:
    if settings.storage_type == "local":
        return LocalStorageClient(settings.local_storage_path, settings.api_base_url)
    raise NotImplementedError("S3 storage not implemented yet — set STORAGE_TYPE=local")


def get_session_service() -> SessionService:
    return SessionService(SessionRepo(), get_storage_client())


def get_scoring_service() -> ScoringService:
    from gucci.criteria import GUCCI_CRITERIA
    return ScoringService(
        ScoringRepo(),
        SessionRepo(),
        get_vision_client(),
        get_storage_client(),
        GUCCI_CRITERIA,
    )
