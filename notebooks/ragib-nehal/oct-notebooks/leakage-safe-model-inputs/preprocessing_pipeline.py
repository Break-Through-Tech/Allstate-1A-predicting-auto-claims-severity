"""Leakage-safe data and preprocessing contracts for October modeling."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
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
        steps=[("preprocessing", preprocessor), ("model", fitted_estimator)]
    )
