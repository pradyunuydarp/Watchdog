import re
from dataclasses import dataclass

from app.models import AnalysisCategory, AnalysisResponse, AnalysisSeverity


_CATEGORY_KEYWORDS: dict[AnalysisCategory, tuple[str, ...]] = {
    AnalysisCategory.database: ("database", "sql", "postgres", "mysql", "query"),
    AnalysisCategory.network: ("network", "dns", "latency", "packet", "socket", "connection"),
    AnalysisCategory.authentication: ("auth", "login", "token", "jwt", "permission", "forbidden"),
    AnalysisCategory.performance: ("slow", "latency", "throughput", "cpu", "memory", "timeout"),
    AnalysisCategory.infrastructure: ("deploy", "pod", "container", "kubernetes", "node", "disk"),
}

_SEVERITY_KEYWORDS: dict[AnalysisSeverity, tuple[str, ...]] = {
    AnalysisSeverity.critical: ("critical", "outage", "down", "severe", "panic", "breach"),
    AnalysisSeverity.high: ("high", "failed", "error", "timeout", "unavailable", "reject"),
    AnalysisSeverity.medium: ("warn", "warning", "degraded", "retry", "slow"),
}

_ENTITY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b[A-Z]{2,}[A-Z0-9_-]*\b"),
    re.compile(r"\b(?:db|api|auth|cache|queue|service|payment|gateway)\b", re.IGNORECASE),
    re.compile(r"\b(?:timeout|latency|failure|error|outage)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class AnalyzerResult:
    category: AnalysisCategory
    severity: AnalysisSeverity
    confidence: float
    entities: list[str]

    def to_response(self) -> AnalysisResponse:
        return AnalysisResponse(
            category=self.category,
            severity=self.severity,
            confidence=self.confidence,
            entities=self.entities,
        )


class HeuristicAnalyzer:
    def analyze(self, text: str) -> AnalyzerResult:
        normalized = text.lower()
        category = self._pick_category(normalized)
        severity = self._pick_severity(normalized)
        entities = self._extract_entities(text)
        confidence = self._score_confidence(normalized, category, severity, entities)

        return AnalyzerResult(
            category=category,
            severity=severity,
            confidence=confidence,
            entities=entities,
        )

    def _pick_category(self, text: str) -> AnalysisCategory:
        best_category = AnalysisCategory.unknown
        best_score = 0

        for category, keywords in _CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_category = category
                best_score = score

        return best_category

    def _pick_severity(self, text: str) -> AnalysisSeverity:
        for severity, keywords in _SEVERITY_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return severity
        return AnalysisSeverity.low

    def _extract_entities(self, text: str) -> list[str]:
        entities: list[str] = []
        for pattern in _ENTITY_PATTERNS:
            for match in pattern.findall(text):
                if match not in entities:
                    entities.append(match.lower())
        return entities

    def _score_confidence(
        self,
        text: str,
        category: AnalysisCategory,
        severity: AnalysisSeverity,
        entities: list[str],
    ) -> float:
        confidence = 0.35
        if category is not AnalysisCategory.unknown:
            confidence += 0.25
        if severity is not AnalysisSeverity.low:
            confidence += 0.2
        confidence += min(len(entities) * 0.05, 0.15)
        if any(term in text for term in ("urgent", "immediate", "critical", "outage")):
            confidence += 0.05
        return round(min(confidence, 0.99), 2)


analyzer = HeuristicAnalyzer()
