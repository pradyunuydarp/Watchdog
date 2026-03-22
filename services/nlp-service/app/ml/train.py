"""Command-line entry point for training the lightweight NLP models."""

from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.ml.pipeline import TrainingPipeline


def main() -> None:
    """Train models from the configured dataset path and persist the artifact."""

    pipeline = TrainingPipeline(random_seed=settings.training_random_seed)
    bundle = pipeline.train_from_jsonl(
        dataset_path=Path(settings.training_data_path),
        output_path=Path(settings.model_artifact_path),
    )
    print(
        "trained",
        bundle.bundle_metadata.model_version,
        f"category_test_accuracy={bundle.bundle_metadata.category_test_accuracy}",
        f"severity_test_accuracy={bundle.bundle_metadata.severity_test_accuracy}",
    )


if __name__ == "__main__":
    main()
