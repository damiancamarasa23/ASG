"""
Internal endpoints — not part of the public B2B API.

/internal/upload/{session_id}/{filename}
    Simulates S3 presigned URL behavior in local development.
    Client PUTs raw image bytes directly to this endpoint,
    exactly as it would to a presigned S3 URL in production.
"""

from fastapi import APIRouter, Depends, Request

from app.clients.storage_client import StorageClient
from app.dependencies import get_storage_client

router = APIRouter(prefix="/internal", tags=["internal"])


@router.put("/upload/{session_id}/{filename}")
async def upload_image(
    session_id: str,
    filename: str,
    request: Request,
    storage: StorageClient = Depends(get_storage_client),
):
    data = await request.body()
    storage.save_image(session_id, filename, data)
    return {"session_id": session_id, "filename": filename, "bytes": len(data)}
