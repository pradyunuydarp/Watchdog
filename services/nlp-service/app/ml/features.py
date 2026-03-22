"""Feature extraction helpers for lightweight NLP models."""

from __future__ import annotations

import re


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Tokenize raw text into lowercase alphanumeric tokens."""

    return TOKEN_PATTERN.findall(text.lower())


def generate_ngrams(tokens: list[str], ngram_range: tuple[int, int]) -> list[str]:
    """Generate feature tokens for the requested n-gram range."""

    minimum_n, maximum_n = ngram_range
    ngrams: list[str] = []
    for ngram_size in range(minimum_n, maximum_n + 1):
        if len(tokens) < ngram_size:
            continue
        for start_index in range(0, len(tokens) - ngram_size + 1):
            ngrams.append(" ".join(tokens[start_index : start_index + ngram_size]))
    return ngrams
