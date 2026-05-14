from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_session_service
from app.models.session import (
    ConfirmUploadRequest,
    ConfirmUploadResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    GetUploadUrlRequest,
    GetUploadUrlResponse,
)
from app.services.session_service import SessionService

router = APIRouter(tags=["sessions"])


@router.post("/create_session/", response_model=CreateSessionResponse)
def create_session(
    req: CreateSessionRequest,
    service: SessionService = Depends(get_session_service),
):
    return service.create_session(req.consumer_platform_id, req.user_id, req.brand)


@router.post("/get_upload_url/", response_model=GetUploadUrlResponse)
def get_upload_url(
    req: GetUploadUrlRequest,
    service: SessionService = Depends(get_session_service),
):
    result = service.get_upload_url(req.session_id, req.filename)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.post("/confirm_upload/", response_model=ConfirmUploadResponse)
def confirm_upload(
    req: ConfirmUploadRequest,
    service: SessionService = Depends(get_session_service),
):
    result = service.confirm_upload(req.session_id, req.filename)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result
