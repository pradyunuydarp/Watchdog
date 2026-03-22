"""Text model implementations for the Watchdog NLP service."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import math
import random
from typing import Protocol

from app.ml.features import generate_ngrams, tokenize

PAD_TOKEN = "<pad>"
UNKNOWN_TOKEN = "<unk>"
MODEL_FAMILY_NAIVE_BAYES = "naive_bayes"
MODEL_FAMILY_GRU = "gru"
MODEL_FAMILY_LSTM = "lstm"
MODEL_FAMILY_ATTENTION = "attention"
MODEL_FAMILY_TRANSFORMER = "transformer"
SEQUENCE_MODEL_FAMILIES = {MODEL_FAMILY_GRU, MODEL_FAMILY_LSTM}
PLANNED_MODEL_FAMILIES = {MODEL_FAMILY_ATTENTION, MODEL_FAMILY_TRANSFORMER}
SUPPORTED_MODEL_FAMILIES = {MODEL_FAMILY_NAIVE_BAYES, *SEQUENCE_MODEL_FAMILIES, *PLANNED_MODEL_FAMILIES}

try:
    import torch
    from torch import Tensor, nn
    from torch.nn.utils.rnn import pack_padded_sequence

    TORCH_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when torch is missing.
    torch = None
    Tensor = object
    class _Module:
        pass

    class _NNNamespace:
        Module = _Module

    nn = _NNNamespace()
    pack_padded_sequence = None
    TORCH_AVAILABLE = False


class TextClassifier(Protocol):
    """Common prediction surface shared by all model implementations."""

    def predict(self, text: str) -> str:
        """Return the predicted label."""

    def predict_with_confidence(self, text: str) -> "Prediction":
        """Return the predicted label with confidence."""

    def evaluate(self, texts: list[str], labels: list[str]) -> "EvaluationMetrics":
        """Evaluate the classifier against labeled examples."""


@dataclass(frozen=True, slots=True)
class TrainingConfig:
    """Hyperparameters for the Naive Bayes text model."""

    alpha: float
    min_token_frequency: int
    ngram_range: tuple[int, int]


@dataclass(frozen=True, slots=True)
class SequenceTrainingConfig:
    """Hyperparameters for recurrent sequence classifiers."""

    architecture: str
    embedding_dim: int
    hidden_dim: int
    num_layers: int
    dropout: float
    learning_rate: float
    epochs: int
    batch_size: int
    max_vocab_size: int
    max_sequence_length: int
    random_seed: int = 42


@dataclass(frozen=True, slots=True)
class PlannedModelConfig:
    """Configuration scaffold for future attention and transformer backends."""

    architecture: str
    encoder_name: str
    tokenizer_name: str
    max_sequence_length: int
    random_seed: int = 42


@dataclass(frozen=True, slots=True)
class Prediction:
    """Model prediction with a calibrated-ish confidence estimate."""

    label: str
    confidence: float


@dataclass(frozen=True, slots=True)
class EvaluationMetrics:
    """Basic evaluation metrics for a supervised classifier."""

    accuracy: float
    macro_f1: float


@dataclass(frozen=True, slots=True)
class SequenceVocabulary:
    """Vocabulary used by the sequence models."""

    token_to_index: dict[str, int]
    pad_token: str = PAD_TOKEN
    unknown_token: str = UNKNOWN_TOKEN

    @classmethod
    def build(cls, texts: list[str], max_vocab_size: int) -> "SequenceVocabulary":
        """Build a capped token vocabulary from training texts."""

        token_counts: Counter[str] = Counter()
        for text in texts:
            token_counts.update(tokenize(text))

        token_to_index = {PAD_TOKEN: 0, UNKNOWN_TOKEN: 1}
        for token, _ in token_counts.most_common(max(max_vocab_size - len(token_to_index), 0)):
            if token not in token_to_index:
                token_to_index[token] = len(token_to_index)
        return cls(token_to_index=token_to_index)

    @property
    def index_to_token(self) -> list[str]:
        """Return the inverse vocabulary mapping as a dense list."""

        items = sorted(self.token_to_index.items(), key=lambda item: item[1])
        return [token for token, _ in items]

    @property
    def padding_index(self) -> int:
        """Return the embedding padding index."""

        return self.token_to_index[self.pad_token]

    @property
    def unknown_index(self) -> int:
        """Return the unknown token index."""

        return self.token_to_index[self.unknown_token]

    def encode(self, text: str, max_sequence_length: int) -> tuple[list[int], int]:
        """Encode a text string into a fixed-length list of token ids."""

        tokens = tokenize(text)[:max_sequence_length]
        if not tokens:
            tokens = [self.unknown_token]

        token_ids = [self.token_to_index.get(token, self.unknown_index) for token in tokens]
        length = len(token_ids)
        if length < max_sequence_length:
            token_ids.extend([self.padding_index] * (max_sequence_length - length))
        return token_ids, length


class NaiveBayesTextClassifier:
    """Minimal multinomial Naive Bayes classifier for text labels."""

    def __init__(self, config: TrainingConfig) -> None:
        self.config = config
        self._vocabulary: set[str] = set()
        self._class_document_counts: Counter[str] = Counter()
        self._class_token_counts: dict[str, Counter[str]] = defaultdict(Counter)
        self._class_total_tokens: Counter[str] = Counter()
        self._labels: set[str] = set()

    def fit(self, texts: list[str], labels: list[str]) -> None:
        """Fit the classifier on labeled text examples."""

        if len(texts) != len(labels):
            raise ValueError("Texts and labels must have equal length.")
        if not texts:
            raise ValueError("Training data must not be empty.")

        document_frequency: Counter[str] = Counter()
        tokenized_documents: list[list[str]] = []
        for text in texts:
            tokens = generate_ngrams(tokenize(text), self.config.ngram_range)
            tokenized_documents.append(tokens)
            document_frequency.update(set(tokens))

        self._vocabulary = {
            token
            for token, frequency in document_frequency.items()
            if frequency >= self.config.min_token_frequency
        }

        if not self._vocabulary:
            self._vocabulary = set(document_frequency.keys())

        for tokens, label in zip(tokenized_documents, labels, strict=True):
            self._labels.add(label)
            self._class_document_counts[label] += 1
            filtered_tokens = [token for token in tokens if token in self._vocabulary]
            self._class_token_counts[label].update(filtered_tokens)
            self._class_total_tokens[label] += len(filtered_tokens)

    def predict(self, text: str) -> str:
        """Return only the predicted label."""

        return self.predict_with_confidence(text).label

    def predict_with_confidence(self, text: str) -> Prediction:
        """Return a predicted label and normalized confidence score."""

        if not self._labels:
            raise ValueError("Model must be trained before prediction.")

        features = [token for token in generate_ngrams(tokenize(text), self.config.ngram_range) if token in self._vocabulary]
        class_scores: dict[str, float] = {}
        total_documents = sum(self._class_document_counts.values())
        vocabulary_size = max(len(self._vocabulary), 1)

        for label in self._labels:
            prior = math.log(self._class_document_counts[label] / total_documents)
            likelihood = 0.0
            for feature in features:
                token_count = self._class_token_counts[label][feature]
                smoothed_probability = (token_count + self.config.alpha) / (
                    self._class_total_tokens[label] + self.config.alpha * vocabulary_size
                )
                likelihood += math.log(smoothed_probability)
            class_scores[label] = prior + likelihood

        best_label = max(class_scores, key=class_scores.get)
        normalized_confidence = _softmax_confidence(class_scores, best_label)
        return Prediction(label=best_label, confidence=round(normalized_confidence, 2))

    def evaluate(self, texts: list[str], labels: list[str]) -> EvaluationMetrics:
        """Evaluate the classifier using accuracy and macro-F1."""

        predictions = [self.predict(text) for text in texts]
        accuracy = sum(1 for predicted, actual in zip(predictions, labels, strict=True) if predicted == actual) / len(labels)
        macro_f1 = _macro_f1(predictions, labels)
        return EvaluationMetrics(accuracy=round(accuracy, 4), macro_f1=round(macro_f1, 4))


class SequenceTextClassifier:
    """PyTorch-backed sequence classifier using either a GRU or LSTM encoder."""

    def __init__(
        self,
        config: SequenceTrainingConfig,
        vocabulary: SequenceVocabulary | None = None,
        labels: list[str] | None = None,
        state_dict: dict[str, object] | None = None,
        device: str = "cpu",
    ) -> None:
        _require_torch()
        if config.architecture not in SEQUENCE_MODEL_FAMILIES:
            raise ValueError(f"Unsupported sequence architecture: {config.architecture}")

        self.config = config
        self._device = _resolve_device(device)
        self._vocabulary = vocabulary
        self._labels = labels or []
        self._state_dict = state_dict
        self._model = None

    @property
    def architecture(self) -> str:
        """Return the configured recurrent architecture."""

        return self.config.architecture

    @property
    def vocabulary(self) -> SequenceVocabulary:
        """Return the fitted vocabulary."""

        if self._vocabulary is None:
            raise ValueError("Vocabulary is not initialized.")
        return self._vocabulary

    @property
    def labels(self) -> list[str]:
        """Return the sorted label list."""

        if not self._labels:
            raise ValueError("Labels are not initialized.")
        return self._labels

    def fit(self, texts: list[str], labels: list[str]) -> None:
        """Train the sequence classifier on labeled text examples."""

        if len(texts) != len(labels):
            raise ValueError("Texts and labels must have equal length.")
        if not texts:
            raise ValueError("Training data must not be empty.")

        self._vocabulary = SequenceVocabulary.build(texts, self.config.max_vocab_size)
        self._labels = sorted(set(labels))
        label_to_index = {label: index for index, label in enumerate(self._labels)}

        model = _SequenceClassifierModule(
            architecture=self.config.architecture,
            vocab_size=len(self.vocabulary.token_to_index),
            embedding_dim=self.config.embedding_dim,
            hidden_dim=self.config.hidden_dim,
            num_layers=self.config.num_layers,
            dropout=self.config.dropout,
            num_classes=len(self._labels),
            padding_index=self.vocabulary.padding_index,
        ).to(self._device)

        optimizer = torch.optim.Adam(model.parameters(), lr=self.config.learning_rate)
        loss_fn = nn.CrossEntropyLoss()

        encoded_texts = [self.vocabulary.encode(text, self.config.max_sequence_length) for text in texts]
        indexed_labels = [label_to_index[label] for label in labels]

        random_generator = random.Random(self.config.random_seed)
        torch.manual_seed(self.config.random_seed)

        model.train()
        for _ in range(self.config.epochs):
            batch_indices = list(range(len(encoded_texts)))
            random_generator.shuffle(batch_indices)
            for start in range(0, len(batch_indices), self.config.batch_size):
                current_indices = batch_indices[start : start + self.config.batch_size]
                batch_tokens = [encoded_texts[index][0] for index in current_indices]
                batch_lengths = [encoded_texts[index][1] for index in current_indices]
                batch_labels = [indexed_labels[index] for index in current_indices]

                token_tensor = torch.tensor(batch_tokens, dtype=torch.long, device=self._device)
                length_tensor = torch.tensor(batch_lengths, dtype=torch.long, device=self._device)
                label_tensor = torch.tensor(batch_labels, dtype=torch.long, device=self._device)

                optimizer.zero_grad()
                logits = model(token_tensor, length_tensor)
                loss = loss_fn(logits, label_tensor)
                loss.backward()
                optimizer.step()

        self._model = model.eval()
        self._state_dict = self._model.state_dict()

    def predict(self, text: str) -> str:
        """Return only the predicted label."""

        return self.predict_with_confidence(text).label

    def predict_with_confidence(self, text: str) -> Prediction:
        """Return the predicted label and softmax confidence."""

        model = self._ensure_runtime_model()
        token_ids, length = self.vocabulary.encode(text, self.config.max_sequence_length)
        with torch.no_grad():
            logits = model(
                torch.tensor([token_ids], dtype=torch.long, device=self._device),
                torch.tensor([length], dtype=torch.long, device=self._device),
            )
            probabilities = torch.softmax(logits, dim=1).squeeze(0).cpu().tolist()

        best_index = max(range(len(probabilities)), key=probabilities.__getitem__)
        return Prediction(label=self.labels[best_index], confidence=round(float(probabilities[best_index]), 2))

    def evaluate(self, texts: list[str], labels: list[str]) -> EvaluationMetrics:
        """Evaluate the classifier using accuracy and macro-F1."""

        predictions = [self.predict(text) for text in texts]
        accuracy = sum(1 for predicted, actual in zip(predictions, labels, strict=True) if predicted == actual) / len(labels)
        macro_f1 = _macro_f1(predictions, labels)
        return EvaluationMetrics(accuracy=round(accuracy, 4), macro_f1=round(macro_f1, 4))

    def export_state(self) -> dict[str, object]:
        """Return a serializable state payload for artifact storage."""

        if self._state_dict is None:
            raise ValueError("Model must be trained or restored before export.")
        return {
            "config": {
                "architecture": self.config.architecture,
                "embedding_dim": self.config.embedding_dim,
                "hidden_dim": self.config.hidden_dim,
                "num_layers": self.config.num_layers,
                "dropout": self.config.dropout,
                "learning_rate": self.config.learning_rate,
                "epochs": self.config.epochs,
                "batch_size": self.config.batch_size,
                "max_vocab_size": self.config.max_vocab_size,
                "max_sequence_length": self.config.max_sequence_length,
                "random_seed": self.config.random_seed,
            },
            "vocabulary": self.vocabulary.index_to_token,
            "labels": self.labels,
            "state_dict": self._state_dict,
        }

    @classmethod
    def from_state(cls, payload: dict[str, object], device: str = "cpu") -> "SequenceTextClassifier":
        """Restore a trained classifier from persisted state."""

        index_to_token = list(payload["vocabulary"])
        vocabulary = SequenceVocabulary(token_to_index={token: index for index, token in enumerate(index_to_token)})
        return cls(
            config=SequenceTrainingConfig(**payload["config"]),
            vocabulary=vocabulary,
            labels=list(payload["labels"]),
            state_dict=payload["state_dict"],
            device=device,
        )

    def _ensure_runtime_model(self) -> "_SequenceClassifierModule":
        """Load the torch module lazily for inference."""

        if self._model is None:
            if self._state_dict is None:
                raise ValueError("Model has not been trained or restored.")
            self._model = _SequenceClassifierModule(
                architecture=self.config.architecture,
                vocab_size=len(self.vocabulary.token_to_index),
                embedding_dim=self.config.embedding_dim,
                hidden_dim=self.config.hidden_dim,
                num_layers=self.config.num_layers,
                dropout=self.config.dropout,
                num_classes=len(self.labels),
                padding_index=self.vocabulary.padding_index,
            ).to(self._device)
            self._model.load_state_dict(self._state_dict)
            self._model.eval()
        return self._model


class _SequenceClassifierModule(nn.Module):
    """Shared GRU/LSTM encoder architecture."""

    def __init__(
        self,
        architecture: str,
        vocab_size: int,
        embedding_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
        num_classes: int,
        padding_index: int,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=padding_index)
        recurrent_dropout = dropout if num_layers > 1 else 0.0
        if architecture == MODEL_FAMILY_GRU:
            self.encoder = nn.GRU(
                input_size=embedding_dim,
                hidden_size=hidden_dim,
                num_layers=num_layers,
                dropout=recurrent_dropout,
                batch_first=True,
            )
        else:
            self.encoder = nn.LSTM(
                input_size=embedding_dim,
                hidden_size=hidden_dim,
                num_layers=num_layers,
                dropout=recurrent_dropout,
                batch_first=True,
            )
        self.classifier = nn.Linear(hidden_dim, num_classes)

    def forward(self, token_ids: Tensor, lengths: Tensor) -> Tensor:
        """Encode padded tokens and produce logits."""

        embedded = self.embedding(token_ids)
        packed = pack_padded_sequence(embedded, lengths.cpu(), batch_first=True, enforce_sorted=False)
        _, hidden = self.encoder(packed)
        if isinstance(hidden, tuple):
            hidden = hidden[0]
        return self.classifier(hidden[-1])


class PlannedTextClassifier:
    """Placeholder classifier for future attention-based and transformer models."""

    def __init__(self, config: PlannedModelConfig, readiness_message: str | None = None) -> None:
        if config.architecture not in PLANNED_MODEL_FAMILIES:
            raise ValueError(f"Unsupported planned model architecture: {config.architecture}")
        self.config = config
        self._readiness_message = readiness_message or (
            f"{config.architecture} models are scaffolded but not implemented yet."
        )

    @property
    def architecture(self) -> str:
        """Return the configured planned architecture."""

        return self.config.architecture

    def predict(self, text: str) -> str:
        """Raise until the backend is implemented."""

        raise NotImplementedError(self._readiness_message)

    def predict_with_confidence(self, text: str) -> Prediction:
        """Raise until the backend is implemented."""

        raise NotImplementedError(self._readiness_message)

    def evaluate(self, texts: list[str], labels: list[str]) -> EvaluationMetrics:
        """Raise until the backend is implemented."""

        raise NotImplementedError(self._readiness_message)

    def export_state(self) -> dict[str, object]:
        """Return a serializable placeholder payload."""

        return {
            "config": {
                "architecture": self.config.architecture,
                "encoder_name": self.config.encoder_name,
                "tokenizer_name": self.config.tokenizer_name,
                "max_sequence_length": self.config.max_sequence_length,
                "random_seed": self.config.random_seed,
            },
            "status": "planned",
            "readiness_message": self._readiness_message,
        }

    @classmethod
    def from_state(cls, payload: dict[str, object]) -> "PlannedTextClassifier":
        """Restore a placeholder classifier from persisted state."""

        return cls(
            config=PlannedModelConfig(**payload["config"]),
            readiness_message=str(payload.get("readiness_message", "")) or None,
        )


def _require_torch() -> None:
    """Raise a clear error when torch-backed features are requested without torch."""

    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is required for sequence-based analyzers and training.")


def _resolve_device(device: str) -> str:
    """Resolve runtime device selection safely."""

    if device == "auto":
        if TORCH_AVAILABLE and torch.cuda.is_available():
            return "cuda"
        return "cpu"
    return device


def _softmax_confidence(class_scores: dict[str, float], best_label: str) -> float:
    """Convert log scores into a bounded confidence estimate."""

    max_score = max(class_scores.values())
    normalized_values = {label: math.exp(score - max_score) for label, score in class_scores.items()}
    denominator = sum(normalized_values.values())
    return normalized_values[best_label] / denominator if denominator else 0.0


def _macro_f1(predictions: list[str], labels: list[str]) -> float:
    """Compute macro-averaged F1 across all observed classes."""

    observed_labels = sorted(set(predictions) | set(labels))
    if not observed_labels:
        return 0.0

    f1_scores: list[float] = []
    for current_label in observed_labels:
        true_positive = sum(
            1
            for predicted, actual in zip(predictions, labels, strict=True)
            if predicted == current_label and actual == current_label
        )
        false_positive = sum(
            1
            for predicted, actual in zip(predictions, labels, strict=True)
            if predicted == current_label and actual != current_label
        )
        false_negative = sum(
            1
            for predicted, actual in zip(predictions, labels, strict=True)
            if predicted != current_label and actual == current_label
        )

        precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) else 0.0
        recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) else 0.0

        if precision + recall == 0:
            f1_scores.append(0.0)
        else:
            f1_scores.append((2 * precision * recall) / (precision + recall))

    return sum(f1_scores) / len(f1_scores)
