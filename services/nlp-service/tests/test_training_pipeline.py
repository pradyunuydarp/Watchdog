"""Unit tests for the lightweight training pipeline and artifact handling."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.ml.artifacts import ModelBundleStore
from app.ml.dataset import load_jsonl_dataset, split_dataset
from app.ml.model import TORCH_AVAILABLE
from app.ml.pipeline import TrainingPipeline


class TrainingPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset_path = Path("data/training/incidents.jsonl")
        self.pipeline = TrainingPipeline(random_seed=7, model_family="naive_bayes")

    def test_dataset_loads_and_splits(self) -> None:
        examples = load_jsonl_dataset(self.dataset_path)
        split = split_dataset(examples, random_seed=7)
        self.assertGreaterEqual(len(split.train), 1)
        self.assertGreaterEqual(len(split.validate), 1)
        self.assertGreaterEqual(len(split.test), 1)

    def test_training_pipeline_persists_and_restores_model_bundle(self) -> None:
        with TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "bundle.json"
            bundle = self.pipeline.train_from_jsonl(self.dataset_path, artifact_path)
            reloaded_bundle = ModelBundleStore.load(artifact_path)

            self.assertEqual(bundle.bundle_metadata.model_version, "naive-bayes-v1")
            self.assertEqual(reloaded_bundle.bundle_metadata.model_version, "naive-bayes-v1")
            prediction = reloaded_bundle.category_model.predict_with_confidence(
                "Database timeout on checkout service"
            )
            self.assertEqual(prediction.label, "database")

    def test_attention_training_scaffold_raises_not_implemented(self) -> None:
        with self.assertRaises(NotImplementedError):
            TrainingPipeline(random_seed=7, model_family="attention").train_from_jsonl(
                self.dataset_path,
                Path("artifacts/attention-bundle.pt"),
            )

    def test_transformer_training_scaffold_raises_not_implemented(self) -> None:
        with self.assertRaises(NotImplementedError):
            TrainingPipeline(random_seed=7, model_family="transformer").train_from_jsonl(
                self.dataset_path,
                Path("artifacts/transformer-bundle.pt"),
            )

    @unittest.skipUnless(TORCH_AVAILABLE, "PyTorch is required for sequence-model tests.")
    def test_gru_training_pipeline_persists_and_restores_model_bundle(self) -> None:
        with TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "gru-bundle.pt"
            bundle = TrainingPipeline(random_seed=7, model_family="gru").train_from_jsonl(self.dataset_path, artifact_path)
            reloaded_bundle = ModelBundleStore.load(artifact_path)

            self.assertEqual(bundle.bundle_metadata.model_family, "gru")
            self.assertEqual(reloaded_bundle.bundle_metadata.model_family, "gru")
            prediction = reloaded_bundle.category_model.predict_with_confidence(
                "Database timeout on checkout service",
                device="cpu",
            )
            self.assertIn(prediction.label, {example.category.value for example in load_jsonl_dataset(self.dataset_path)})
            self.assertGreaterEqual(prediction.confidence, 0.0)
            self.assertLessEqual(prediction.confidence, 1.0)

    @unittest.skipUnless(TORCH_AVAILABLE, "PyTorch is required for sequence-model tests.")
    def test_lstm_training_pipeline_persists_and_restores_model_bundle(self) -> None:
        with TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "lstm-bundle.pt"
            bundle = TrainingPipeline(random_seed=7, model_family="lstm").train_from_jsonl(self.dataset_path, artifact_path)
            reloaded_bundle = ModelBundleStore.load(artifact_path)

            self.assertEqual(bundle.bundle_metadata.model_family, "lstm")
            self.assertEqual(reloaded_bundle.bundle_metadata.model_family, "lstm")
            prediction = reloaded_bundle.severity_model.predict_with_confidence(
                "Critical database outage is blocking checkout",
                device="cpu",
            )
            self.assertIn(prediction.label, {example.severity.value for example in load_jsonl_dataset(self.dataset_path)})
            self.assertGreaterEqual(prediction.confidence, 0.0)
            self.assertLessEqual(prediction.confidence, 1.0)
