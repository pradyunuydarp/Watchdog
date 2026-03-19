import unittest

from app.models import AnalysisCategory, AnalysisSeverity
from app.services.analyzer import HeuristicAnalyzer


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

