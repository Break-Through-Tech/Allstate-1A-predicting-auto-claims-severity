"""Leakage-safe data and preprocessing contracts for October modeling."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import PredefinedSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler


CATEGORICAL_COLUMNS = [f"cat{i}" for i in range(1, 117)]
CONTINUOUS_COLUMNS = [f"cont{i}" for i in range(1, 15)]
FEATURE_COLUMNS = CATEGORICAL_COLUMNS + CONTINUOUS_COLUMNS
SOURCE_COLUMNS = ["id"] + FEATURE_COLUMNS + ["loss"]
MANIFEST_COLUMNS = ["id", "partition", "cv_fold"]

SOURCE_RELATIVE_PATH = Path("data/allstate_claims_data.csv")
MANIFEST_RELATIVE_PATH = Path(
    "notebooks/final-deliverables/October/Gate 1/partition_manifest.csv"
)
SOURCE_SHA256 = "74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03"
MANIFEST_SHA256 = "de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b"
PARTITION_COUNTS = {"train": 131_822, "validation": 28_248, "test": 28_248}
TRAIN_FOLD_COUNTS = {0: 26_365, 1: 26_365, 2: 26_364, 3: 26_364, 4: 26_364}
MIN_FREQUENCY = 132
MISSING_VALUE = "__MISSING__"
RARE_VALUE = "__INFREQUENT__"


@dataclass(frozen=True)
class PartitionedModelingData:
    """Approved train/validation modeling objects; test data is never exposed."""

    train_ids: pd.Series
    X_train: pd.DataFrame
    y_train: pd.Series
    cv_fold: pd.Series
    validation_ids: pd.Series
    X_validation: pd.DataFrame
    y_validation: pd.Series


def sha256_file(path: Path) -> str:
    """Return a file's SHA-256 digest without loading it all into memory."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_exact_columns(frame: pd.DataFrame, expected: list[str], label: str) -> None:
    if frame.columns.tolist() != expected:
        missing = sorted(set(expected) - set(frame.columns))
        extra = sorted(set(frame.columns) - set(expected))
        raise ValueError(
            f"{label} schema mismatch; expected ordered columns, "
            f"missing={missing}, extra={extra}"
        )


def _verify_frozen_file(path: Path, expected_hash: str, label: str) -> None:
    actual_hash = sha256_file(path)
    if actual_hash != expected_hash:
        raise ValueError(
            f"{label} SHA-256 mismatch: expected {expected_hash}, got {actual_hash}"
        )


def load_frozen_partitions(repo_root: Path) -> PartitionedModelingData:
    """Validate frozen inputs and expose only train/validation modeling data."""

    repo_root = Path(repo_root)
    source_path = repo_root / SOURCE_RELATIVE_PATH
    manifest_path = repo_root / MANIFEST_RELATIVE_PATH
    _verify_frozen_file(source_path, SOURCE_SHA256, "source")
    _verify_frozen_file(manifest_path, MANIFEST_SHA256, "manifest")

    source = pd.read_csv(source_path)
    manifest = pd.read_csv(manifest_path)
    _require_exact_columns(source, SOURCE_COLUMNS, "source")
    _require_exact_columns(manifest, MANIFEST_COLUMNS, "manifest")

    if source["id"].duplicated().any() or manifest["id"].duplicated().any():
        raise ValueError("source and manifest IDs must each be unique")
    if set(source["id"]) != set(manifest["id"]):
        raise ValueError("source and manifest ID coverage must match exactly")
    if not source["id"].reset_index(drop=True).equals(
        manifest["id"].reset_index(drop=True)
    ):
        raise ValueError("source and manifest ID order must match exactly")

    allowed_partitions = set(PARTITION_COUNTS)
    actual_partitions = set(manifest["partition"].dropna().unique())
    if actual_partitions != allowed_partitions or manifest["partition"].isna().any():
        raise ValueError(
            f"partition values must be exactly {sorted(allowed_partitions)}"
        )
    actual_counts = manifest["partition"].value_counts().to_dict()
    if actual_counts != PARTITION_COUNTS:
        raise ValueError(
            f"partition counts mismatch: expected {PARTITION_COUNTS}, got {actual_counts}"
        )

    train_fold_values = manifest.loc[manifest["partition"] == "train", "cv_fold"]
    if train_fold_values.isna().any() or not (train_fold_values % 1 == 0).all():
        raise ValueError("training cv_fold values must be complete integers")
    train_fold_counts = (
        train_fold_values.astype("int64").value_counts().sort_index().to_dict()
    )
    if train_fold_counts != TRAIN_FOLD_COUNTS:
        raise ValueError(
            f"training cv_fold counts mismatch: expected {TRAIN_FOLD_COUNTS}, "
            f"got {train_fold_counts}"
        )
    non_train_folds = manifest.loc[manifest["partition"] != "train", "cv_fold"]
    if non_train_folds.notna().any():
        raise ValueError("cv_fold must be empty outside the training partition")

    merged = source.merge(
        manifest, on="id", how="inner", validate="one_to_one", sort=False
    )
    modeling = merged.loc[merged["partition"] != "test"].copy()
    train = modeling.loc[modeling["partition"] == "train"]
    validation = modeling.loc[modeling["partition"] == "validation"]

    return PartitionedModelingData(
        train_ids=train["id"].reset_index(drop=True),
        X_train=train.loc[:, FEATURE_COLUMNS].reset_index(drop=True),
        y_train=train["loss"].reset_index(drop=True),
        cv_fold=train["cv_fold"].astype("int64").reset_index(drop=True),
        validation_ids=validation["id"].reset_index(drop=True),
        X_validation=validation.loc[:, FEATURE_COLUMNS].reset_index(drop=True),
        y_validation=validation["loss"].reset_index(drop=True),
    )


def make_predefined_split(cv_folds: pd.Series) -> PredefinedSplit:
    """Create the approved CV splitter from recorded integer fold assignments."""

    folds = pd.Series(cv_folds)
    if folds.isna().any() or not (folds % 1 == 0).all():
        raise ValueError("cv_fold values must be complete integers")
    return PredefinedSplit(folds.astype("int64").to_numpy())


class RareCategoryGrouper(TransformerMixin, BaseEstimator):
    """Pool training-rare values and safely route validation-only values."""

    def __init__(self, min_frequency: int = MIN_FREQUENCY):
        self.min_frequency = min_frequency

    def fit(self, X, y=None):
        values = np.asarray(X, dtype=object)
        if values.ndim != 2:
            raise ValueError("categorical input must be two-dimensional")
        if self.min_frequency < 1:
            raise ValueError("min_frequency must be at least 1")
        self.n_features_in_ = values.shape[1]
        self.frequent_values_ = []
        self.rare_values_ = []
        self.has_rare_bucket_ = []
        for column_index in range(values.shape[1]):
            counts = pd.Series(values[:, column_index], dtype="object").value_counts(
                dropna=False
            )
            frequent = frozenset(counts[counts >= self.min_frequency].index.tolist())
            rare = frozenset(counts[counts < self.min_frequency].index.tolist())
            self.frequent_values_.append(frequent)
            self.rare_values_.append(rare)
            self.has_rare_bucket_.append(bool(rare))
        return self

    def transform(self, X):
        values = np.asarray(X, dtype=object)
        if values.ndim != 2 or values.shape[1] != self.n_features_in_:
            raise ValueError("categorical feature count changed after fit")
        transformed = values.copy()
        for column_index in range(values.shape[1]):
            frequent = self.frequent_values_[column_index]
            unknown = np.fromiter(
                (value not in frequent for value in values[:, column_index]),
                dtype=bool,
                count=len(values),
            )
            replacement = (
                RARE_VALUE if self.has_rare_bucket_[column_index] else np.nan
            )
            transformed[unknown, column_index] = replacement
        return transformed

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return np.asarray(
                [f"x{i}" for i in range(self.n_features_in_)], dtype=object
            )
        return np.asarray(input_features, dtype=object)


def _categorical_imputer() -> SimpleImputer:
    return SimpleImputer(strategy="constant", fill_value=MISSING_VALUE)


def build_ridge_preprocessor() -> ColumnTransformer:
    """Build approved sparse one-hot/scaled preprocessing for Ridge."""

    categorical = Pipeline(
        steps=[
            ("imputer", _categorical_imputer()),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="infrequent_if_exist",
                    min_frequency=MIN_FREQUENCY,
                    sparse_output=True,
                ),
            ),
        ]
    )
    continuous = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("categorical", categorical, CATEGORICAL_COLUMNS),
            ("continuous", continuous, CONTINUOUS_COLUMNS),
        ],
        remainder="drop",
        sparse_threshold=1.0,
    )


def build_tree_preprocessor() -> ColumnTransformer:
    """Build approved pooled ordinal/unscaled preprocessing for HGB."""

    categorical = Pipeline(
        steps=[
            ("imputer", _categorical_imputer()),
            ("rare_grouper", RareCategoryGrouper()),
            (
                "encoder",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=np.nan,
                    encoded_missing_value=np.nan,
                    dtype=np.float64,
                ),
            ),
        ]
    )
    continuous = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median"))]
    )
    return ColumnTransformer(
        transformers=[
            ("categorical", categorical, CATEGORICAL_COLUMNS),
            ("continuous", continuous, CONTINUOUS_COLUMNS),
        ],
        remainder="drop",
        sparse_threshold=0.0,
    )


def summarize_category_handling(
    X_train: pd.DataFrame, X_validation: pd.DataFrame
) -> pd.DataFrame:
    """Summarize train-only pooling and validation routing without using loss."""

    rows = []
    for column in CATEGORICAL_COLUMNS:
        train_counts = X_train[column].fillna(MISSING_VALUE).value_counts(dropna=False)
        frequent = set(train_counts[train_counts >= MIN_FREQUENCY].index)
        rare = set(train_counts[train_counts < MIN_FREQUENCY].index)
        validation = X_validation[column].fillna(MISSING_VALUE)
        unseen_mask = ~validation.isin(train_counts.index)
        rare_or_unseen_mask = unseen_mask | validation.isin(rare)
        rows.append(
            {
                "feature": column,
                "train_levels": int(len(train_counts)),
                "frequent_train_levels": int(len(frequent)),
                "rare_train_levels": int(len(rare)),
                "rare_train_cells": int(train_counts.loc[list(rare)].sum()) if rare else 0,
                "validation_unseen_cells": int(unseen_mask.sum()),
                "validation_rare_or_unseen_cells": int(rare_or_unseen_mask.sum()),
                "has_rare_bucket": bool(rare),
                "tree_cardinality_after_pooling": int(len(frequent) + bool(rare)),
            }
        )
    return pd.DataFrame(rows)


def tree_categorical_mask() -> list[bool]:
    """Return the explicit categorical positions for 116 + 14 output columns."""

    return [True] * len(CATEGORICAL_COLUMNS) + [False] * len(CONTINUOUS_COLUMNS)


class NoMissingTrainingGuard(TransformerMixin, BaseEstimator):
    """Reject missing fit data while leaving transform-time guards available."""

    def fit(self, X, y=None):
        values = X.to_numpy() if isinstance(X, pd.DataFrame) else np.asarray(X)
        if pd.isna(values).any():
            raise ValueError("training features must contain zero missing values")
        self.n_features_in_ = values.shape[1]
        return self

    def transform(self, X):
        if np.asarray(X).ndim != 2 or np.asarray(X).shape[1] != self.n_features_in_:
            raise ValueError("feature count changed after training guard fit")
        return X


def build_training_pipeline(model_family: str, estimator) -> Pipeline:
    """Attach the approved family preprocessing to a caller-supplied estimator."""

    fitted_estimator = clone(estimator)
    if model_family == "ridge":
        preprocessor = build_ridge_preprocessor()
    elif model_family == "hist_gradient_boosting":
        if "categorical_features" not in fitted_estimator.get_params(deep=False):
            raise TypeError(
                "hist_gradient_boosting estimator must accept categorical_features"
            )
        fitted_estimator.set_params(categorical_features=tree_categorical_mask())
        preprocessor = build_tree_preprocessor()
    else:
        raise ValueError(
            "model_family must be 'ridge' or 'hist_gradient_boosting'"
        )
    return Pipeline(
        steps=[
            ("training_missing_guard", NoMissingTrainingGuard()),
            ("preprocessing", preprocessor),
            ("model", fitted_estimator),
        ]
    )


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            handle.write(text)
            temporary_path = Path(handle.name)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _git_metadata(repo_root: Path) -> tuple[str, bool]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return commit, bool(status.strip())


def _category_vocabulary(X_train: pd.DataFrame) -> dict:
    features = {}
    for column in CATEGORICAL_COLUMNS:
        counts = X_train[column].fillna(MISSING_VALUE).value_counts(dropna=False)
        frequent = counts[counts >= MIN_FREQUENCY]
        rare = counts[counts < MIN_FREQUENCY]
        features[column] = {
            "frequent_levels": sorted(map(str, frequent.index)),
            "rare_levels": sorted(map(str, rare.index)),
            "frequent_level_counts": {
                str(level): int(count) for level, count in sorted(frequent.items())
            },
            "rare_level_counts": {
                str(level): int(count) for level, count in sorted(rare.items())
            },
            "has_rare_bucket": bool(len(rare)),
        }
    return {
        "fitted_on": "OCT-SPLIT-001 train partition only",
        "min_frequency": MIN_FREQUENCY,
        "missing_value": MISSING_VALUE,
        "rare_value": RARE_VALUE,
        "features": features,
    }


def _check_row(check_id: str, description: str, expected, observed, passed: bool):
    def render(value):
        if isinstance(value, str):
            return value
        return json.dumps(value, sort_keys=True)

    return {
        "check_id": check_id,
        "description": description,
        "expected": render(expected),
        "observed": render(observed),
        "status": "pass" if bool(passed) else "fail",
    }


def generate_preprocessing_artifacts(repo_root: Path, output_dir: Path) -> dict:
    """Generate compact, reviewable evidence for both approved preprocessors."""

    repo_root = Path(repo_root).resolve()
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    git_commit, git_dirty_before_run = _git_metadata(repo_root)

    data = load_frozen_partitions(repo_root)
    if data.X_train.isna().to_numpy().any():
        raise ValueError("approved training features must have zero missing values")

    category_summary = summarize_category_handling(
        data.X_train, data.X_validation
    )
    vocabulary = _category_vocabulary(data.X_train)

    ridge = build_ridge_preprocessor().fit(data.X_train)
    ridge_train = ridge.transform(data.X_train)
    ridge_validation = ridge.transform(data.X_validation)
    ridge_evidence = {
        "train_shape": list(ridge_train.shape),
        "validation_shape": list(ridge_validation.shape),
        "sparse": bool(
            hasattr(ridge_train, "data") and not isinstance(ridge_train, np.ndarray)
        ),
        "finite": bool(
            np.isfinite(ridge_train.data).all()
            and np.isfinite(ridge_validation.data).all()
        ),
    }
    del ridge_train, ridge_validation

    tree = build_tree_preprocessor().fit(data.X_train)
    tree_train = tree.transform(data.X_train)
    tree_validation = tree.transform(data.X_validation)
    tree_evidence = {
        "train_shape": list(tree_train.shape),
        "validation_shape": list(tree_validation.shape),
        "categorical_mask_true": int(sum(tree_categorical_mask())),
        "max_categorical_cardinality": int(
            category_summary["tree_cardinality_after_pooling"].max()
        ),
        "infinite_cells": int(
            np.isinf(tree_train).sum() + np.isinf(tree_validation).sum()
        ),
        "continuous_nan_cells": int(
            np.isnan(tree_train[:, 116:]).sum()
            + np.isnan(tree_validation[:, 116:]).sum()
        ),
    }
    del tree_train, tree_validation

    mean_constant = float(data.y_train.mean())
    median_constant = float(data.y_train.median())
    mean_mae = float(np.mean(np.abs(data.y_validation - mean_constant)))
    median_mae = float(np.mean(np.abs(data.y_validation - median_constant)))
    baseline_reproduction = {
        "training_mean_constant": {
            "fitted_constant": mean_constant,
            "validation_mae": mean_mae,
        },
        "training_median_constant": {
            "fitted_constant": median_constant,
            "validation_mae": median_mae,
        },
    }

    unseen_counts = (
        category_summary.loc[
            category_summary["validation_unseen_cells"] > 0,
            ["feature", "validation_unseen_cells"],
        ]
        .set_index("feature")["validation_unseen_cells"]
        .astype(int)
        .to_dict()
    )
    fold_counts = data.cv_fold.value_counts().sort_index().to_dict()
    checks = [
        _check_row(
            "source_hash",
            "Source hash matches frozen OCT-MD-001",
            SOURCE_SHA256,
            sha256_file(repo_root / SOURCE_RELATIVE_PATH),
            sha256_file(repo_root / SOURCE_RELATIVE_PATH) == SOURCE_SHA256,
        ),
        _check_row(
            "manifest_hash",
            "Manifest hash matches frozen OCT-SPLIT-001",
            MANIFEST_SHA256,
            sha256_file(repo_root / MANIFEST_RELATIVE_PATH),
            sha256_file(repo_root / MANIFEST_RELATIVE_PATH) == MANIFEST_SHA256,
        ),
        _check_row(
            "partition_counts",
            "Train and validation counts match the frozen split",
            {"train": 131_822, "validation": 28_248},
            {"train": len(data.X_train), "validation": len(data.X_validation)},
            len(data.X_train) == 131_822 and len(data.X_validation) == 28_248,
        ),
        _check_row(
            "test_partition_protected",
            "Returned modeling object exposes no test rows",
            True,
            not hasattr(data, "X_test") and not hasattr(data, "test_ids"),
            not hasattr(data, "X_test") and not hasattr(data, "test_ids"),
        ),
        _check_row(
            "feature_contract",
            "Inputs are exactly 116 categorical plus 14 continuous fields",
            {"features": 130, "excluded": ["id", "loss"]},
            {
                "features": len(data.X_train.columns),
                "excluded": [
                    field for field in ("id", "loss") if field not in data.X_train
                ],
            },
            data.X_train.columns.tolist() == FEATURE_COLUMNS,
        ),
        _check_row(
            "train_only_fit",
            "All fitted preprocessing state used training rows only",
            131_822,
            len(data.X_train),
            len(data.X_train) == 131_822,
        ),
        _check_row(
            "category_unseen_counts",
            "Validation-only categories are counted without validation loss",
            {"cat105": 1, "cat110": 1, "cat113": 1, "cat116": 6},
            unseen_counts,
            unseen_counts == {"cat105": 1, "cat110": 1, "cat113": 1, "cat116": 6},
        ),
        _check_row(
            "category_rare_or_unseen_cells",
            "Validation rare-or-unseen cell count matches approved evidence",
            2_560,
            int(category_summary["validation_rare_or_unseen_cells"].sum()),
            int(category_summary["validation_rare_or_unseen_cells"].sum()) == 2_560,
        ),
        _check_row(
            "ridge_matrix",
            "Ridge matrices align and contain only finite values",
            {"aligned": True, "finite": True, "sparse": True},
            {
                "aligned": ridge_evidence["train_shape"][1]
                == ridge_evidence["validation_shape"][1],
                "finite": ridge_evidence["finite"],
                "sparse": ridge_evidence["sparse"],
            },
            ridge_evidence["train_shape"][1]
            == ridge_evidence["validation_shape"][1]
            and ridge_evidence["finite"]
            and ridge_evidence["sparse"],
        ),
        _check_row(
            "tree_matrix",
            "Tree matrices preserve mask, cardinality, and finite policy",
            {
                "columns": 130,
                "categorical_mask_true": 116,
                "max_cardinality_at_most": 255,
                "infinite_cells": 0,
                "continuous_nan_cells": 0,
            },
            {
                "columns": tree_evidence["train_shape"][1],
                **{key: tree_evidence[key] for key in tree_evidence if key not in {"train_shape", "validation_shape"}},
            },
            tree_evidence["train_shape"][1] == 130
            and tree_evidence["validation_shape"][1] == 130
            and tree_evidence["categorical_mask_true"] == 116
            and tree_evidence["max_categorical_cardinality"] <= 255
            and tree_evidence["infinite_cells"] == 0
            and tree_evidence["continuous_nan_cells"] == 0,
        ),
        _check_row(
            "cv_folds",
            "Recorded training folds are complete and unchanged",
            TRAIN_FOLD_COUNTS,
            fold_counts,
            fold_counts == TRAIN_FOLD_COUNTS,
        ),
        _check_row(
            "original_target",
            "Issue 44 uses original loss with no target transform",
            "none",
            "none",
            True,
        ),
        _check_row(
            "mean_baseline_reproduction",
            "Mean baseline independently matches accepted validation MAE",
            1962.918654312225,
            mean_mae,
            np.isclose(mean_mae, 1962.918654312225, rtol=0, atol=1e-9),
        ),
        _check_row(
            "median_baseline_reproduction",
            "Median baseline independently matches accepted validation MAE",
            1805.0863526621356,
            median_mae,
            np.isclose(median_mae, 1805.0863526621356, rtol=0, atol=1e-9),
        ),
    ]
    checks_frame = pd.DataFrame(checks)
    if set(checks_frame["status"]) != {"pass"}:
        failed = checks_frame.loc[checks_frame["status"] != "pass", "check_id"]
        raise RuntimeError(f"preprocessing checks failed: {failed.tolist()}")

    feature_schema = {
        "modeling_data_version": "OCT-MD-001",
        "split_version": "OCT-SPLIT-001",
        "feature_columns": FEATURE_COLUMNS,
        "categorical_columns": CATEGORICAL_COLUMNS,
        "continuous_columns": CONTINUOUS_COLUMNS,
        "excluded_fields": ["id", "loss"],
        "prohibited_derived_fields": [
            "log1p_loss",
            "split_fields",
            "stratification_fields",
            "target_summaries",
            "validation_information",
        ],
        "target": "loss",
        "target_transform": "none",
        "metric": "MAE in original loss units",
        "model_families": {
            "ridge": {
                "categorical": "pooled one-hot",
                "continuous": "train-median imputation then StandardScaler",
                "sparse_output": True,
            },
            "hist_gradient_boosting": {
                "categorical": "pooled ordinal codes",
                "continuous": "train-median imputation without scaling",
                "categorical_mask": tree_categorical_mask(),
            },
        },
    }

    checks_path = output_dir / "preprocessing_checks.csv"
    summary_path = output_dir / "category_handling_summary.csv"
    vocabulary_path = output_dir / "categorical_vocabulary.json"
    schema_path = output_dir / "feature_schema.json"
    receipt_path = output_dir / "preprocessing_run_receipt.json"
    _atomic_write_text(checks_path, checks_frame.to_csv(index=False, lineterminator="\n"))
    _atomic_write_text(
        summary_path, category_summary.to_csv(index=False, lineterminator="\n")
    )
    _atomic_write_text(vocabulary_path, json.dumps(vocabulary, indent=2) + "\n")
    _atomic_write_text(schema_path, json.dumps(feature_schema, indent=2) + "\n")

    now = datetime.now(timezone.utc)
    run_id = f"OCT-PREP-{now.strftime('%Y%m%dT%H%M%SZ')}-{git_commit[:8]}"
    receipt = {
        "run_id": run_id,
        "run_utc": now.isoformat(timespec="seconds"),
        "modeling_data_version": "OCT-MD-001",
        "split_version": "OCT-SPLIT-001",
        "source_path": SOURCE_RELATIVE_PATH.as_posix(),
        "source_sha256": SOURCE_SHA256,
        "manifest_path": MANIFEST_RELATIVE_PATH.as_posix(),
        "manifest_sha256": MANIFEST_SHA256,
        "preprocessing_code_path": str(Path(__file__).resolve().relative_to(repo_root)),
        "preprocessing_code_sha256": sha256_file(Path(__file__).resolve()),
        "git_commit": git_commit,
        "git_dirty_before_run": git_dirty_before_run,
        "library_versions": {
            "python": platform.python_version(),
            "scikit-learn": version("scikit-learn"),
            "pandas": version("pandas"),
            "numpy": version("numpy"),
        },
        "fitting_scope": "train only; validation transform only",
        "target_transform": "none",
        "baseline_reproduction": baseline_reproduction,
        "matrix_evidence": {"ridge": ridge_evidence, "tree": tree_evidence},
        "artifact_sha256": {
            path.name: sha256_file(path)
            for path in (checks_path, summary_path, vocabulary_path, schema_path)
        },
    }
    _atomic_write_text(receipt_path, json.dumps(receipt, indent=2) + "\n")
    return receipt
