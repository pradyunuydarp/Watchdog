"""Heuristic analysis engine and service façade for the NLP service.

The module is intentionally layered:

* ``HeuristicAnalyzer`` performs the deterministic signal extraction.
* ``NlpAnalyzerService`` converts the analysis result into API-facing models.
* The future gRPC server can reuse the same service façade without changing the
  analysis logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config import Settings, settings
from app.ml.artifacts import ModelBundleStore
from app.ml.model import MODEL_FAMILY_ATTENTION, MODEL_FAMILY_GRU, MODEL_FAMILY_LSTM, MODEL_FAMILY_TRANSFORMER
from app.ml.pipeline import TrainedModelBundle
from app.models import (
    AnalysisCategory,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisSeverity,
    ProtoAnalyzeRequest,
    ProtoAnalyzeResponse,
)
from app.services.lexicon import KeywordLexicon


@dataclass(frozen=True, slots=True)
class AnalyzerResult:
    """Internal analysis result used across HTTP and gRPC adapters."""

    category: AnalysisCategory
    severity: AnalysisSeverity
    confidence: float
    entities: list[str]
    model_version: str
    attributes: dict[str, str]
    source: str | None = None
    correlation_id: str | None = None

    def to_http_response(self) -> AnalysisResponse:
        """Convert the internal result into the public HTTP response model."""

        return AnalysisResponse(
            category=self.category,
            severity=self.severity,
            confidence=self.confidence,
            entities=self.entities,
            source=self.source,
            correlation_id=self.correlation_id,
            attributes=self.attributes,
        )

    def to_proto_response(self) -> ProtoAnalyzeResponse:
        """Convert the internal result into the proto-shaped response model."""

        return ProtoAnalyzeResponse(
            category=self.category,
            severity=self.severity,
            confidence=self.confidence,
            entities=self.entities,
            model_version=self.model_version,
            attributes=self.attributes,
        )


class HeuristicAnalyzer:
    """Deterministic rule-based analyzer for early-stage triage."""

    def __init__(self, lexicon: KeywordLexicon | None = None, runtime_settings: Settings | None = None) -> None:
        self._lexicon = lexicon or KeywordLexicon.default()
        self._settings = runtime_settings or settings

    def analyze(
        self,
        text: str,
        source: str | None = None,
        correlation_id: str | None = None,
        attributes: dict[str, str] | None = None,
    ) -> AnalyzerResult:
        """Analyze free-form text and return a structured triage result."""

        normalized_text = text.lower()
        category = self._pick_category(normalized_text)
        severity = self._pick_severity(normalized_text)
        entities = self._extract_entities(text)
        confidence = self._score_confidence(normalized_text, category, severity, entities)

        return AnalyzerResult(
            category=category,
            severity=severity,
            confidence=confidence,
            entities=entities,
            model_version="heuristic-v1",
            attributes=dict(attributes or {}),
            source=source,
            correlation_id=correlation_id,
        )

    def _pick_category(self, text: str) -> AnalysisCategory:
        """Choose the most likely category from the configured keyword lexicon."""

        best_category = AnalysisCategory.unknown
        best_score = 0

        for category, keywords in self._lexicon.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_category = category
                best_score = score

        return best_category

    def _pick_severity(self, text: str) -> AnalysisSeverity:
        """Choose the most likely severity from the configured keyword lexicon."""

        for severity, keywords in self._lexicon.severity_keywords.items():
            if any(keyword in text for keyword in keywords):
                return severity
        return AnalysisSeverity.low

    def _extract_entities(self, text: str) -> list[str]:
        """Extract simple entity-like tokens from the input text."""

        entities: list[str] = []
        for pattern in self._lexicon.entity_patterns:
            for match in pattern.findall(text):
                lowered_match = match.lower()
                if lowered_match not in entities:
                    entities.append(lowered_match)
        return entities

    def _score_confidence(
        self,
        text: str,
        category: AnalysisCategory,
        severity: AnalysisSeverity,
        entities: list[str],
    ) -> float:
        """Compute a bounded confidence score from the detected signals."""

        confidence = self._settings.analysis_base_confidence
        if category is not AnalysisCategory.unknown:
            confidence += self._settings.analysis_category_boost
        if severity is not AnalysisSeverity.low:
            confidence += self._settings.analysis_severity_boost
        confidence += min(len(entities) * self._settings.analysis_entity_boost, 0.15)
        if any(term in text for term in ("urgent", "immediate", "critical", "outage")):
            confidence += self._settings.analysis_urgent_boost
        return round(min(confidence, self._settings.analysis_max_confidence), 2)


class NlpAnalyzerService:
    """Application service that owns the analysis workflow.

    Keeping this wrapper separate from the heuristic engine makes it easy to
    attach alternate transports, enrich requests, or swap the analyzer
    implementation later.
    """

    def __init__(self, analyzer: HeuristicAnalyzer | None = None) -> None:
        self._analyzer = analyzer or HeuristicAnalyzer()

    def analyze_http(self, request: AnalysisRequest) -> AnalysisResponse:
        """Analyze a public HTTP request and return the API response model."""

        return self.analyze(
            text=request.text,
            source=request.source,
            correlation_id=request.correlation_id,
            attributes=request.attributes,
        ).to_http_response()

    def analyze_proto(self, request: ProtoAnalyzeRequest) -> ProtoAnalyzeResponse:
        """Analyze a proto-shaped request for future gRPC handlers."""

        return self.analyze(
            text=request.text,
            source=request.source,
            correlation_id=request.correlation_id,
            attributes=request.attributes,
        ).to_proto_response()

    def analyze(
        self,
        text: str,
        source: str | None = None,
        correlation_id: str | None = None,
        attributes: dict[str, str] | None = None,
    ) -> AnalyzerResult:
        """Execute the underlying analyzer and return the internal result."""

        return self._analyzer.analyze(
            text=text,
            source=source,
            correlation_id=correlation_id,
            attributes=attributes,
        )


analyzer_service = NlpAnalyzerService()


class ModelBackedAnalyzer:
    """Analyzer backed by a previously trained model bundle.

    The model is loaded from a local artifact generated by the training
    pipeline. If the artifact does not exist or is invalid, callers should
    continue using the heuristic analyzer.
    """

    def __init__(self, model_bundle: TrainedModelBundle) -> None:
        self._model_bundle = model_bundle

    def analyze(
        self,
        text: str,
        source: str | None = None,
        correlation_id: str | None = None,
        attributes: dict[str, str] | None = None,
    ) -> AnalyzerResult:
        """Run inference using the persisted category and severity models."""

        category_prediction = self._model_bundle.category_model.predict_with_confidence(text)
        severity_prediction = self._model_bundle.severity_model.predict_with_confidence(text)
        extracted_entities = HeuristicAnalyzer()._extract_entities(text)

        return AnalyzerResult(
            category=AnalysisCategory(category_prediction.label),
            severity=AnalysisSeverity(severity_prediction.label),
            confidence=round((category_prediction.confidence + severity_prediction.confidence) / 2, 2),
            entities=extracted_entities,
            model_version=self._model_bundle.bundle_metadata.model_version,
            attributes=dict(attributes or {}),
            source=source,
            correlation_id=correlation_id,
        )


class SequenceModelAnalyzer(ModelBackedAnalyzer):
    """Base analyzer for persisted sequence models."""

    expected_family: str | None = None

    def __init__(self, model_bundle: TrainedModelBundle, runtime_settings: Settings = settings) -> None:
        if self.expected_family and model_bundle.bundle_metadata.model_family != self.expected_family:
            raise ValueError(
                f"Loaded model family {model_bundle.bundle_metadata.model_family} does not match {self.expected_family}."
            )
        self._runtime_settings = runtime_settings
        super().__init__(model_bundle)

    def analyze(
        self,
        text: str,
        source: str | None = None,
        correlation_id: str | None = None,
        attributes: dict[str, str] | None = None,
    ) -> AnalyzerResult:
        """Run inference using the persisted sequence models."""

        category_prediction = self._model_bundle.category_model.predict_with_confidence(
            text,
            device=self._runtime_settings.model_device,
        )
        severity_prediction = self._model_bundle.severity_model.predict_with_confidence(
            text,
            device=self._runtime_settings.model_device,
        )
        extracted_entities = HeuristicAnalyzer(runtime_settings=self._runtime_settings)._extract_entities(text)

        return AnalyzerResult(
            category=AnalysisCategory(category_prediction.label),
            severity=AnalysisSeverity(severity_prediction.label),
            confidence=round((category_prediction.confidence + severity_prediction.confidence) / 2, 2),
            entities=extracted_entities,
            model_version=self._model_bundle.bundle_metadata.model_version,
            attributes=dict(attributes or {}),
            source=source,
            correlation_id=correlation_id,
        )


class GruAnalyzer(SequenceModelAnalyzer):
    """Sequence analyzer backed by a persisted GRU classifier bundle."""

    expected_family = "gru"


class LstmAnalyzer(SequenceModelAnalyzer):
    """Sequence analyzer backed by a persisted LSTM classifier bundle."""

    expected_family = "lstm"


class PlannedModelAnalyzer:
    """Placeholder analyzer for backends that are intentionally scaffold-only."""

    expected_family: str | None = None

    def __init__(self, runtime_settings: Settings = settings, model_bundle: TrainedModelBundle | None = None) -> None:
        self._runtime_settings = runtime_settings
        self._model_bundle = model_bundle

    def analyze(
        self,
        text: str,
        source: str | None = None,
        correlation_id: str | None = None,
        attributes: dict[str, str] | None = None,
    ) -> AnalyzerResult:
        """Fail explicitly until the backend is implemented."""

        raise NotImplementedError(
            f"{self.expected_family} backend is configured but not implemented yet. "
            "Keep using heuristic/GRU/LSTM until the actual model runtime is wired in."
        )


class AttentionAnalyzer(PlannedModelAnalyzer):
    """Placeholder analyzer for future attention-based backends."""

    expected_family = MODEL_FAMILY_ATTENTION


class TransformerAnalyzer(PlannedModelAnalyzer):
    """Placeholder analyzer for future transformer-based backends."""

    expected_family = MODEL_FAMILY_TRANSFORMER


def _build_model_family_analyzer(
    model_family: str,
    runtime_settings: Settings,
    model_bundle: TrainedModelBundle | None = None,
) -> ModelBackedAnalyzer | GruAnalyzer | LstmAnalyzer | AttentionAnalyzer | TransformerAnalyzer:
    """Build an analyzer instance for a known model family."""

    if model_family == MODEL_FAMILY_GRU:
        if model_bundle is None:
            raise ValueError("GRU analyzer requires a model bundle.")
        return GruAnalyzer(model_bundle, runtime_settings=runtime_settings)
    if model_family == MODEL_FAMILY_LSTM:
        if model_bundle is None:
            raise ValueError("LSTM analyzer requires a model bundle.")
        return LstmAnalyzer(model_bundle, runtime_settings=runtime_settings)
    if model_family == MODEL_FAMILY_ATTENTION:
        return AttentionAnalyzer(runtime_settings=runtime_settings, model_bundle=model_bundle)
    if model_family == MODEL_FAMILY_TRANSFORMER:
        return TransformerAnalyzer(runtime_settings=runtime_settings, model_bundle=model_bundle)
    if model_bundle is None:
        raise ValueError("Model-backed analyzer requires a model bundle.")
    return ModelBackedAnalyzer(model_bundle)


def build_default_analyzer(
    runtime_settings: Settings = settings,
) -> HeuristicAnalyzer | ModelBackedAnalyzer | GruAnalyzer | LstmAnalyzer | AttentionAnalyzer | TransformerAnalyzer:
    """Build the configured analyzer backend with heuristic fallback safety."""

    if runtime_settings.analyzer_backend != "model":
        if runtime_settings.analyzer_backend in {
            MODEL_FAMILY_GRU,
            MODEL_FAMILY_LSTM,
            MODEL_FAMILY_ATTENTION,
            MODEL_FAMILY_TRANSFORMER,
        }:
            artifact_path = Path(runtime_settings.model_artifact_path)
            if artifact_path.exists():
                return _build_model_family_analyzer(
                    runtime_settings.analyzer_backend,
                    runtime_settings,
                    ModelBundleStore.load(artifact_path),
                )
            return HeuristicAnalyzer(runtime_settings=runtime_settings)
        return HeuristicAnalyzer(runtime_settings=runtime_settings)

    artifact_path = Path(runtime_settings.model_artifact_path)
    if not artifact_path.exists():
        return HeuristicAnalyzer(runtime_settings=runtime_settings)

    model_bundle = ModelBundleStore.load(artifact_path)
    return _build_model_family_analyzer(model_bundle.bundle_metadata.model_family, runtime_settings, model_bundle)


analyzer_service = NlpAnalyzerService(build_default_analyzer())
