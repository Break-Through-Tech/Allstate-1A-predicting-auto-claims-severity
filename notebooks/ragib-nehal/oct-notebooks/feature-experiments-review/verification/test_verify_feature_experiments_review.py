"""Mutation tests for the issue #46 standalone verifier."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


BUNDLE = Path(__file__).resolve().parents[1]
VERIFIER_PATH = Path(__file__).resolve().parent / "verify_feature_experiments_review.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("issue46_verifier", VERIFIER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class VerifierMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load_verifier()
        cls.source, cls.manifest, cls.train = cls.verifier.check_frozen_inputs()
        cls.predictions = pd.read_csv(cls.verifier.PREDICTIONS)
        cls.comparison = pd.read_csv(cls.verifier.COMPARISON).set_index("run_id")

    def test_rejects_validation_losses_reassigned_to_different_claim_ids(self):
        corrupted = self.predictions.copy()
        corrupted["id"] = corrupted["id"].shift(-1, fill_value=corrupted["id"].iloc[0])

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "validation_predictions.csv"
            corrupted.to_csv(path, index=False)
            with patch.object(self.verifier, "PREDICTIONS", path):
                with self.assertRaisesRegex(self.verifier.VerificationError, "loss.*claim ID"):
                    self.verifier.check_predictions_and_metrics(self.manifest)

    def test_rejects_corrupted_segment_and_largest_error_values(self):
        diagnostics = pd.read_csv(self.verifier.DIAGNOSTICS)
        diagnostics.loc[
            (diagnostics["model"] == "e02_full")
            & (diagnostics["segment"] == "loss >= train p99"),
            "mae",
        ] = 0.0
        diagnostics.loc[
            (diagnostics["model"] == "o1_reduced")
            & (diagnostics["segment"] == "loss >= train p99"),
            "support_claims",
        ] = 0
        diagnostics["mean_signed_error"] = 0.0
        largest = pd.read_csv(self.verifier.LARGEST)
        largest[["prediction", "signed_error", "abs_error"]] = 0.0

        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            diagnostics_path = directory / "error_diagnostics.csv"
            largest_path = directory / "largest_errors.csv"
            diagnostics.to_csv(diagnostics_path, index=False)
            largest.to_csv(largest_path, index=False)
            with (
                patch.object(self.verifier, "DIAGNOSTICS", diagnostics_path),
                patch.object(self.verifier, "LARGEST", largest_path),
            ):
                with self.assertRaises(self.verifier.VerificationError):
                    self.verifier.check_diagnostics(self.predictions, self.comparison)

    def test_executed_notebook_does_not_commit_absolute_workspace_path(self):
        notebook = json.loads(self.verifier.NOTEBOOK.read_text(encoding="utf-8"))
        serialized_outputs = json.dumps(
            [output for cell in notebook["cells"] for output in cell.get("outputs", [])]
        )
        self.assertNotIn(str(self.verifier.ROOT), serialized_outputs)

    def test_completed_work_uses_an_implementation_record_not_an_active_plan(self):
        self.assertFalse((BUNDLE / "issue_46_implementation_plan.md").exists())
        self.assertTrue((BUNDLE / "records" / "issue_46_implementation_record.md").is_file())

    def test_issue_report_lives_only_in_docs_and_remains_manifested(self):
        issue_report = (
            self.verifier.ROOT
            / "docs/team/october/Gate 3/feature_experiments_report.md"
        )
        self.assertEqual(
            getattr(self.verifier, "ISSUE_REPORT", None),
            issue_report,
        )
        self.assertTrue(issue_report.is_file())
        self.assertIn(issue_report, self.verifier.artifact_files())
        self.assertFalse((BUNDLE / "feature_experiments_report.md").exists())
        self.assertFalse((BUNDLE / "model_review.md").exists())

    def test_markdown_files_have_no_trailing_whitespace(self):
        offenders = []
        for path in BUNDLE.rglob("*.md"):
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.endswith((" ", "\t")):
                    offenders.append(f"{path.name}:{line_number}")
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
