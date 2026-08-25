"""
test_confidence_audit.py

Basic unit + integration tests for the Trust Audit prototype.
Run with:  python -m unittest discover -s tests -v
(No pytest dependency required -- uses the standard library only.)
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.confidence_audit import audit_record, audit_records, summarize
from backend import data_loader


class TestAuditRecordUnit(unittest.TestCase):
    """Unit tests using synthetic records -- checks the logic in isolation."""

    def test_high_score_with_hedging_is_flagged_overstated(self):
        record = {
            "relevance_score": 100,
            "reasoning": "The snippet appears to be a research abstract, likely from a university site.",
        }
        result = audit_record(record)
        self.assertEqual(result.verdict, "Overstated Confidence")
        self.assertLess(result.adjusted_score, result.original_score)
        self.assertIn("appears to be", result.hedge_phrases_found)

    def test_high_score_with_no_hedging_is_consistent(self):
        record = {
            "relevance_score": 95,
            "reasoning": "This is the author's official university faculty profile page.",
        }
        result = audit_record(record)
        self.assertEqual(result.verdict, "Consistent")
        self.assertEqual(result.adjusted_score, 95)

    def test_low_score_with_hedging_is_consistent_not_flagged(self):
        # Hedged language paired with an already-low score is *honest*, not a bug.
        record = {
            "relevance_score": 40,
            "reasoning": "This possibly relates to the author but could not be confirmed.",
        }
        result = audit_record(record)
        self.assertEqual(result.verdict, "Consistent")

    def test_low_score_with_definitive_language_is_understated(self):
        record = {
            "relevance_score": 30,
            "reasoning": "This is confirmed and verified as the author's official ORCID record.",
        }
        result = audit_record(record)
        self.assertEqual(result.verdict, "Understated Confidence")
        self.assertGreater(result.adjusted_score, result.original_score)

    def test_missing_reasoning_does_not_crash(self):
        record = {"relevance_score": 80, "reasoning": None}
        result = audit_record(record)
        self.assertEqual(result.verdict, "Consistent")

    def test_missing_score_defaults_to_zero(self):
        record = {"reasoning": "appears to be something"}
        result = audit_record(record)
        self.assertEqual(result.original_score, 0)

    def test_adjusted_score_never_negative_or_over_100(self):
        record = {
            "relevance_score": 100,
            "reasoning": (
                "appears to be likely possibly could be might be presumably "
                "seems to seemingly suggests potentially unclear"
            ),
        }
        result = audit_record(record)
        self.assertGreaterEqual(result.adjusted_score, 0)
        self.assertLessEqual(result.adjusted_score, 100)

    def test_summarize_totals_match_record_count(self):
        records = [
            {"relevance_score": 100, "reasoning": "appears to be a match"},
            {"relevance_score": 90, "reasoning": "this is the official confirmed record"},
            {"relevance_score": 95, "reasoning": "clearly the author's own site"},
        ]
        results = audit_records(records)
        stats = summarize(results)
        self.assertEqual(stats["total_records"], 3)
        self.assertEqual(
            stats["consistent"] + stats["overstated"] + stats["understated"],
            3,
        )


class TestRealDataIntegration(unittest.TestCase):
    """Integration tests against the actual provided dataset (data/authors/)."""

    @classmethod
    def setUpClass(cls):
        data_loader.reload_data()
        cls.authors = data_loader.list_authors()

    def test_data_directory_loaded(self):
        self.assertEqual(len(self.authors), 50, "Expected all 50 provided author folders to load.")

    def test_every_author_has_required_files(self):
        for author in self.authors:
            self.assertIn("profile", author)
            self.assertIn("publications", author)
            self.assertIn("broad_impact", author)

    def test_audit_runs_without_error_on_full_dataset(self):
        total = 0
        for author in self.authors:
            results = audit_records(author["broad_impact"])
            total += len(results)
            for r in results:
                self.assertIn(r.verdict, ("Consistent", "Overstated Confidence", "Understated Confidence"))
                self.assertGreaterEqual(r.adjusted_score, 0)
                self.assertLessEqual(r.adjusted_score, 100)
        self.assertGreater(total, 0)

    def test_known_example_andrew_gewirth_is_flagged(self):
        # Regression test for the exact example used in the product pitch:
        # Gewirth's chemistry.illinois.edu record is scored 100 but hedges
        # with "appears to be" / "likely" -- it must be flagged.
        author = data_loader.get_author("Andrew_A._Gewirth")
        self.assertIsNotNone(author, "Expected Andrew_A._Gewirth in the dataset.")
        results = audit_records(author["broad_impact"])
        matches = [r for r in results if r.url and "chemistry.illinois.edu" in r.url]
        self.assertTrue(matches, "Expected to find the chemistry.illinois.edu record.")
        self.assertEqual(matches[0].verdict, "Overstated Confidence")


if __name__ == "__main__":
    unittest.main()
