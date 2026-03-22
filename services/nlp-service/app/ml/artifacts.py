"""Model artifact persistence helpers for trained classifiers."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.ml.model import (
    MODEL_FAMILY_GRU,
    MODEL_FAMILY_LSTM,
    NaiveBayesTextClassifier,
    PlannedTextClassifier,
    SequenceTextClassifier,
    TrainingConfig,
    _require_torch,
    torch,
)


@dataclass(frozen=True, slots=True)
class BundleMetadata:
    """Metadata stored alongside trained model artifacts."""

    model_version: str
    model_family: str
    category_validation_accuracy: float
    category_test_accuracy: float
    severity_validation_accuracy: float
    severity_test_accuracy: float


@dataclass(frozen=True, slots=True)
class PersistedClassifier:
    """Serializable form of a trained text classifier."""

    family: str
    payload: dict[str, Any]

    @classmethod
    def from_trained_model(
        cls,
        model: NaiveBayesTextClassifier | SequenceTextClassifier | PlannedTextClassifier,
    ) -> "PersistedClassifier":
        """Create a persisted view from an in-memory trained classifier."""

        if isinstance(model, NaiveBayesTextClassifier):
            return cls(
                family="naive_bayes",
                payload={
                    "config": {
                        "alpha": model.config.alpha,
                        "min_token_frequency": model.config.min_token_frequency,
                        "ngram_range": list(model.config.ngram_range),
                    },
                    "vocabulary": sorted(model._vocabulary),
                    "class_document_counts": dict(model._class_document_counts),
                    "class_token_counts": {label: dict(counter) for label, counter in model._class_token_counts.items()},
                    "class_total_tokens": dict(model._class_total_tokens),
                },
            )

        if isinstance(model, SequenceTextClassifier):
            return cls(family=model.architecture, payload=model.export_state())

        if isinstance(model, PlannedTextClassifier):
            return cls(family=model.architecture, payload=model.export_state())

        raise TypeError(f"Unsupported classifier type: {type(model)!r}")

    def to_runtime_model(
        self,
        device: str = "cpu",
    ) -> NaiveBayesTextClassifier | SequenceTextClassifier | PlannedTextClassifier:
        """Rebuild a runtime classifier from persisted state."""

        if self.family == "naive_bayes":
            config_payload = dict(self.payload["config"])
            config_payload["ngram_range"] = tuple(config_payload["ngram_range"])
            model = NaiveBayesTextClassifier(TrainingConfig(**config_payload))
            model._vocabulary = set(self.payload["vocabulary"])
            model._class_document_counts = Counter(self.payload["class_document_counts"])
            model._class_token_counts = {
                label: Counter(tokens) for label, tokens in self.payload["class_token_counts"].items()
            }
            model._class_total_tokens = Counter(self.payload["class_total_tokens"])
            model._labels = set(self.payload["class_document_counts"].keys())
            return model

        if self.family in {MODEL_FAMILY_GRU, MODEL_FAMILY_LSTM}:
            return SequenceTextClassifier.from_state(self.payload, device=device)
        if self.family in {"attention", "transformer"}:
            return PlannedTextClassifier.from_state(self.payload)

        raise ValueError(f"Unsupported persisted classifier family: {self.family}")

    def predict_with_confidence(self, text: str, device: str = "cpu"):
        """Run inference by reconstructing the runtime model lazily."""

        return self.to_runtime_model(device=device).predict_with_confidence(text)


class ModelBundleStore:
    """Persist and restore trained model bundles."""

    FORMAT_VERSION = 2

    @staticmethod
    def save(path: Path, bundle) -> None:
        """Write the trained bundle to disk."""

        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format_version": ModelBundleStore.FORMAT_VERSION,
            "bundle_metadata": {
                "model_version": bundle.bundle_metadata.model_version,
                "model_family": bundle.bundle_metadata.model_family,
                "category_validation_accuracy": bundle.bundle_metadata.category_validation_accuracy,
                "category_test_accuracy": bundle.bundle_metadata.category_test_accuracy,
                "severity_validation_accuracy": bundle.bundle_metadata.severity_validation_accuracy,
                "severity_test_accuracy": bundle.bundle_metadata.severity_test_accuracy,
            },
            "category_model": {
                "family": bundle.category_model.family,
                "payload": bundle.category_model.payload,
            },
            "severity_model": {
                "family": bundle.severity_model.family,
                "payload": bundle.severity_model.payload,
            },
        }

        if bundle.bundle_metadata.model_family in {MODEL_FAMILY_GRU, MODEL_FAMILY_LSTM}:
            _require_torch()
            torch.save(payload, path)
            return

        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    @staticmethod
    def load(path: Path):
        """Load a trained bundle from disk."""

        from app.ml.pipeline import TrainedModelBundle

        payload = ModelBundleStore._read_payload(path)
        if payload.get("format_version") == ModelBundleStore.FORMAT_VERSION:
            return TrainedModelBundle(
                category_model=PersistedClassifier(**payload["category_model"]),
                severity_model=PersistedClassifier(**payload["severity_model"]),
                bundle_metadata=BundleMetadata(**payload["bundle_metadata"]),
            )

        return _load_legacy_json_bundle(path)

    @staticmethod
    def _read_payload(path: Path) -> dict[str, Any]:
        """Read a persisted payload, supporting both torch and JSON artifacts."""

        if torch is not None:
            try:
                return torch.load(path, map_location="cpu", weights_only=False)
            except Exception:
                pass
        return json.loads(path.read_text(encoding="utf-8"))


def _load_legacy_json_bundle(path: Path):
    """Load the original JSON-only Naive Bayes artifact format."""

    from app.ml.pipeline import TrainedModelBundle

    payload = json.loads(path.read_text(encoding="utf-8"))
    return TrainedModelBundle(
        category_model=_legacy_persisted_classifier_from_dict(payload["category_model"]),
        severity_model=_legacy_persisted_classifier_from_dict(payload["severity_model"]),
        bundle_metadata=BundleMetadata(model_family="naive_bayes", **payload["bundle_metadata"]),
    )


def _legacy_persisted_classifier_from_dict(payload: dict[str, Any]) -> PersistedClassifier:
    """Rebuild a persisted classifier from the original JSON format."""

    config_payload = dict(payload["config"])
    config_payload["ngram_range"] = list(config_payload["ngram_range"])
    return PersistedClassifier(
        family="naive_bayes",
        payload={
            "config": config_payload,
            "vocabulary": payload["vocabulary"],
            "class_document_counts": payload["class_document_counts"],
            "class_token_counts": payload["class_token_counts"],
            "class_total_tokens": payload["class_total_tokens"],
        },
    )
