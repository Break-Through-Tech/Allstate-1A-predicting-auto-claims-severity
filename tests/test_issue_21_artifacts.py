import csv
import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATE2 = ROOT / "notebooks/final-deliverables/September/Gate 2"
EVIDENCE_DIR = (
    ROOT
    / "notebooks/final-deliverables/September/Gate 3"
    / "findings-and-limitations"
)
NOTEBOOK_PATH = ROOT / "notebooks/ragib-nehal/ragib_nehal_task_13.ipynb"
REGISTER_PATH = GATE2 / "findings_register.csv"
REVIEW_REGISTER_PATH = GATE2 / "independent_review_register.csv"
REPORT_PATH = ROOT / "docs/team/september/Gate 3/findings_and_limitations_report.md"
SOURCE_PATH = ROOT / "data/allstate_claims_data.csv"

# checks sha256 of a file in chunks to avoid loading the entire file into memory
def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

# computes the sha256 of the executable code cells in a notebook, ignoring outputs and metadata
def executable_notebook_sha256(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    code_sources = [
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    ]
    payload = json.dumps(code_sources, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

# runs tests for issue #21 artifacts, including notebook, evidence bundle, and register
class Issue21ArtifactTests(unittest.TestCase):
    def test_notebook_and_evidence_bundle_exist(self):
        expected = {
            "finding_evidence_checks.csv",
            "independent_recalculation_results.csv",
            "run_manifest.json",
        }
        self.assertTrue(NOTEBOOK_PATH.is_file())
        self.assertTrue(EVIDENCE_DIR.is_dir())
        self.assertEqual(
            {path.name for path in EVIDENCE_DIR.iterdir() if path.is_file()},
            expected,
        )

        notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        saved_outputs = json.dumps(
            [cell.get("outputs", []) for cell in notebook["cells"]]
        )
        self.assertNotIn(str(ROOT), saved_outputs)

    # checks that the canonical register contains exactly seven supported findings with expected properties
    def test_canonical_register_contains_seven_supported_findings(self):
        with REGISTER_PATH.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual([row["finding_id"] for row in rows], [
            "F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007"
        ])
        self.assertEqual({row["register_version"] for row in rows}, {"2.0.0"})
        self.assertEqual(len({row["finding_id"] for row in rows}), 7)
        self.assertTrue(all(row["review_decision"] == "approved" for row in rows))
        self.assertTrue(all(row["reviewer"] == "Liam Stapley" for row in rows))
        self.assertTrue(all(row["evidence_status"] in {
            "directly observed", "consistent with a pattern", "hypothesis", "inconclusive"
        } for row in rows))

        for row in rows:
            evidence = ROOT / row["evidence_path"]
            self.assertTrue(evidence.is_file(), row["finding_id"])
            self.assertEqual(row["evidence_sha256"], sha256(evidence))

    # check if recalculated results match the required benchmarks within specified tolerances
    def test_recalculation_results_match_required_benchmarks(self):
        results = pd.read_csv(
            EVIDENCE_DIR / "independent_recalculation_results.csv",
            dtype={"metric": str},
        ).set_index("metric")

        expected = {
            "source_rows": 188318,
            "source_columns": 132,
            "missing_cells": 0,
            "duplicate_rows": 0,
            "unique_ids": 188318,
            "mean_loss": 3037.34,
            "median_loss": 2115.57,
            "p95_loss": 8508.54,
            "max_loss": 121012.25,
            "raw_skewness": 3.795,
            "categorical_fields": 116,
            "two_level_fields": 72,
            "four_or_fewer_level_fields": 88,
            "cat1_levels": 2,
            "cat109_levels": 84,
            "cat110_levels": 131,
            "cat116_levels": 326,
            "continuous_target_rows": 14,
            "continuous_pair_rows": 91,
        }
        tolerances = {
            "mean_loss": 0.005,
            "median_loss": 0.005,
            "p95_loss": 0.005,
            "max_loss": 0.005,
            "raw_skewness": 0.0005,
        }

        for metric, value in expected.items():
            self.assertIn(metric, results.index)
            self.assertLessEqual(
                abs(float(results.loc[metric, "recalculated_value"]) - value),
                tolerances.get(metric, 0),
            )
            self.assertEqual(results.loc[metric, "comparison_status"], "PASS")
            self.assertEqual(results.loc[metric, "reviewer"], "Liam Stapley")
            self.assertEqual(results.loc[metric, "review_date"], "2026-10-04")
            self.assertEqual(results.loc[metric, "review_decision"], "approved")

    def test_headline_rankings_are_recalculated_from_source(self):
        data = pd.read_csv(SOURCE_PATH)
        continuous = [f"cont{i}" for i in range(1, 15)]
        target_rank = (
            data[continuous]
            .corrwith(data["loss"])
            .abs()
            .sort_values(ascending=False)
            .head(3)
            .index.tolist()
        )
        self.assertEqual(target_rank, ["cont2", "cont7", "cont3"])

        matrix = data[continuous].corr()
        pairs = []
        for left_index, left in enumerate(continuous):
            for right in continuous[left_index + 1:]:
                pairs.append((abs(matrix.loc[left, right]), left, right))
        strongest = [(left, right) for _, left, right in sorted(pairs, reverse=True)[:3]]
        self.assertEqual(strongest, [
            ("cont11", "cont12"),
            ("cont1", "cont9"),
            ("cont6", "cont10"),
        ])

    # test that the manifest file and review register are up-to-date with the current state of the source and notebook
    def test_manifest_hashes_and_review_register_are_current(self):
        manifest = json.loads((EVIDENCE_DIR / "run_manifest.json").read_text())
        self.assertEqual(manifest["issue"], "#21")
        self.assertEqual(manifest["status"], "approved")
        self.assertEqual(manifest["review"], {
            "reviewer": "Liam Stapley",
            "review_date": "2026-10-04",
            "review_decision": "approved",
        })
        self.assertEqual(manifest["source"]["sha256"], sha256(SOURCE_PATH))
        self.assertEqual(
            manifest["notebook"]["executable_source_sha256"],
            executable_notebook_sha256(NOTEBOOK_PATH),
        )
        self.assertIn("base_git_revision", manifest)
        self.assertIn("working_tree_dirty", manifest)

        for artifact in manifest["artifacts"]:
            path = ROOT / artifact["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(artifact["sha256"], sha256(path))

        reviews = pd.read_csv(REVIEW_REGISTER_PATH, keep_default_na=False)
        issue21 = reviews.loc[reviews["issue"] == "#21"]
        self.assertEqual(len(issue21), 1)
        row = issue21.iloc[0]
        self.assertEqual(row["author"], "Ragib Nehal")
        self.assertEqual(row["independent_reviewer"], "Liam Stapley")
        self.assertEqual(row["review_decision"], "approved")
        self.assertEqual(row["fresh_run_verified"], "reviewed")

    # checks that the finding checks are derived from evidence comparisons and have expected properties 
    def test_finding_checks_are_derived_from_evidence_comparisons(self):
        checks = pd.read_csv(EVIDENCE_DIR / "finding_evidence_checks.csv")
        self.assertEqual(set(checks["finding_id"]), {
            "F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007"
        })
        self.assertTrue(checks["status"].eq("PASS").all())
        self.assertTrue((checks["comparison_count"] > 0).all())

        counts = checks.set_index("finding_id")["comparison_count"]
        self.assertGreaterEqual(counts["F-001"], 5)
        self.assertGreaterEqual(counts["F-003"], 6)
        self.assertGreaterEqual(counts["F-004"], 28)
        self.assertGreaterEqual(counts["F-005"], 137 * 3)
        self.assertGreaterEqual(counts["F-006"], 91 * 2)

    def test_report_exists(self):
        self.assertTrue(REPORT_PATH.is_file())


if __name__ == "__main__":
    unittest.main()
