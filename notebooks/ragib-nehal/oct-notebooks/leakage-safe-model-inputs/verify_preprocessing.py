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
    for column in CATEGORICAL_COLUMNS:
        train_counts = train[column].value_counts(dropna=False)
        rare_levels = set(train_counts[train_counts < MIN_FREQUENCY].index)
        unseen = ~validation[column].isin(train_counts.index)
        unseen_count = int(unseen.sum())
        if unseen_count:
            unseen_counts[column] = unseen_count
        rare_or_unseen_cells += int(
            (unseen | validation[column].isin(rare_levels)).sum()
        )
    category = unseen_counts == {
        "cat105": 1,
        "cat110": 1,
        "cat113": 1,
        "cat116": 6,
    } and rare_or_unseen_cells == 2_560

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
    baseline = (
        np.isclose(mean_constant, 3038.8402548133095, rtol=0, atol=1e-9)
        and np.isclose(median_constant, 2115.39, rtol=0, atol=1e-9)
        and np.isclose(mean_mae, 1962.918654312225, rtol=0, atol=1e-9)
        and np.isclose(median_mae, 1805.0863526621356, rtol=0, atol=1e-9)
    )

    receipt = json.loads(
        (artifact_dir / "preprocessing_run_receipt.json").read_text()
    )
    checks = pd.read_csv(artifact_dir / "preprocessing_checks.csv")
    expected_artifacts = {
        "preprocessing_checks.csv",
        "category_handling_summary.csv",
        "categorical_vocabulary.json",
        "feature_schema.json",
    }
    artifact_hashes = receipt.get("artifact_sha256", {})
    artifacts = (
        set(artifact_hashes) == expected_artifacts
        and all(
            _sha256(artifact_dir / name) == expected_hash
            for name, expected_hash in artifact_hashes.items()
        )
        and set(checks["status"]) == {"pass"}
        and receipt["library_versions"]["scikit-learn"] == "1.6.1"
        and receipt["target_transform"] == "none"
    )

    return {
        "source_split": bool(source_split),
        "category": bool(category),
        "schema": bool(schema),
        "baseline": bool(baseline),
        "artifacts": bool(artifacts),
    }


def main() -> int:
    default_repo = Path(__file__).resolve().parents[4]
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
