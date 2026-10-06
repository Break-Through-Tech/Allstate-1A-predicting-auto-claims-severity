import csv
import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE2 = ROOT / "notebooks/final-deliverables/September/Gate 2"


def read_rows(path, key):
    with path.open(newline="", encoding="utf-8") as handle:
        return {row[key]: row for row in csv.DictReader(handle)}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ReviewRegisterConsistencyTests(unittest.TestCase):
    def test_documented_method_approvals_are_recorded(self):
        rows = read_rows(GATE2 / "method_approvals.csv", "method")

        expected = {
            "Data dictionary": ("Ragib Nehal", "2026-09-24"),
            "Target views": ("Liam Stapley", "2026-10-04"),
            "Rare-level rule": ("Liam Stapley", "2026-10-04"),
            "Continuous-bin rule": ("Liam Stapley", "2026-09-23"),
            "Correlation methods": ("Liam Stapley", "2026-09-23"),
            "Findings-register format": ("Liam Stapley", "2026-10-04"),
        }

        self.assertEqual(set(rows), set(expected))
        for method, (reviewer, review_date) in expected.items():
            self.assertEqual(rows[method]["decision"], "approved")
            self.assertEqual(rows[method]["approved_by"], reviewer)
            self.assertEqual(rows[method]["decision_date"], review_date)

    def test_completed_non_author_reviews_are_recorded(self):
        rows = read_rows(GATE2 / "independent_review_register.csv", "issue")

        self.assertEqual(rows["#15"]["independent_reviewer"], "Ragib Nehal")
        self.assertEqual(rows["#15"]["review_date"], "2026-09-24")
        self.assertEqual(rows["#15"]["review_decision"], "approved")

        self.assertEqual(rows["#18"]["independent_reviewer"], "Liam Stapley")
        self.assertEqual(rows["#18"]["review_date"], "2026-09-27")
        self.assertEqual(rows["#18"]["review_decision"], "approved")

        self.assertEqual(rows["#17"]["author"], "Ragib Nehal")
        self.assertEqual(rows["#17"]["independent_reviewer"], "Liam Stapley")
        self.assertEqual(rows["#17"]["review_date"], "2026-09-23")
        self.assertEqual(rows["#17"]["review_decision"], "approved")
        self.assertEqual(rows["#17"]["fresh_run_verified"], "reviewed")

    def test_findings_review_and_evidence_links_are_current(self):
        findings = read_rows(GATE2 / "findings_register.csv", "finding_id")

        for finding in findings.values():
            self.assertEqual(finding["reviewer"], "Liam Stapley")
            self.assertEqual(finding["review_decision"], "approved")
            evidence_path = ROOT / finding["evidence_path"]
            self.assertEqual(finding["evidence_sha256"], sha256(evidence_path))


if __name__ == "__main__":
    unittest.main()
