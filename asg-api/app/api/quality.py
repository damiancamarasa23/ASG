from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.services.image_quality_service import validate

router = APIRouter(tags=["quality"])


class QualityResponse(BaseModel):
    ok: bool
    issues: list[str]


@router.post("/validate_image_quality/", response_model=QualityResponse)
async def validate_image_quality(request: Request):
    image_bytes = await request.body()
    result = validate(image_bytes)
    return QualityResponse(ok=result.ok, issues=result.issues)
