from __future__ import annotations

import hashlib
import json
import importlib.util
import shutil
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import nbformat
from scipy import sparse
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_validate


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


class RecordingRegressor(RegressorMixin, BaseEstimator):
    fit_sizes = []

    def fit(self, X, y):
        type(self).fit_sizes.append(len(y))
        self.constant_ = float(np.mean(y))
        return self

    def predict(self, X):
        return np.full(X.shape[0], self.constant_)


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


class CategoryHandlingTests(unittest.TestCase):
    def _model_frame(self) -> pd.DataFrame:
        columns = {
            "cat1": ["A"] * 132 + ["B"],
            "cat2": ["X"] * 133,
            **{column: ["A"] * 133 for column in pipeline.CATEGORICAL_COLUMNS[2:]},
            **{
                column: np.arange(133, dtype=float) + index
                for index, column in enumerate(
                    pipeline.CONTINUOUS_COLUMNS, start=1
                )
            },
        }
        frame = pd.DataFrame(columns)
        frame.loc[0, "cont1"] = np.nan
        return frame.loc[:, pipeline.FEATURE_COLUMNS]

    def test_rare_grouper_learns_training_counts_only(self):
        train = np.array([["A"]] * 132 + [["B"]], dtype=object)
        validation = np.array([["Z"]] * 200, dtype=object)
        grouper = pipeline.RareCategoryGrouper(min_frequency=132)

        grouper.fit(train)
        transformed = grouper.transform(validation)

        self.assertEqual(grouper.frequent_values_[0], frozenset({"A"}))
        self.assertEqual(grouper.rare_values_[0], frozenset({"B"}))
        self.assertTrue((transformed[:, 0] == pipeline.RARE_VALUE).all())

    def test_rare_grouper_uses_missing_code_without_supported_rare_bucket(self):
        train = np.array([["A"]] * 132, dtype=object)
        grouper = pipeline.RareCategoryGrouper(min_frequency=132).fit(train)

        transformed = grouper.transform(np.array([["UNSEEN"]], dtype=object))

        self.assertTrue(np.isnan(transformed[0, 0]))

    def test_ridge_one_hot_uses_approved_rare_and_unseen_behavior(self):
        train = self._model_frame()
        preprocessor = pipeline.build_ridge_preprocessor().fit(train)
        categorical = preprocessor.named_transformers_["categorical"]
        encoder = categorical.named_steps["encoder"]
        sample = train.iloc[[132, 132, 0]].copy().reset_index(drop=True)
        sample.loc[0, "cat1"] = "UNSEEN"
        sample.loc[2, "cat2"] = "UNSEEN"
        encoded = categorical.transform(sample[pipeline.CATEGORICAL_COLUMNS]).toarray()
        cat1_width = len(encoder.categories_[0])
        cat2_width = len(encoder.categories_[1])

        self.assertEqual(encoder.handle_unknown, "infrequent_if_exist")
        self.assertEqual(encoder.min_frequency, 132)
        self.assertTrue(encoder.sparse_output)
        np.testing.assert_array_equal(
            encoded[0, :cat1_width], encoded[1, :cat1_width]
        )
        self.assertEqual(encoded[2, cat1_width : cat1_width + cat2_width].sum(), 0)

    def test_continuous_imputer_and_scaler_ignore_validation_values(self):
        train = self._model_frame()
        preprocessor = pipeline.build_ridge_preprocessor().fit(train)
        continuous = preprocessor.named_transformers_["continuous"]
        imputer = continuous.named_steps["imputer"]
        scaler = continuous.named_steps["scaler"]

        self.assertAlmostEqual(imputer.statistics_[0], 67.5)
        self.assertAlmostEqual(scaler.mean_[0], 67.5)

        validation = train.iloc[[0]].copy()
        validation.loc[:, "cont1"] = 1_000_000.0
        continuous.transform(validation[pipeline.CONTINUOUS_COLUMNS])
        self.assertAlmostEqual(imputer.statistics_[0], 67.5)
        self.assertAlmostEqual(scaler.mean_[0], 67.5)

    def test_tree_preprocessor_uses_pooled_and_missing_codes(self):
        train = self._model_frame()
        preprocessor = pipeline.build_tree_preprocessor().fit(train)
        sample = train.iloc[[0, 1]].copy()
        sample.loc[sample.index[0], "cat1"] = "UNSEEN"
        sample.loc[sample.index[1], "cat2"] = "UNSEEN"

        transformed = preprocessor.transform(sample)
        training_transformed = preprocessor.transform(train.iloc[[132]])

        self.assertEqual(transformed[0, 0], training_transformed[0, 0])
        self.assertTrue(np.isnan(transformed[1, 1]))
        self.assertEqual(transformed.shape[1], 130)


class ModelFamilyPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = pipeline.load_frozen_partitions(REPO_ROOT)

    def test_training_pipeline_refits_preprocessing_inside_each_fold(self):
        RecordingRegressor.fit_sizes = []
        X = self.data.X_train.iloc[:15].copy()
        y = self.data.y_train.iloc[:15].copy()
        folds = pipeline.make_predefined_split(
            pd.Series([0] * 5 + [1] * 5 + [2] * 5)
        )
        model = pipeline.build_training_pipeline("ridge", RecordingRegressor())

        cross_validate(model, X, y, cv=folds, scoring="neg_mean_absolute_error")

        self.assertEqual(RecordingRegressor.fit_sizes, [10, 10, 10])

    def test_ridge_outputs_aligned_finite_sparse_matrices(self):
        preprocessor = pipeline.build_ridge_preprocessor().fit(self.data.X_train)

        train_matrix = preprocessor.transform(self.data.X_train)
        validation_matrix = preprocessor.transform(self.data.X_validation)

        self.assertTrue(sparse.issparse(train_matrix))
        self.assertEqual(train_matrix.shape[1], validation_matrix.shape[1])
        self.assertTrue(np.isfinite(train_matrix.data).all())
        self.assertTrue(np.isfinite(validation_matrix.data).all())

    def test_tree_outputs_exact_mask_cardinality_and_nonfinite_policy(self):
        preprocessor = pipeline.build_tree_preprocessor().fit(self.data.X_train)

        train_matrix = preprocessor.transform(self.data.X_train)
        validation_matrix = preprocessor.transform(self.data.X_validation)
        mask = pipeline.tree_categorical_mask()
        summary = pipeline.summarize_category_handling(
            self.data.X_train, self.data.X_validation
        )

        self.assertEqual(train_matrix.shape, (131_822, 130))
        self.assertEqual(validation_matrix.shape, (28_248, 130))
        self.assertEqual(mask, [True] * 116 + [False] * 14)
        self.assertLessEqual(summary["tree_cardinality_after_pooling"].max(), 255)
        self.assertFalse(np.isinf(train_matrix).any())
        self.assertFalse(np.isinf(validation_matrix).any())
        self.assertFalse(np.isnan(train_matrix[:, 116:]).any())
        self.assertFalse(np.isnan(validation_matrix[:, 116:]).any())

    def test_tree_wrapper_sets_explicit_categorical_mask(self):
        estimator = HistGradientBoostingRegressor(max_iter=1, random_state=0)

        model = pipeline.build_training_pipeline(
            "hist_gradient_boosting", estimator
        )

        self.assertEqual(
            model.named_steps["model"].categorical_features,
            [True] * 116 + [False] * 14,
        )

    def test_unknown_model_family_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "model_family"):
            pipeline.build_training_pipeline("random_forest", RecordingRegressor())

    def test_both_training_wrappers_reject_missing_fit_inputs(self):
        X = self.data.X_train.iloc[:200].copy()
        X.loc[X.index[0], "cont1"] = np.nan
        y = self.data.y_train.iloc[:200]
        configurations = (
            ("ridge", RecordingRegressor()),
            (
                "hist_gradient_boosting",
                HistGradientBoostingRegressor(max_iter=1, random_state=0),
            ),
        )

        for family, estimator in configurations:
            with self.subTest(family=family):
                model = pipeline.build_training_pipeline(family, estimator)
                with self.assertRaisesRegex(ValueError, "zero missing"):
                    model.fit(X, y)


class SavedArtifactTests(unittest.TestCase):
    expected_files = {
        "preprocessing_checks.csv",
        "category_handling_summary.csv",
        "categorical_vocabulary.json",
        "feature_schema.json",
        "preprocessing_run_receipt.json",
    }

    def test_all_required_artifacts_exist(self):
        self.assertTrue(hasattr(pipeline, "generate_preprocessing_artifacts"))
        self.assertEqual(
            {path.name for path in ISSUE_DIR.iterdir()} & self.expected_files,
            self.expected_files,
        )

    def test_all_recorded_checks_pass_and_cover_contract(self):
        checks = pd.read_csv(ISSUE_DIR / "preprocessing_checks.csv")
        expected_checks = {
            "source_hash",
            "manifest_hash",
            "partition_counts",
            "test_partition_protected",
            "feature_contract",
            "train_only_fit",
            "category_unseen_counts",
            "category_rare_or_unseen_cells",
            "ridge_matrix",
            "tree_matrix",
            "cv_folds",
            "original_target",
            "mean_baseline_reproduction",
            "median_baseline_reproduction",
        }

        self.assertEqual(set(checks["check_id"]), expected_checks)
        self.assertEqual(set(checks["status"]), {"pass"})

    def test_category_evidence_matches_approved_observations(self):
        summary = pd.read_csv(ISSUE_DIR / "category_handling_summary.csv")
        unseen = summary.set_index("feature")["validation_unseen_cells"]

        self.assertEqual(len(summary), 116)
        self.assertEqual(int(unseen.sum()), 9)
        self.assertEqual(
            unseen[unseen > 0].astype(int).to_dict(),
            {"cat105": 1, "cat110": 1, "cat113": 1, "cat116": 6},
        )
        self.assertEqual(
            int(summary["validation_rare_or_unseen_cells"].sum()), 2_560
        )
        self.assertLessEqual(summary["tree_cardinality_after_pooling"].max(), 255)

    def test_vocabulary_is_train_derived_and_complete(self):
        vocabulary = json.loads(
            (ISSUE_DIR / "categorical_vocabulary.json").read_text()
        )

        self.assertEqual(vocabulary["min_frequency"], 132)
        self.assertEqual(set(vocabulary["features"]), set(pipeline.CATEGORICAL_COLUMNS))
        self.assertEqual(
            len(vocabulary["features"]["cat116"]["frequent_levels"])
            + len(vocabulary["features"]["cat116"]["rare_levels"]),
            306,
        )
        self.assertNotIn("validation_counts", json.dumps(vocabulary))

    def test_feature_schema_names_both_families_and_exclusions(self):
        schema = json.loads((ISSUE_DIR / "feature_schema.json").read_text())

        self.assertEqual(schema["feature_columns"], pipeline.FEATURE_COLUMNS)
        self.assertEqual(schema["categorical_columns"], pipeline.CATEGORICAL_COLUMNS)
        self.assertEqual(schema["continuous_columns"], pipeline.CONTINUOUS_COLUMNS)
        self.assertEqual(schema["excluded_fields"], ["id", "loss"])
        self.assertEqual(schema["target_transform"], "none")
        self.assertEqual(
            schema["model_families"]["hist_gradient_boosting"][
                "categorical_mask"
            ],
            [True] * 116 + [False] * 14,
        )

    def test_receipt_records_versions_hashes_state_and_baselines(self):
        receipt = json.loads(
            (ISSUE_DIR / "preprocessing_run_receipt.json").read_text()
        )

        self.assertEqual(receipt["modeling_data_version"], "OCT-MD-001")
        self.assertEqual(receipt["split_version"], "OCT-SPLIT-001")
        self.assertEqual(receipt["source_sha256"], pipeline.SOURCE_SHA256)
        self.assertEqual(receipt["manifest_sha256"], pipeline.MANIFEST_SHA256)
        self.assertEqual(receipt["library_versions"]["scikit-learn"], "1.6.1")
        self.assertIn("git_commit", receipt)
        self.assertIn("git_dirty_before_run", receipt)
        self.assertIn("preprocessing_code_sha256", receipt)
        self.assertAlmostEqual(
            receipt["baseline_reproduction"]["training_mean_constant"][
                "fitted_constant"
            ],
            3038.8402548133095,
        )
        self.assertAlmostEqual(
            receipt["baseline_reproduction"]["training_mean_constant"][
                "validation_mae"
            ],
            1962.918654312225,
        )
        self.assertAlmostEqual(
            receipt["baseline_reproduction"]["training_median_constant"][
                "validation_mae"
            ],
            1805.0863526621356,
        )
        self.assertNotIn("feature_model_mae", json.dumps(receipt))


class NotebookAndReviewPackageTests(unittest.TestCase):
    notebook_path = ISSUE_DIR / "leakage_safe_model_inputs.ipynb"
    verifier_path = ISSUE_DIR / "verify_preprocessing.py"
    validation_path = ISSUE_DIR / "preprocessing_validation.md"
    approval_path = ISSUE_DIR / "gate2_approval_record.md"
    team_report_path = (
        REPO_ROOT
        / "docs"
        / "team"
        / "october"
        / "Gate 2"
        / "issue_44_independent_review.md"
    )

    def test_notebook_executes_sequentially_and_calls_reusable_module(self):
        notebook = nbformat.read(self.notebook_path, as_version=4)
        code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
        counts = [cell.execution_count for cell in code_cells]
        source = "\n".join(cell.source for cell in code_cells)
        output_text = "\n".join(
            str(output.get("text", ""))
            + str(output.get("data", {}).get("text/plain", ""))
            for cell in code_cells
            for output in cell.get("outputs", [])
        )

        self.assertEqual(counts, list(range(1, len(code_cells) + 1)))
        self.assertIn("REPO_ROOT_OVERRIDE", source)
        self.assertIn("generate_preprocessing_artifacts", source)
        self.assertNotIn("OneHotEncoder(", source)
        self.assertNotIn("RareCategoryGrouper(", source)
        self.assertIn("ridge", output_text.lower())
        self.assertIn("hist_gradient_boosting", output_text.lower())
        self.assertIn("validation_unseen_cells", output_text)
        self.assertNotIn("candidate_validation_mae", output_text)
        self.assertNotIn(str(Path.home()), output_text)

    def test_independent_verifier_recomputes_all_evidence_sections(self):
        spec = importlib.util.spec_from_file_location(
            "issue44_verifier", self.verifier_path
        )
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)

        results = verifier.verify(REPO_ROOT, ISSUE_DIR)

        self.assertEqual(
            set(results), {"source_split", "category", "schema", "baseline", "artifacts"}
        )
        self.assertTrue(all(results.values()))

    def _load_verifier(self):
        spec = importlib.util.spec_from_file_location(
            "issue44_verifier_for_negative_test", self.verifier_path
        )
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        return verifier

    def _copy_artifacts(self, destination: Path):
        for name in SavedArtifactTests.expected_files:
            shutil.copy2(ISSUE_DIR / name, destination / name)

    def test_verifier_rejects_saved_baseline_mismatch(self):
        verifier = self._load_verifier()
        with tempfile.TemporaryDirectory() as raw_directory:
            artifact_dir = Path(raw_directory)
            self._copy_artifacts(artifact_dir)
            receipt_path = artifact_dir / "preprocessing_run_receipt.json"
            receipt = json.loads(receipt_path.read_text())
            receipt["baseline_reproduction"]["training_mean_constant"][
                "validation_mae"
            ] = -999
            receipt_path.write_text(json.dumps(receipt))

            results = verifier.verify(REPO_ROOT, artifact_dir)

        self.assertFalse(results["baseline"])

    def test_verifier_rejects_saved_category_evidence_mismatch(self):
        verifier = self._load_verifier()
        with tempfile.TemporaryDirectory() as raw_directory:
            artifact_dir = Path(raw_directory)
            self._copy_artifacts(artifact_dir)
            summary_path = artifact_dir / "category_handling_summary.csv"
            summary = pd.read_csv(summary_path)
            summary.loc[summary["feature"] == "cat105", "validation_unseen_cells"] = 2
            summary.to_csv(summary_path, index=False)
            vocabulary_path = artifact_dir / "categorical_vocabulary.json"
            vocabulary = json.loads(vocabulary_path.read_text())
            vocabulary["features"]["cat116"]["rare_level_counts"]["ZZ_FAKE"] = 1
            vocabulary_path.write_text(json.dumps(vocabulary))
            receipt_path = artifact_dir / "preprocessing_run_receipt.json"
            receipt = json.loads(receipt_path.read_text())
            receipt["artifact_sha256"][summary_path.name] = _sha256(summary_path)
            receipt["artifact_sha256"][vocabulary_path.name] = _sha256(vocabulary_path)
            receipt_path.write_text(json.dumps(receipt))

            results = verifier.verify(REPO_ROOT, artifact_dir)

        self.assertFalse(results["category"])

    def test_verifier_rejects_recorded_code_hash_mismatch(self):
        verifier = self._load_verifier()
        with tempfile.TemporaryDirectory() as raw_directory:
            artifact_dir = Path(raw_directory)
            self._copy_artifacts(artifact_dir)
            receipt_path = artifact_dir / "preprocessing_run_receipt.json"
            receipt = json.loads(receipt_path.read_text())
            receipt["preprocessing_code_sha256"] = "0" * 64
            receipt_path.write_text(json.dumps(receipt))

            results = verifier.verify(REPO_ROOT, artifact_dir)

        self.assertFalse(results["artifacts"])

    def test_validation_report_covers_evidence_policy_limits_and_handoff(self):
        report = self.validation_path.read_text()

        for heading in (
            "## Observed evidence",
            "## Configured policy",
            "## Limitations",
            "## Issue #45 handoff",
        ):
            self.assertIn(heading, report)

    def test_gate2_record_is_complete_but_pending_and_unsigned(self):
        record = self.approval_path.read_text()

        self.assertIn("Gate 2 status: pending independent review", record)
        self.assertIn("OCT-MD-001", record)
        self.assertIn("OCT-SPLIT-001", record)
        self.assertIn(pipeline.SOURCE_SHA256, record)
        self.assertIn(pipeline.MANIFEST_SHA256, record)
        for artifact in SavedArtifactTests.expected_files:
            self.assertIn(artifact, record)
        self.assertIn("Reviewer: ____________________", record)
        self.assertIn("Review date: ____________________", record)
        self.assertIn("Decision: ____________________", record)

    def test_team_report_is_actionable_and_leaves_decision_unsigned(self):
        report = self.team_report_path.read_text()

        self.assertIn("verify_preprocessing.py", report)
        self.assertIn("python -m unittest", report)
        self.assertIn("Expected independent evidence", report)
        self.assertIn("Artifact inventory", report)
        self.assertIn("Reviewer checklist", report)
        self.assertIn("Reviewer: ____________________", report)
        self.assertIn("Decision: ____________________", report)


if __name__ == "__main__":
    unittest.main()
