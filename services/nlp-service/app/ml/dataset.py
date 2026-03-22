"""Dataset loading and splitting helpers for supervised NLP experiments.

The training pipeline expects JSONL examples containing free-form text plus the
target category and severity labels. The functions in this module keep dataset
handling deterministic and explicit so experiments can be reproduced later.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import random

from app.models import AnalysisCategory, AnalysisSeverity


@dataclass(frozen=True, slots=True)
class TrainingExample:
    """Single labeled training example used by the training pipeline."""

    text: str
    category: AnalysisCategory
    severity: AnalysisSeverity


@dataclass(frozen=True, slots=True)
class DatasetSplit:
    """Container for train/validate/test splits."""

    train: list[TrainingExample]
    validate: list[TrainingExample]
    test: list[TrainingExample]


def load_jsonl_dataset(path: Path) -> list[TrainingExample]:
    """Load a supervised dataset from JSONL.

    Each record must provide `text`, `category`, and `severity`. Extra fields
    are ignored so the dataset format can evolve without breaking the loader.
    """

    examples: list[TrainingExample] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue
        payload = json.loads(stripped_line)
        examples.append(
            TrainingExample(
                text=payload["text"],
                category=AnalysisCategory(payload["category"]),
                severity=AnalysisSeverity(payload["severity"]),
            )
        )
    return examples


def split_dataset(
    examples: list[TrainingExample],
    train_ratio: float = 0.7,
    validate_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42,
) -> DatasetSplit:
    """Create deterministic train/validate/test splits.

    The split is random but reproducible through the seed. For the current
    scaffold the split is not stratified; that can be introduced later if the
    dataset size justifies the additional complexity.
    """

    if not examples:
        raise ValueError("Dataset must contain at least one example.")
    if round(train_ratio + validate_ratio + test_ratio, 5) != 1.0:
        raise ValueError("Split ratios must sum to 1.0.")

    shuffled_examples = list(examples)
    random.Random(random_seed).shuffle(shuffled_examples)

    train_end = max(1, int(len(shuffled_examples) * train_ratio))
    validate_end = train_end + max(1, int(len(shuffled_examples) * validate_ratio))

    train_examples = shuffled_examples[:train_end]
    validate_examples = shuffled_examples[train_end:validate_end]
    test_examples = shuffled_examples[validate_end:]

    if not validate_examples:
        validate_examples = train_examples[-1:]
    if not test_examples:
        test_examples = shuffled_examples[-1:]

    return DatasetSplit(
        train=train_examples,
        validate=validate_examples,
        test=test_examples,
    )
