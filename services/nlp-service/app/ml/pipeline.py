"""Training and tuning pipeline for the Watchdog NLP service."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path

from app.core.config import settings
from app.ml.artifacts import BundleMetadata, ModelBundleStore, PersistedClassifier
from app.ml.dataset import DatasetSplit, load_jsonl_dataset, split_dataset
from app.ml.model import (
    EvaluationMetrics,
    MODEL_FAMILY_ATTENTION,
    MODEL_FAMILY_TRANSFORMER,
    NaiveBayesTextClassifier,
    PlannedModelConfig,
    PlannedTextClassifier,
    SequenceTextClassifier,
    SequenceTrainingConfig,
    SUPPORTED_MODEL_FAMILIES,
    TextClassifier,
    TORCH_AVAILABLE,
    TrainingConfig,
)


@dataclass(frozen=True, slots=True)
class TuningResult:
    """Selected hyperparameters and validation metrics for a model family."""

    config: TrainingConfig | SequenceTrainingConfig | PlannedModelConfig
    validation_metrics: EvaluationMetrics


@dataclass(frozen=True, slots=True)
class TrainedModelBundle:
    """Container for the final category and severity models."""

    category_model: PersistedClassifier
    severity_model: PersistedClassifier
    bundle_metadata: BundleMetadata


class TrainingPipeline:
    """Train, validate, test, and persist two classifiers."""

    def __init__(
        self,
        random_seed: int = settings.training_random_seed,
        model_family: str = settings.model_architecture,
        device: str = settings.model_device,
    ) -> None:
        self._random_seed = random_seed
        self._model_family = model_family
        self._device = device
        if self._model_family not in SUPPORTED_MODEL_FAMILIES:
            raise ValueError(f"Unsupported training model family: {self._model_family}")

    def train_from_jsonl(self, dataset_path: Path, output_path: Path) -> TrainedModelBundle:
        """Load a JSONL dataset, train the models, and persist the artifact."""

        examples = load_jsonl_dataset(dataset_path)
        split = split_dataset(examples, random_seed=self._random_seed)
        bundle = self.train(split)
        ModelBundleStore.save(output_path, bundle)
        return bundle

    def train(self, split: DatasetSplit) -> TrainedModelBundle:
        """Train category and severity models and return the selected bundle."""

        category_model, category_result = self._fit_best_model(
            train_texts=[example.text for example in split.train],
            train_labels=[example.category.value for example in split.train],
            validate_texts=[example.text for example in split.validate],
            validate_labels=[example.category.value for example in split.validate],
        )
        severity_model, severity_result = self._fit_best_model(
            train_texts=[example.text for example in split.train],
            train_labels=[example.severity.value for example in split.train],
            validate_texts=[example.text for example in split.validate],
            validate_labels=[example.severity.value for example in split.validate],
        )

        category_final_model = self._fit_final_model(
            config=category_result.config,
            texts=[example.text for example in split.train + split.validate],
            labels=[example.category.value for example in split.train + split.validate],
        )
        severity_final_model = self._fit_final_model(
            config=severity_result.config,
            texts=[example.text for example in split.train + split.validate],
            labels=[example.severity.value for example in split.train + split.validate],
        )

        category_test_metrics = category_final_model.evaluate(
            [example.text for example in split.test],
            [example.category.value for example in split.test],
        )
        severity_test_metrics = severity_final_model.evaluate(
            [example.text for example in split.test],
            [example.severity.value for example in split.test],
        )

        metadata = BundleMetadata(
            model_version=f"{self._model_family.replace('_', '-')}-v1",
            model_family=self._model_family,
            category_validation_accuracy=category_result.validation_metrics.accuracy,
            category_test_accuracy=category_test_metrics.accuracy,
            severity_validation_accuracy=severity_result.validation_metrics.accuracy,
            severity_test_accuracy=severity_test_metrics.accuracy,
        )
        return TrainedModelBundle(
            category_model=PersistedClassifier.from_trained_model(category_final_model),
            severity_model=PersistedClassifier.from_trained_model(severity_final_model),
            bundle_metadata=metadata,
        )

    def _fit_best_model(
        self,
        train_texts: list[str],
        train_labels: list[str],
        validate_texts: list[str],
        validate_labels: list[str],
    ) -> tuple[TextClassifier, TuningResult]:
        """Search a compact hyperparameter grid and keep the best model."""

        if self._model_family == "naive_bayes":
            return self._fit_best_naive_bayes_model(train_texts, train_labels, validate_texts, validate_labels)
        if self._model_family in {"gru", "lstm"}:
            return self._fit_best_sequence_model(train_texts, train_labels, validate_texts, validate_labels)
        if self._model_family in {MODEL_FAMILY_ATTENTION, MODEL_FAMILY_TRANSFORMER}:
            return self._planned_model_not_ready()
        raise ValueError(f"Unsupported training model family: {self._model_family}")

    def _fit_best_naive_bayes_model(
        self,
        train_texts: list[str],
        train_labels: list[str],
        validate_texts: list[str],
        validate_labels: list[str],
    ) -> tuple[NaiveBayesTextClassifier, TuningResult]:
        """Search a compact hyperparameter grid and keep the best Naive Bayes model."""

        search_space = [
            TrainingConfig(alpha=alpha, min_token_frequency=min_token_frequency, ngram_range=ngram_range)
            for alpha, min_token_frequency, ngram_range in product(
                (0.3, 0.7, 1.0),
                (1, 2),
                ((1, 1), (1, 2)),
            )
        ]

        best_model: NaiveBayesTextClassifier | None = None
        best_result: TuningResult | None = None

        for candidate_config in search_space:
            candidate_model = NaiveBayesTextClassifier(candidate_config)
            candidate_model.fit(train_texts, train_labels)
            validation_metrics = candidate_model.evaluate(validate_texts, validate_labels)
            candidate_result = TuningResult(config=candidate_config, validation_metrics=validation_metrics)
            if best_result is None or validation_metrics.macro_f1 > best_result.validation_metrics.macro_f1:
                best_model = candidate_model
                best_result = candidate_result

        if best_model is None or best_result is None:
            raise RuntimeError("Hyperparameter search failed to select a model.")

        return best_model, best_result

    def _fit_best_sequence_model(
        self,
        train_texts: list[str],
        train_labels: list[str],
        validate_texts: list[str],
        validate_labels: list[str],
    ) -> tuple[SequenceTextClassifier, TuningResult]:
        """Search a compact hyperparameter grid and keep the best sequence model."""

        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for GRU/LSTM model training.")

        search_space = [
            SequenceTrainingConfig(
                architecture=self._model_family,
                embedding_dim=embedding_dim,
                hidden_dim=hidden_dim,
                num_layers=1,
                dropout=0.0,
                learning_rate=learning_rate,
                epochs=settings.sequence_epochs,
                batch_size=settings.sequence_batch_size,
                max_vocab_size=settings.sequence_max_vocab_size,
                max_sequence_length=settings.sequence_max_sequence_length,
                random_seed=self._random_seed,
            )
            for embedding_dim, hidden_dim, learning_rate in product((32, 48), (32, 64), (0.01, 0.005))
        ]

        best_model: SequenceTextClassifier | None = None
        best_result: TuningResult | None = None

        for candidate_config in search_space:
            candidate_model = SequenceTextClassifier(candidate_config, device=self._device)
            candidate_model.fit(train_texts, train_labels)
            validation_metrics = candidate_model.evaluate(validate_texts, validate_labels)
            candidate_result = TuningResult(config=candidate_config, validation_metrics=validation_metrics)
            if best_result is None or validation_metrics.macro_f1 > best_result.validation_metrics.macro_f1:
                best_model = candidate_model
                best_result = candidate_result

        if best_model is None or best_result is None:
            raise RuntimeError("Sequence model search failed to select a model.")

        return best_model, best_result

    def _planned_model_not_ready(self) -> tuple[TextClassifier, TuningResult]:
        """Raise an explicit error for future backends that are scaffolded only."""

        config = PlannedModelConfig(
            architecture=self._model_family,
            encoder_name=settings.transformer_model_name,
            tokenizer_name=settings.planned_model_tokenizer_name,
            max_sequence_length=settings.sequence_max_sequence_length,
            random_seed=self._random_seed,
        )
        raise NotImplementedError(
            f"{config.architecture} training is scaffolded in Watchdog but not implemented yet. "
            "Install the intended model stack, add tokenizer/encoder wiring, and then connect fine-tuning."
        )

    def _fit_final_model(
        self,
        config: TrainingConfig | SequenceTrainingConfig | PlannedModelConfig,
        texts: list[str],
        labels: list[str],
    ) -> TextClassifier:
        """Retrain the chosen hyperparameters on the combined train+validate set."""

        if isinstance(config, TrainingConfig):
            final_model = NaiveBayesTextClassifier(config)
            final_model.fit(texts, labels)
            return final_model

        if isinstance(config, PlannedModelConfig):
            return PlannedTextClassifier(config)

        final_model = SequenceTextClassifier(config, device=self._device)
        final_model.fit(texts, labels)
        return final_model
