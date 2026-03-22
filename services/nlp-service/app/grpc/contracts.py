"""Proto-shaped contract objects used before generated gRPC bindings exist.

These dataclasses mirror the future protobuf messages closely enough for the
service layer to stay stable while the actual gRPC code generation is added in a
later iteration.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GrpcAnalyzeRequest:
    """Proto-shaped request for the Analyzer service."""

    text: str
    source: str | None = None
    correlation_id: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GrpcEnrichment:
    """Proto-shaped enrichment payload returned by the Analyzer service."""

    category: str
    severity: str
    confidence: float
    entities: list[str] = field(default_factory=list)
    model_version: str = "heuristic-v1"


@dataclass(frozen=True, slots=True)
class GrpcAnalyzeResponse:
    """Proto-shaped response for the Analyzer service."""

    enrichment: GrpcEnrichment
    attributes: dict[str, str] = field(default_factory=dict)

