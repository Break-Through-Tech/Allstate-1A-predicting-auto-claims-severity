"""Independent raw-data verification for the Issue #44 review package."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


SOURCE_HASH = "74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03"
MANIFEST_HASH = "de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b"
CATEGORICAL_COLUMNS = [f"cat{i}" for i in range(1, 117)]
CONTINUOUS_COLUMNS = [f"cont{i}" for i in range(1, 15)]
FEATURE_COLUMNS = CATEGORICAL_COLUMNS + CONTINUOUS_COLUMNS
MIN_FREQUENCY = 132


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(repo_root: Path, artifact_dir: Path) -> dict[str, bool]:
    """Recompute evidence from frozen inputs instead of trusting saved statuses."""

    repo_root = Path(repo_root).resolve()
    artifact_dir = Path(artifact_dir).resolve()
    source_path = repo_root / "data" / "allstate_claims_data.csv"
    manifest_path = (
        repo_root
        / "notebooks"
        / "final-deliverables"
        / "October"
        / "Gate 1"
        / "partition_manifest.csv"
    )
    source = pd.read_csv(source_path)
    manifest = pd.read_csv(manifest_path)
    aligned = source.merge(
        manifest, on="id", how="inner", validate="one_to_one", sort=False
    )
    modeling = aligned.loc[aligned["partition"] != "test"].copy()
    train = modeling.loc[modeling["partition"] == "train"]
    validation = modeling.loc[modeling["partition"] == "validation"]

    source_split = (
        _sha256(source_path) == SOURCE_HASH
        and _sha256(manifest_path) == MANIFEST_HASH
        and len(source) == len(manifest) == 188_318
        and len(train) == 131_822
        and len(validation) == 28_248
        and manifest["partition"].value_counts().to_dict()
        == {"train": 131_822, "validation": 28_248, "test": 28_248}
    )

    unseen_counts = {}
    rare_or_unseen_cells = 0
    category_rows = []
    vocabulary_features = {}
    for column in CATEGORICAL_COLUMNS:
        train_counts = train[column].value_counts(dropna=False)
        frequent_levels = set(train_counts[train_counts >= MIN_FREQUENCY].index)
        rare_levels = set(train_counts[train_counts < MIN_FREQUENCY].index)
        unseen = ~validation[column].isin(train_counts.index)
        unseen_count = int(unseen.sum())
        if unseen_count:
            unseen_counts[column] = unseen_count
        rare_or_unseen = int(
            (unseen | validation[column].isin(rare_levels)).sum()
        )
        rare_or_unseen_cells += rare_or_unseen
        category_rows.append(
            {
                "feature": column,
                "train_levels": int(len(train_counts)),
                "frequent_train_levels": int(len(frequent_levels)),
                "rare_train_levels": int(len(rare_levels)),
                "rare_train_cells": int(train_counts.loc[list(rare_levels)].sum())
                if rare_levels
                else 0,
                "validation_unseen_cells": unseen_count,
                "validation_rare_or_unseen_cells": rare_or_unseen,
                "has_rare_bucket": bool(rare_levels),
                "tree_cardinality_after_pooling": int(
                    len(frequent_levels) + bool(rare_levels)
                ),
            }
        )
        frequent = train_counts[train_counts >= MIN_FREQUENCY]
        rare = train_counts[train_counts < MIN_FREQUENCY]
        vocabulary_features[column] = {
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
    saved_summary = pd.read_csv(artifact_dir / "category_handling_summary.csv")
    computed_summary = pd.DataFrame(category_rows)
    saved_vocabulary = json.loads(
        (artifact_dir / "categorical_vocabulary.json").read_text()
    )
    computed_vocabulary = {
        "fitted_on": "OCT-SPLIT-001 train partition only",
        "min_frequency": MIN_FREQUENCY,
        "missing_value": "__MISSING__",
        "rare_value": "__INFREQUENT__",
        "features": vocabulary_features,
    }
    category = (
        unseen_counts
        == {
        "cat105": 1,
        "cat110": 1,
        "cat113": 1,
        "cat116": 6,
        }
        and rare_or_unseen_cells == 2_560
        and saved_summary.equals(computed_summary)
        and saved_vocabulary == computed_vocabulary
    )

    schema_document = json.loads((artifact_dir / "feature_schema.json").read_text())
    schema = (
        source.columns.tolist() == ["id"] + FEATURE_COLUMNS + ["loss"]
        and schema_document["feature_columns"] == FEATURE_COLUMNS
        and schema_document["excluded_fields"] == ["id", "loss"]
        and schema_document["target_transform"] == "none"
        and schema_document["model_families"]["hist_gradient_boosting"][
            "categorical_mask"
        ]
        == [True] * 116 + [False] * 14
    )

    mean_constant = float(train["loss"].mean())
    median_constant = float(train["loss"].median())
    mean_mae = float(np.mean(np.abs(validation["loss"] - mean_constant)))
    median_mae = float(np.mean(np.abs(validation["loss"] - median_constant)))
    receipt = json.loads(
        (artifact_dir / "preprocessing_run_receipt.json").read_text()
    )
    saved_baselines = receipt.get("baseline_reproduction", {})
    baseline = (
        np.isclose(mean_constant, 3038.8402548133095, rtol=0, atol=1e-9)
        and np.isclose(median_constant, 2115.39, rtol=0, atol=1e-9)
        and np.isclose(mean_mae, 1962.918654312225, rtol=0, atol=1e-9)
        and np.isclose(median_mae, 1805.0863526621356, rtol=0, atol=1e-9)
        and np.isclose(
            saved_baselines["training_mean_constant"]["fitted_constant"],
            mean_constant,
            rtol=0,
            atol=1e-9,
        )
        and np.isclose(
            saved_baselines["training_mean_constant"]["validation_mae"],
            mean_mae,
            rtol=0,
            atol=1e-9,
        )
        and np.isclose(
            saved_baselines["training_median_constant"]["fitted_constant"],
            median_constant,
            rtol=0,
            atol=1e-9,
        )
        and np.isclose(
            saved_baselines["training_median_constant"]["validation_mae"],
            median_mae,
            rtol=0,
            atol=1e-9,
        )
    )

    checks = pd.read_csv(artifact_dir / "preprocessing_checks.csv")
    expected_artifacts = {
        "preprocessing_checks.csv",
        "category_handling_summary.csv",
        "categorical_vocabulary.json",
        "feature_schema.json",
    }
    artifact_hashes = receipt.get("artifact_sha256", {})
    preprocessing_code_path = repo_root / receipt["preprocessing_code_path"]
    artifacts = (
        set(artifact_hashes) == expected_artifacts
        and all(
            _sha256(artifact_dir / name) == expected_hash
            for name, expected_hash in artifact_hashes.items()
        )
        and set(checks["status"]) == {"pass"}
        and receipt["library_versions"]["scikit-learn"] == "1.6.1"
        and receipt["target_transform"] == "none"
        and preprocessing_code_path.is_file()
        and _sha256(preprocessing_code_path)
        == receipt["preprocessing_code_sha256"]
    )

    return {
        "source_split": bool(source_split),
        "category": bool(category),
        "schema": bool(schema),
        "baseline": bool(baseline),
        "artifacts": bool(artifacts),
    }


def main() -> int:
    default_repo = Path(__file__).resolve().parents[5]
    default_artifacts = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=default_repo)
    parser.add_argument("--artifact-dir", type=Path, default=default_artifacts)
    args = parser.parse_args()

    results = verify(args.repo_root, args.artifact_dir)
    labels = {
        "source_split": "source/split",
        "category": "category",
        "schema": "schema",
        "baseline": "baseline",
        "artifacts": "artifact integrity",
    }
    for key, passed in results.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {labels[key]}")
    if all(results.values()):
        print("Independent preprocessing verification passed (5/5 sections).")
        return 0
    print("Independent preprocessing verification failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
