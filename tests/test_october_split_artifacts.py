import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATE1 = ROOT / "notebooks/final-deliverables/October/Gate 1"
SOURCE_PATH = ROOT / "data/allstate_claims_data.csv"
MANIFEST_PATH = GATE1 / "partition_manifest.csv"
RUN_MANIFEST_PATH = GATE1 / "modeling_run_manifest.json"
CHECKS_PATH = GATE1 / "split_checks.csv"
TARGET_SUMMARY_PATH = GATE1 / "partition_target_summary.csv"
HIGH_LOSS_PATH = GATE1 / "high_loss_support.csv"
CATEGORICAL_COVERAGE_PATH = GATE1 / "categorical_level_coverage.csv"

EXPECTED_COUNTS = {"train": 131822, "validation": 28248, "test": 28248}


# checks sha256 of a file in chunks to avoid loading the entire file into memory
def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class PartitionManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = pd.read_csv(MANIFEST_PATH, dtype={"cv_fold": "Int64"})
        cls.source_ids = pd.read_csv(SOURCE_PATH, usecols=["id"])["id"]
        cls.split = json.loads(RUN_MANIFEST_PATH.read_text(encoding="utf-8"))["split"]

    def test_columns(self):
        self.assertEqual(list(self.manifest.columns), ["id", "partition", "cv_fold"])

    def test_every_source_claim_appears_exactly_once(self):
        self.assertTrue(self.manifest["id"].is_unique)
        self.assertEqual(set(self.manifest["id"]), set(self.source_ids))
        self.assertEqual(len(self.manifest), len(self.source_ids))

    def test_partition_counts(self):
        counts = self.manifest["partition"].value_counts().to_dict()
        self.assertEqual(counts, EXPECTED_COUNTS)

    def test_cv_folds_only_on_train_rows(self):
        train = self.manifest[self.manifest["partition"] == "train"]
        held_out = self.manifest[self.manifest["partition"] != "train"]
        self.assertFalse(train["cv_fold"].isna().any())
        self.assertEqual(set(train["cv_fold"]), {0, 1, 2, 3, 4})
        self.assertTrue(held_out["cv_fold"].isna().all())

    # pandas writes an integer column with blanks as floats ("3.0") unless kept nullable
    def test_cv_fold_written_as_integers(self):
        raw = pd.read_csv(MANIFEST_PATH, dtype=str)["cv_fold"].dropna()
        self.assertTrue(raw.str.fullmatch(r"[0-4]").all())

    def test_manifest_hash_and_split_are_registered(self):
        self.assertEqual(self.split["status"], "frozen")
        self.assertEqual(self.split["version"], "OCT-SPLIT-001")
        self.assertEqual(self.split["random_seed"], 42)
        self.assertEqual(self.split["manifest_sha256"], sha256(MANIFEST_PATH))
        self.assertEqual(self.split["train_claims"], EXPECTED_COUNTS["train"])
        self.assertEqual(self.split["validation_claims"], EXPECTED_COUNTS["validation"])
        self.assertEqual(self.split["test_claims"], EXPECTED_COUNTS["test"])

    def test_library_versions_are_recorded(self):
        for library in ["scikit-learn", "pandas", "numpy"]:
            self.assertIn(library, self.split["library_versions"])


class SplitChecksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checks = pd.read_csv(CHECKS_PATH)

    def test_all_integrity_checks_pass(self):
        integrity = self.checks[self.checks["kind"] == "integrity"]
        self.assertEqual(
            sorted(integrity["check_id"]), ["I1", "I2", "I3", "I4", "I5", "I6"]
        )
        self.assertTrue((integrity["status"] == "pass").all(), integrity.to_string())

    def test_distribution_checks_are_recorded(self):
        distribution = self.checks[self.checks["kind"] == "distribution"]
        self.assertEqual(sorted(distribution["check_id"]), ["D1", "D2", "D3"])
        self.assertTrue(distribution["status"].isin(["pass", "flag"]).all())


# test-partition targets stay unexamined in October, so no table may report them
class PreComparisonTests(unittest.TestCase):
    def test_target_summary_excludes_test(self):
        summary = pd.read_csv(TARGET_SUMMARY_PATH)
        self.assertEqual(list(summary["partition"]), ["train", "validation"])

    def test_high_loss_support_excludes_test(self):
        support = pd.read_csv(HIGH_LOSS_PATH)
        self.assertEqual(set(support["partition"]), {"train", "validation"})
        self.assertEqual(set(support["threshold"]), {"train_p90", "train_p99"})

    def test_categorical_coverage_has_every_cat_field(self):
        coverage = pd.read_csv(CATEGORICAL_COVERAGE_PATH)
        self.assertEqual(
            sorted(coverage["field"]), sorted(f"cat{i}" for i in range(1, 117))
        )


if __name__ == "__main__":
    unittest.main()
