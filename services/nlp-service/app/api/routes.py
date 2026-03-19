from fastapi import APIRouter

from app.models import AnalysisRequest, AnalysisResponse
from app.services.analyzer import analyzer

internal_router = APIRouter(prefix="/api/internal/nlp", tags=["nlp"])
v1_router = APIRouter(prefix="/api/v1", tags=["health"])


@v1_router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "watchdog-nlp-service"}


@internal_router.post("/analyze", response_model=AnalysisResponse)
def analyze(payload: AnalysisRequest) -> AnalysisResponse:
    return analyzer.analyze(payload.text).to_response()
