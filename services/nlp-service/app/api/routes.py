"""HTTP routes for the NLP service."""

from fastapi import APIRouter, Depends

from app.core.config import Settings, settings
from app.models import AnalysisRequest, AnalysisResponse, HealthResponse
from app.services.analyzer import NlpAnalyzerService, analyzer_service

internal_router = APIRouter(prefix="/api/internal/nlp", tags=["nlp"])
v1_router = APIRouter(prefix="/api/v1", tags=["health"])


def get_settings() -> Settings:
    """Return the singleton settings object for FastAPI dependency injection."""

    return settings


def get_analyzer_service() -> NlpAnalyzerService:
    """Return the analyzer service singleton for request handlers."""

    return analyzer_service


@v1_router.get("/health", response_model=HealthResponse)
def health(runtime_settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Report service health in a transport-neutral shape."""

    return HealthResponse(**runtime_settings.as_health_payload())


@internal_router.post("/analyze", response_model=AnalysisResponse)
def analyze(
    payload: AnalysisRequest,
    service: NlpAnalyzerService = Depends(get_analyzer_service),
) -> AnalysisResponse:
    """Analyze text from the HTTP API and return a structured result."""

    return service.analyze_http(payload)
