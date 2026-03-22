"""Keyword and pattern lexicon used by the heuristic analyzer.

Keeping the rule data in a dedicated module makes the analyzer logic easier to
read and easier to replace later with a model-backed or embeddings-backed
implementation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import AnalysisCategory, AnalysisSeverity


@dataclass(frozen=True, slots=True)
class KeywordLexicon:
    """Immutable grouping of category and severity keywords."""

    category_keywords: dict[AnalysisCategory, tuple[str, ...]]
    severity_keywords: dict[AnalysisSeverity, tuple[str, ...]]
    entity_patterns: tuple[re.Pattern[str], ...]

    @classmethod
    def default(cls) -> "KeywordLexicon":
        """Create the default keyword lexicon used by the service."""

        return cls(
            category_keywords={
                AnalysisCategory.database: ("database", "sql", "postgres", "mysql", "query"),
                AnalysisCategory.network: ("network", "dns", "latency", "packet", "socket", "connection"),
                AnalysisCategory.authentication: ("auth", "login", "token", "jwt", "permission", "forbidden"),
                AnalysisCategory.performance: ("slow", "latency", "throughput", "cpu", "memory", "timeout"),
                AnalysisCategory.infrastructure: ("deploy", "pod", "container", "kubernetes", "node", "disk"),
            },
            severity_keywords={
                AnalysisSeverity.critical: ("critical", "outage", "down", "severe", "panic", "breach"),
                AnalysisSeverity.high: ("high", "failed", "error", "timeout", "unavailable", "reject"),
                AnalysisSeverity.medium: ("warn", "warning", "degraded", "retry", "slow"),
            },
            entity_patterns=(
                re.compile(r"\b[A-Z]{2,}[A-Z0-9_-]*\b"),
                re.compile(r"\b(?:database|sql|postgres|mysql|query)\b", re.IGNORECASE),
                re.compile(r"\b(?:db|api|auth|cache|queue|service|payment|gateway)\b", re.IGNORECASE),
                re.compile(r"\b(?:timeout|latency|failure|error|outage)\b", re.IGNORECASE),
            ),
        )
