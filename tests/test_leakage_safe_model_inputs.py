from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
ISSUE_DIR = (
    REPO_ROOT
    / "notebooks"
    / "ragib-nehal"
    / "oct-notebooks"
    / "leakage-safe-model-inputs"
)
sys.path.insert(0, str(ISSUE_DIR))

import preprocessing_pipeline as pipeline  # noqa: E402


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class FrozenDataBoundaryTests(unittest.TestCase):
    def _source_frame(self) -> pd.DataFrame:
        rows = []
        for claim_id, marker in zip(range(1, 7), "ABCDEF", strict=True):
            row = {"id": claim_id}
            row.update({f"cat{i}": marker for i in range(1, 117)})
            row.update({f"cont{i}": claim_id / 10 for i in range(1, 15)})
            row["loss"] = claim_id * 100.0
            rows.append(row)
        return pd.DataFrame(rows)

    def _manifest_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "id": range(1, 7),
                "partition": [
                    "train",
                    "train",
                    "train",
                    "validation",
                    "validation",
                    "test",
                ],
                "cv_fold": [0, 1, 2, np.nan, np.nan, np.nan],
            }
        )

    @contextmanager
    def _fixture_repo(self, source=None, manifest=None):
        with tempfile.TemporaryDirectory() as raw_directory:
            root = Path(raw_directory)
            source_path = root / "data" / "allstate_claims_data.csv"
            manifest_path = (
                root
                / "notebooks"
                / "final-deliverables"
                / "October"
                / "Gate 1"
                / "partition_manifest.csv"
            )
            source_path.parent.mkdir(parents=True)
            manifest_path.parent.mkdir(parents=True)
            (source if source is not None else self._source_frame()).to_csv(
                source_path, index=False
            )
            (manifest if manifest is not None else self._manifest_frame()).to_csv(
                manifest_path, index=False
            )
            with patch.multiple(
                pipeline,
                SOURCE_SHA256=_sha256(source_path),
                MANIFEST_SHA256=_sha256(manifest_path),
                PARTITION_COUNTS={"train": 3, "validation": 2, "test": 1},
                TRAIN_FOLD_COUNTS={0: 1, 1: 1, 2: 1},
            ):
                yield root

    def test_real_files_obey_frozen_contract(self):
        data = pipeline.load_frozen_partitions(REPO_ROOT)

        self.assertEqual(len(data.X_train), 131_822)
        self.assertEqual(len(data.X_validation), 28_248)
        self.assertEqual(data.X_train.columns.tolist(), pipeline.FEATURE_COLUMNS)
        self.assertEqual(data.X_validation.columns.tolist(), pipeline.FEATURE_COLUMNS)
        self.assertEqual(data.train_ids.nunique(), 131_822)
        self.assertEqual(data.validation_ids.nunique(), 28_248)
        self.assertTrue(set(data.train_ids).isdisjoint(data.validation_ids))
        self.assertEqual(
            data.cv_fold.value_counts().sort_index().to_dict(),
            {0: 26_365, 1: 26_365, 2: 26_364, 3: 26_364, 4: 26_364},
        )
        self.assertFalse(hasattr(data, "X_test"))
        self.assertFalse(hasattr(data, "test_ids"))
        self.assertEqual(
            pipeline.sha256_file(REPO_ROOT / pipeline.SOURCE_RELATIVE_PATH),
            pipeline.SOURCE_SHA256,
        )
        self.assertEqual(
            pipeline.sha256_file(REPO_ROOT / pipeline.MANIFEST_RELATIVE_PATH),
            pipeline.MANIFEST_SHA256,
        )

    def test_test_rows_are_removed_before_feature_target_objects(self):
        source = self._source_frame()
        source.loc[source["id"] == 6, "cat1"] = "TEST_ONLY"
        source.loc[source["id"] == 6, "loss"] = 999_999_999.0
        with self._fixture_repo(source=source) as root:
            data = pipeline.load_frozen_partitions(root)

        self.assertNotIn("TEST_ONLY", data.X_train["cat1"].tolist())
        self.assertNotIn("TEST_ONLY", data.X_validation["cat1"].tolist())
        self.assertNotIn(999_999_999.0, data.y_train.tolist())
        self.assertNotIn(999_999_999.0, data.y_validation.tolist())

    def test_reordered_manifest_ids_are_rejected(self):
        manifest = self._manifest_frame().iloc[::-1].reset_index(drop=True)
        with self._fixture_repo(manifest=manifest) as root:
            with self.assertRaisesRegex(ValueError, "ID order"):
                pipeline.load_frozen_partitions(root)

    def test_duplicate_source_ids_are_rejected(self):
        source = self._source_frame()
        source.loc[5, "id"] = 5
        with self._fixture_repo(source=source) as root:
            with self.assertRaisesRegex(ValueError, "unique"):
                pipeline.load_frozen_partitions(root)

    def test_missing_manifest_ids_are_rejected(self):
        manifest = self._manifest_frame().iloc[:-1]
        with self._fixture_repo(manifest=manifest) as root:
            with self.assertRaisesRegex(ValueError, "ID coverage"):
                pipeline.load_frozen_partitions(root)

    def test_unexpected_partition_is_rejected(self):
        manifest = self._manifest_frame()
        manifest.loc[5, "partition"] = "holdout"
        with self._fixture_repo(manifest=manifest) as root:
            with self.assertRaisesRegex(ValueError, "partition"):
                pipeline.load_frozen_partitions(root)

    def test_missing_or_extra_source_fields_are_rejected(self):
        for changed in (
            self._source_frame().drop(columns="cont14"),
            self._source_frame().assign(log1p_loss=1.0),
        ):
            with self.subTest(columns=len(changed.columns)):
                with self._fixture_repo(source=changed) as root:
                    with self.assertRaisesRegex(ValueError, "source schema"):
                        pipeline.load_frozen_partitions(root)

    def test_incomplete_or_nonintegral_training_folds_are_rejected(self):
        for bad_value in (np.nan, 0.5):
            manifest = self._manifest_frame()
            manifest.loc[0, "cv_fold"] = bad_value
            with self.subTest(bad_value=bad_value):
                with self._fixture_repo(manifest=manifest) as root:
                    with self.assertRaisesRegex(ValueError, "cv_fold"):
                        pipeline.load_frozen_partitions(root)

    def test_predefined_split_preserves_recorded_fold_assignments(self):
        folds = pd.Series([0, 1, 2, 0], dtype="int64")

        split = pipeline.make_predefined_split(folds)

        np.testing.assert_array_equal(split.test_fold, [0, 1, 2, 0])


if __name__ == "__main__":
    unittest.main()
