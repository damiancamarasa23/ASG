from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_scoring_service
from app.models.scoring import (
    GenerateScoringRequest,
    GenerateScoringResponse,
    ScoringStatusResponse,
)
from app.services.scoring_service import ScoringService

router = APIRouter(tags=["scoring"])


@router.post("/generate_scoring/", response_model=GenerateScoringResponse)
async def generate_scoring(
    req: GenerateScoringRequest,
    service: ScoringService = Depends(get_scoring_service),
):
    result = await service.start_scoring(req.session_id, req.product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.get("/scoring_status/{session_id}", response_model=ScoringStatusResponse)
def get_scoring_status(
    session_id: str,
    service: ScoringService = Depends(get_scoring_service),
):
    result = service.get_status(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scoring result not found")
    return result
