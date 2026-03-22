"""Unit tests for the heuristic analyzer and transport adapters."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.grpc.adapter import ProtoAdapter
from app.grpc.contracts import GrpcAnalyzeRequest
from app.ml.model import TORCH_AVAILABLE
from app.ml.pipeline import TrainingPipeline
from app.models import AnalysisCategory, AnalysisRequest, AnalysisSeverity
from app.core.config import Settings
from app.services.analyzer import (
    AttentionAnalyzer,
    GruAnalyzer,
    HeuristicAnalyzer,
    LstmAnalyzer,
    NlpAnalyzerService,
    TransformerAnalyzer,
    build_default_analyzer,
)


class HeuristicAnalyzerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = HeuristicAnalyzer()

    def test_detects_database_incident(self) -> None:
        result = self.analyzer.analyze("Database timeout while processing payment request")
        self.assertEqual(result.category, AnalysisCategory.database)
        self.assertEqual(result.severity, AnalysisSeverity.high)
        self.assertGreater(result.confidence, 0.5)
        self.assertIn("database", result.entities)

    def test_detects_critical_outage(self) -> None:
        result = self.analyzer.analyze("Critical outage: service down and immediate action required")
        self.assertEqual(result.severity, AnalysisSeverity.critical)
        self.assertGreaterEqual(result.confidence, 0.6)


class AnalyzerServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = NlpAnalyzerService()

    def test_http_request_preserves_metadata(self) -> None:
        response = self.service.analyze_http(
            AnalysisRequest(
                text="Auth token rejected for gateway service",
                source="identity-service",
                correlation_id="trace-123",
                attributes={"region": "ap-south-1"},
            )
        )
        self.assertEqual(response.category, AnalysisCategory.authentication)
        self.assertEqual(response.correlation_id, "trace-123")
        self.assertEqual(response.source, "identity-service")
        self.assertEqual(response.attributes["region"], "ap-south-1")

    def test_proto_adapter_maps_response(self) -> None:
        adapter = ProtoAdapter(self.service)
        response = adapter.analyze(
            GrpcAnalyzeRequest(
                text="Database timeout while processing payment request",
                source="payment-service",
                correlation_id="trace-456",
                attributes={"env": "dev"},
            )
        )
        self.assertEqual(response.enrichment.category, "database")
        self.assertEqual(response.enrichment.severity, "high")
        self.assertEqual(response.enrichment.model_version, "heuristic-v1")
        self.assertEqual(response.attributes["env"], "dev")

    def test_attention_backend_without_artifact_falls_back_to_heuristic(self) -> None:
        analyzer = build_default_analyzer(
            Settings(
                analyzer_backend="attention",
                model_artifact_path="artifacts/does-not-exist.pt",
            )
        )
        self.assertIsInstance(analyzer, HeuristicAnalyzer)

    def test_transformer_placeholder_analyzer_raises_clear_error(self) -> None:
        analyzer = TransformerAnalyzer()
        with self.assertRaises(NotImplementedError):
            analyzer.analyze("future transformer request")

    def test_attention_placeholder_analyzer_raises_clear_error(self) -> None:
        analyzer = AttentionAnalyzer()
        with self.assertRaises(NotImplementedError):
            analyzer.analyze("future attention request")


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch is required for sequence-model tests.")
class SequenceAnalyzerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset_path = Path("data/training/incidents.jsonl")

    def test_gru_analyzer_uses_persisted_gru_bundle(self) -> None:
        with TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "gru-bundle.pt"
            bundle = TrainingPipeline(random_seed=11, model_family="gru").train_from_jsonl(self.dataset_path, artifact_path)
            analyzer = GruAnalyzer(bundle)

            result = analyzer.analyze("Database timeout while processing payment request")

            self.assertIn(result.category, set(AnalysisCategory))
            self.assertEqual(result.model_version, "gru-v1")
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)

    def test_lstm_analyzer_uses_persisted_lstm_bundle(self) -> None:
        with TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "lstm-bundle.pt"
            bundle = TrainingPipeline(random_seed=11, model_family="lstm").train_from_jsonl(self.dataset_path, artifact_path)
            analyzer = LstmAnalyzer(bundle)

            result = analyzer.analyze("Critical outage: service down and immediate action required")

            self.assertIn(result.severity, set(AnalysisSeverity))
            self.assertEqual(result.model_version, "lstm-v1")
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)
