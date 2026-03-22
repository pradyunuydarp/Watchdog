"""Adapters between the analyzer service and proto-shaped contracts."""

from __future__ import annotations

from app.grpc.contracts import GrpcAnalyzeRequest, GrpcAnalyzeResponse, GrpcEnrichment
from app.models import ProtoAnalyzeRequest, ProtoAnalyzeResponse
from app.services.analyzer import NlpAnalyzerService


class ProtoAdapter:
    """Convert between proto-shaped transport objects and the service layer."""

    def __init__(self, service: NlpAnalyzerService | None = None) -> None:
        self._service = service or NlpAnalyzerService()

    def analyze(self, request: GrpcAnalyzeRequest) -> GrpcAnalyzeResponse:
        """Handle a gRPC-style request and return a gRPC-style response."""

        proto_request = ProtoAnalyzeRequest(
            text=request.text,
            source=request.source,
            correlation_id=request.correlation_id,
            attributes=request.attributes,
        )
        proto_response: ProtoAnalyzeResponse = self._service.analyze_proto(proto_request)
        return GrpcAnalyzeResponse(
            enrichment=GrpcEnrichment(
                category=proto_response.category.value,
                severity=proto_response.severity.value,
                confidence=proto_response.confidence,
                entities=proto_response.entities,
                model_version=proto_response.model_version,
            ),
            attributes=proto_response.attributes,
        )

