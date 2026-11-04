#!/usr/bin/env python3
"""Independently verify the draft evidence bundle for issue #46."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd


BUNDLE = Path(__file__).resolve().parent
ROOT = BUNDLE.parents[3]
SOURCE = ROOT / "data/allstate_claims_data.csv"
MANIFEST = ROOT / "notebooks/final-deliverables/October/Gate 1/partition_manifest.csv"
NOTEBOOK = BUNDLE / "error_analysis.ipynb"
COMPARISON = BUNDLE / "feature_experiment_comparison.csv"
DECISIONS = BUNDLE / "feature_decisions.csv"
PREDICTIONS = BUNDLE / "validation_predictions.csv"
DIAGNOSTICS = BUNDLE / "error_diagnostics.csv"
LARGEST = BUNDLE / "largest_errors.csv"
RECEIPT = BUNDLE / "run_receipt.json"
ARTIFACT_MANIFEST = BUNDLE / "artifact_manifest.csv"
IMPLEMENTATION_RECORD = BUNDLE / "issue_46_implementation_record.md"

SOURCE_SHA256 = "74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03"
MANIFEST_SHA256 = "de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b"
EXPECTED_EXCLUDED = {
    "cat15", "cat17", "cat18", "cat19", "cat20", "cat21", "cat22",
    "cat32", "cat33", "cat34", "cat35", "cat42", "cat46", "cat47",
    "cat48", "cat51", "cat55", "cat56", "cat58", "cat59", "cat60",
    "cat61", "cat62", "cat63", "cat64", "cat67", "cat68", "cat69",
    "cat70", "cat77", "cat78",
}
EXPECTED_SUPPORT = {
    "loss < train p90": 25_422,
    "train p90 <= loss < p99": 2_547,
    "loss >= train p99": 279,
    "all validation claims": 28_248,
}
REQUIRED_FILES = [
    NOTEBOOK,
    COMPARISON,
    DECISIONS,
    PREDICTIONS,
    DIAGNOSTICS,
    LARGEST,
    RECEIPT,
    ARTIFACT_MANIFEST,
    BUNDLE / "november_handoff.md",
    BUNDLE / "model_review.md",
    BUNDLE / "review_checklist.md",
    BUNDLE / "gate3_approval_record.md",
    IMPLEMENTATION_RECORD,
    BUNDLE / "reviewer_reproduction/.gitkeep",
]


class VerificationError(AssertionError):
    """Raised when a durable artifact breaks the issue #46 contract."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def notebook_code_sha256(path: Path) -> str:
    notebook = nbformat.read(path, as_version=4)
    code = "\n\n".join(cell.source for cell in notebook.cells if cell.cell_type == "code")
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def artifact_files() -> list[Path]:
    return sorted(
        path
        for path in BUNDLE.rglob("*")
        if path.is_file()
        and path != ARTIFACT_MANIFEST
        and ".ipynb_checkpoints" not in path.parts
        and path.name != ".DS_Store"
    )


def refresh_artifact_manifest() -> None:
    rows = [
        {
            "relative_path": path.relative_to(BUNDLE).as_posix(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in artifact_files()
    ]
    pd.DataFrame(rows).to_csv(ARTIFACT_MANIFEST, index=False)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def check_required_files() -> None:
    missing = [path.relative_to(BUNDLE).as_posix() for path in REQUIRED_FILES if not path.is_file()]
    require(not missing, "missing bundle artifacts: " + ", ".join(missing))


def check_frozen_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    require(sha256(SOURCE) == SOURCE_SHA256, "frozen source SHA-256 mismatch")
    require(sha256(MANIFEST) == MANIFEST_SHA256, "partition manifest SHA-256 mismatch")

    manifest = pd.read_csv(MANIFEST, usecols=["id", "partition", "cv_fold"])
    require(manifest["id"].is_unique, "manifest IDs are not unique")
    require(manifest["partition"].value_counts().to_dict() == {
        "train": 131_822,
        "validation": 28_248,
        "test": 28_248,
    }, "partition counts changed")
    train_manifest = manifest.loc[manifest["partition"] == "train"]
    require(set(train_manifest["cv_fold"].astype(int)) == set(range(5)), "training folds are not 0-4")

    source = pd.read_csv(SOURCE)
    train_ids = set(train_manifest["id"])
    train = source.loc[source["id"].isin(train_ids)].copy()
    require(len(train) == 131_822, "training source join changed")
    return source, manifest, train


def check_feature_rule(train: pd.DataFrame) -> None:
    categorical = [f"cat{i}" for i in range(1, 117)]
    dominant_share = train[categorical].apply(
        lambda column: column.value_counts(dropna=False, normalize=True).iloc[0]
    )
    excluded = set(dominant_share.loc[dominant_share > 0.99].index)
    require(excluded == EXPECTED_EXCLUDED, f"training-derived exclusion set changed: {sorted(excluded)}")

    decisions = pd.read_csv(DECISIONS).set_index("experiment_id")
    require(set(decisions.index) == {"O1", "O2", "O3", "O4"}, "feature decision IDs changed")
    require(decisions.loc["O1", "status"] == "completed", "O1 is not completed")
    require(set(decisions.loc["O1", "excluded_features"].split("|")) == EXPECTED_EXCLUDED,
            "O1 decision does not record the exact exclusion set")
    require((decisions.loc[["O2", "O3", "O4"], "status"] == "deferred").all(),
            "O2-O4 must remain deferred")


def check_predictions_and_metrics(manifest: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    predictions = pd.read_csv(PREDICTIONS)
    expected_columns = [
        "id", "loss", "pred_training_mean", "pred_training_median", "pred_ridge",
        "pred_e02_full", "pred_o1_reduced",
    ]
    require(list(predictions.columns) == expected_columns, "prediction columns changed")
    require(len(predictions) == 28_248 and predictions["id"].is_unique,
            "predictions must contain 28,248 unique validation claims")

    validation_ids = set(manifest.loc[manifest["partition"] == "validation", "id"])
    test_ids = set(manifest.loc[manifest["partition"] == "test", "id"])
    prediction_ids = set(predictions["id"])
    require(prediction_ids == validation_ids, "prediction IDs do not equal the frozen validation IDs")
    require(prediction_ids.isdisjoint(test_ids), "protected test IDs appear in predictions")

    source_truth = pd.read_csv(SOURCE, usecols=["id", "loss"]).set_index("id")["loss"]
    expected_loss = predictions["id"].map(source_truth)
    require(expected_loss.notna().all(), "prediction claim ID is absent from the frozen source")
    require(np.array_equal(predictions["loss"].to_numpy(), expected_loss.to_numpy()),
            "recorded loss does not match the frozen source for its claim ID")

    prediction_columns = [column for column in predictions if column.startswith("pred_")]
    require(np.isfinite(predictions[prediction_columns].to_numpy(dtype=float)).all(),
            "non-finite validation prediction found")

    comparison = pd.read_csv(COMPARISON).set_index("run_id")
    require(set(comparison.index) == {"E02-full", "O1"}, "comparison must contain E02-full and O1")
    require(int(comparison.loc["E02-full", "feature_count"]) == 130, "full E02 feature count changed")
    require(int(comparison.loc["O1", "feature_count"]) == 99, "O1 feature count changed")
    require((comparison["cv_folds"] == 5).all(), "both runs must use five CV folds")
    require((comparison["validation_claims"] == 28_248).all(), "validation claim count changed")

    for run_id, prediction_column in {"E02-full": "pred_e02_full", "O1": "pred_o1_reduced"}.items():
        mae = float(np.mean(np.abs(predictions["loss"] - predictions[prediction_column])))
        require(math.isclose(mae, comparison.loc[run_id, "validation_mae"], abs_tol=1e-9),
                f"{run_id} validation MAE does not recompute")

    cv_gain = 100 * (
        comparison.loc["E02-full", "cv_mae_mean"] - comparison.loc["O1", "cv_mae_mean"]
    ) / comparison.loc["E02-full", "cv_mae_mean"]
    validation_gain = 100 * (
        comparison.loc["E02-full", "validation_mae"] - comparison.loc["O1", "validation_mae"]
    ) / comparison.loc["E02-full", "validation_mae"]
    expected_selected = "O1" if cv_gain >= 1.0 and validation_gain >= 1.0 else "E02-full"
    require(comparison["selected"].sum() == 1, "comparison must select exactly one run")
    actual_selected = comparison.index[comparison["selected"]].item()
    require(actual_selected == expected_selected, "selected run violates the predeclared 1% rule")

    decision = pd.read_csv(DECISIONS).set_index("experiment_id").loc["O1", "decision"]
    expected_decision = "exclude_near_constant_fields" if expected_selected == "O1" else "retain_all_130_predictors"
    require(decision == expected_decision, "O1 feature decision violates the predeclared rule")
    return predictions, comparison


def check_diagnostics(predictions: pd.DataFrame, comparison: pd.DataFrame) -> None:
    diagnostics = pd.read_csv(DIAGNOSTICS)
    require(set(diagnostics["model"]) == {
        "training_mean", "training_median", "ridge", "e02_full", "o1_reduced"
    }, "diagnostic model set changed")
    column_of = {
        "training_mean": "pred_training_mean",
        "training_median": "pred_training_median",
        "ridge": "pred_ridge",
        "e02_full": "pred_e02_full",
        "o1_reduced": "pred_o1_reduced",
    }

    frozen_source = pd.read_csv(SOURCE, usecols=["id", "loss"])
    frozen_manifest = pd.read_csv(MANIFEST, usecols=["id", "partition"])
    train_ids = set(frozen_manifest.loc[frozen_manifest["partition"] == "train", "id"])
    train_loss = frozen_source.loc[frozen_source["id"].isin(train_ids), "loss"]
    train_p90 = float(train_loss.quantile(0.90))
    train_p99 = float(train_loss.quantile(0.99))
    segments = {
        "loss < train p90": predictions["loss"] < train_p90,
        "train p90 <= loss < p99": (
            (predictions["loss"] >= train_p90) & (predictions["loss"] < train_p99)
        ),
        "loss >= train p99": predictions["loss"] >= train_p99,
        "all validation claims": pd.Series(True, index=predictions.index),
    }
    require({name: int(mask.sum()) for name, mask in segments.items()} == EXPECTED_SUPPORT,
            "independently derived severity support counts changed")
    require(len(diagnostics) == len(column_of) * len(segments), "diagnostic row count changed")

    float_fields = {
        "mae": lambda absolute, signed, predicted, actual: float(np.mean(absolute)),
        "mean_signed_error": lambda absolute, signed, predicted, actual: float(np.mean(signed)),
        "median_absolute_error": lambda absolute, signed, predicted, actual: float(np.median(absolute)),
        "p90_absolute_error": lambda absolute, signed, predicted, actual: float(np.quantile(absolute, 0.90)),
        "p99_absolute_error": lambda absolute, signed, predicted, actual: float(np.quantile(absolute, 0.99)),
        "underprediction_rate": lambda absolute, signed, predicted, actual: float(np.mean(predicted < actual)),
    }
    for model, prediction_column in column_of.items():
        for segment, mask in segments.items():
            matching = diagnostics.loc[
                (diagnostics["model"] == model) & (diagnostics["segment"] == segment)
            ]
            require(len(matching) == 1, f"expected one diagnostic row for {model} / {segment}")
            row = matching.iloc[0]
            actual = predictions.loc[mask, "loss"].to_numpy(dtype=float)
            predicted = predictions.loc[mask, prediction_column].to_numpy(dtype=float)
            signed = predicted - actual
            absolute = np.abs(signed)
            require(int(row["support_claims"]) == len(actual),
                    f"{model} / {segment} support does not recompute")
            for field, calculation in float_fields.items():
                expected = calculation(absolute, signed, predicted, actual)
                require(math.isclose(float(row[field]), expected, abs_tol=1e-9),
                        f"{model} / {segment} {field} does not recompute")
            require(int(row["negative_predictions"]) == int((predicted < 0).sum()),
                    f"{model} / {segment} negative prediction count changed")
            require(int(row["non_finite_predictions"]) == int((~np.isfinite(predicted)).sum()),
                    f"{model} / {segment} non-finite prediction count changed")

    largest = pd.read_csv(LARGEST)
    selected_run = comparison.index[comparison["selected"]].item()
    selected_column = "pred_o1_reduced" if selected_run == "O1" else "pred_e02_full"
    expected_largest = predictions[["id", "loss", selected_column]].copy()
    expected_largest = expected_largest.rename(columns={selected_column: "prediction"})
    expected_largest["signed_error"] = expected_largest["prediction"] - expected_largest["loss"]
    expected_largest["abs_error"] = expected_largest["signed_error"].abs()
    expected_largest["selected_run"] = selected_run
    expected_largest = expected_largest.nlargest(25, "abs_error").reset_index(drop=True)
    require(list(largest.columns) == list(expected_largest.columns), "largest-errors columns changed")
    require(largest["id"].tolist() == expected_largest["id"].tolist(),
            "largest-errors export is not the selected model's ordered top 25")
    require((largest["selected_run"] == selected_run).all(), "largest-errors selected run changed")
    for field in ["loss", "prediction", "signed_error", "abs_error"]:
        require(np.allclose(largest[field], expected_largest[field], atol=1e-9, rtol=0),
                f"largest-errors {field} values do not recompute")


def check_receipt_and_notebook() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    require(receipt["modeling_data_version"] == "OCT-MD-001", "modeling data version changed")
    require(receipt["split_version"] == "OCT-SPLIT-001", "split version changed")
    require(receipt["seed"] == 42, "seed changed")
    require(receipt["source_sha256"] == SOURCE_SHA256, "receipt source hash changed")
    require(receipt["manifest_sha256"] == MANIFEST_SHA256, "receipt manifest hash changed")
    require(receipt["notebook_code_sha256"] == notebook_code_sha256(NOTEBOOK),
            "receipt does not match current notebook code")
    require(receipt["validation_consults"] == {"E02-full-reproduction": 1, "O1-new": 1},
            "validation consultation record changed")
    require(receipt["test_policy"] == "test rows excluded before analysis; no test summaries, predictions, or scores",
            "test policy changed")
    require(receipt["model_settings"] == {
        "loss": "absolute_error", "learning_rate": 0.1, "max_leaf_nodes": 63,
        "min_samples_leaf": 50, "max_iter": 200, "early_stopping": True,
        "random_state": 42, "rare_min_frequency": 132,
    }, "model settings changed")
    for library in ["python", "numpy", "pandas", "scikit-learn"]:
        require(library in receipt["library_versions"], f"receipt omits {library} version")
    for relative_path, expected_hash in receipt["output_sha256"].items():
        require(sha256(BUNDLE / relative_path) == expected_hash, f"receipt hash mismatch: {relative_path}")

    notebook = nbformat.read(NOTEBOOK, as_version=4)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    counts = [cell.execution_count for cell in code_cells]
    require(counts == list(range(1, len(counts) + 1)), "notebook was not run top to bottom")
    errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    require(not errors, "notebook contains error output")
    serialized_outputs = json.dumps(
        [output for cell in notebook.cells for output in cell.get("outputs", [])]
    )
    require(str(ROOT) not in serialized_outputs, "notebook output contains an absolute personal path")


def check_pending_review_state() -> None:
    model_review = (BUNDLE / "model_review.md").read_text(encoding="utf-8")
    checklist = (BUNDLE / "review_checklist.md").read_text(encoding="utf-8")
    approval = (BUNDLE / "gate3_approval_record.md").read_text(encoding="utf-8")
    handoff = (BUNDLE / "november_handoff.md").read_text(encoding="utf-8")
    require("**Status:** Ready for independent review" in model_review,
            "model review must remain ready for independent review")
    require("**Reviewer:** Mia Chavez (pending)" in model_review,
            "Mia must remain the pending independent reviewer")
    require("- [x]" not in checklist, "review checklist contains unverified completion marks")
    require("**Status:** Pending" in checklist, "review checklist status must remain pending")
    require("**Gate decision:** Pending" in approval, "Gate 3 decision must remain pending")
    require(approval.count("| Pending |") >= 6, "all six team decisions must remain pending")
    for experiment_id in ["O2", "O3", "O4"]:
        require(experiment_id in handoff, f"November handoff omits {experiment_id}")
    require("causal" in model_review.lower() and "anonymous" in model_review.lower(),
            "model review lacks anonymous/non-causal interpretation limits")
    require(IMPLEMENTATION_RECORD.is_file(), "completed work lacks an implementation record")
    require(not (BUNDLE / "issue_46_implementation_plan.md").exists(),
            "completed implementation plan was not converted to a record")
    whitespace_offenders = []
    for path in BUNDLE.rglob("*.md"):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.endswith((" ", "\t")):
                whitespace_offenders.append(f"{path.relative_to(BUNDLE)}:{line_number}")
    require(not whitespace_offenders,
            "Markdown trailing whitespace: " + ", ".join(whitespace_offenders))


def check_artifact_manifest() -> None:
    recorded = pd.read_csv(ARTIFACT_MANIFEST).set_index("relative_path")
    expected_paths = {path.relative_to(BUNDLE).as_posix() for path in artifact_files()}
    require(set(recorded.index) == expected_paths, "artifact manifest file list is stale")
    for relative_path, row in recorded.iterrows():
        path = BUNDLE / relative_path
        require(row["sha256"] == sha256(path), f"artifact manifest hash mismatch: {relative_path}")
        require(int(row["bytes"]) == path.stat().st_size, f"artifact manifest byte count mismatch: {relative_path}")


def verify() -> None:
    check_required_files()
    _, manifest, train = check_frozen_inputs()
    check_feature_rule(train)
    predictions, comparison = check_predictions_and_metrics(manifest)
    check_diagnostics(predictions, comparison)
    check_receipt_and_notebook()
    check_pending_review_state()
    check_artifact_manifest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh-manifest",
        action="store_true",
        help="Rewrite artifact_manifest.csv before verification.",
    )
    args = parser.parse_args()
    try:
        if args.refresh_manifest:
            refresh_artifact_manifest()
        verify()
    except (VerificationError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: issue #46 draft bundle verified")
    print("PASS: review and Gate 3 approvals remain pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
