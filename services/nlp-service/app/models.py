"""Data models shared by the NLP service transports and analyzers."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AnalysisCategory(str, Enum):
    database = "database"
    network = "network"
    authentication = "authentication"
    performance = "performance"
    infrastructure = "infrastructure"
    unknown = "unknown"


class AnalysisSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AnalysisRequest(BaseModel):
    """Public request model for the HTTP analyze endpoint."""

    text: str = Field(min_length=1, max_length=10_000)
    source: str | None = Field(default=None, max_length=256)
    correlation_id: str | None = Field(default=None, max_length=128)
    attributes: dict[str, str] = Field(default_factory=dict)


class AnalysisResponse(BaseModel):
    """Public response model returned by the HTTP analyze endpoint."""

    category: AnalysisCategory
    severity: AnalysisSeverity
    confidence: float = Field(ge=0.0, le=1.0)
    entities: list[str] = Field(default_factory=list)
    source: str | None = None
    correlation_id: str | None = None
    attributes: dict[str, str] = Field(default_factory=dict)


class ProtoAnalyzeRequest(BaseModel):
    """Proto-shaped request model for future gRPC handlers.

    The model mirrors the fields in the future protobuf request without
    requiring generated Python code during early development.
    """

    text: str = Field(min_length=1, max_length=10_000)
    source: str | None = Field(default=None, max_length=256)
    correlation_id: str | None = Field(default=None, max_length=128)
    attributes: dict[str, str] = Field(default_factory=dict)


class ProtoAnalyzeResponse(BaseModel):
    """Proto-shaped response model for future gRPC handlers."""

    model_config = ConfigDict(protected_namespaces=())

    category: AnalysisCategory
    severity: AnalysisSeverity
    confidence: float = Field(ge=0.0, le=1.0)
    entities: list[str] = Field(default_factory=list)
    model_version: str = Field(default="heuristic-v1")
    attributes: dict[str, str] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Response model for health endpoints and readiness checks."""

    status: str = "ok"
    service: str
    environment: str
    transport: str
    details: dict[str, Any] = Field(default_factory=dict)
