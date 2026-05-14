from typing import Optional
from pydantic import BaseModel


class GenerateScoringRequest(BaseModel):
    session_id: str
    product_id: Optional[str] = None  # if None, all criteria are used


class GenerateScoringResponse(BaseModel):
    session_id: str
    status: str  # pending | processing | completed | failed


class CriterionScore(BaseModel):
    key: str
    label: str
    weight: float
    score: int
    observaciones: str
    image_found: bool


class CoherenceResult(BaseModel):
    score: int
    flag: str  # ok | advertencia | sospechoso
    observaciones: str


class ScoringStatusResponse(BaseModel):
    session_id: str
    status: str
    final_score: Optional[int] = None
    criteria: Optional[list[CriterionScore]] = None
    coherence: Optional[CoherenceResult] = None
    overall_observations: Optional[str] = None
    error: Optional[str] = None
