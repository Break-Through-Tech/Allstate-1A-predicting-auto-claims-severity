# Issue #46 Independent Review Checklist

**Issue:** #46

**Reviewer:** Mia Chavez

**Artifact version / commit:** Pending; reviewer must record the immutable commit reviewed

## Reviewer workflow

Paths below are relative to `notebooks/ragib-nehal/oct-notebooks/feature-experiments-review/`. Run the command from the repository root. `review/reviewer_reproduction/` is reserved for evidence Mia generates herself.

1. Read `docs/team/october/Gate 3/feature_experiments_report.md`, then this checklist.
2. Confirm the source and partition-manifest hashes in `receipt/run_receipt.json`, and confirm `receipt/artifact_manifest.csv` lists this bundle and the canonical report.
3. Run the author verifier without changing its assertions:

```sh
python notebooks/ragib-nehal/oct-notebooks/feature-experiments-review/verification/verify_feature_experiments_review.py
```

4. Execute `analysis/error_analysis.ipynb` from a fresh kernel. Save the environment, command output, and independently generated tables only under `review/reviewer_reproduction/`.
5. Record the immutable commit reviewed, the recalculated comparison, the retained-configuration audit, the review date, and the decision in this checklist and `review/gate3_approval_record.md`.

Author verification does not substitute for this review. Issue #46 does not name a final selected model. Issue #47 owns completion and any provisional candidate. Issue #48 owns the November handoff.

## Reproduction setup

- [ ] Confirm the review commit contains only the expected issue #46 bundle changes.
- [ ] Record Python, NumPy, pandas, and scikit-learn versions under `review/reviewer_reproduction/`.
- [ ] Confirm source SHA-256 `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03`.
- [ ] Confirm manifest SHA-256 `de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b`.

## Fresh execution

- [ ] Execute `analysis/error_analysis.ipynb` from a fresh kernel.
- [ ] Run `verification/verify_feature_experiments_review.py` without changing its assertions.
- [ ] Save the reviewer environment, command output, and independently generated tables under `review/reviewer_reproduction/`.

## Independent comparison-table reproduction

- [ ] Recompute both validation MAEs directly from `outputs/validation_predictions.csv`.
- [ ] Confirm 28,248 unique validation IDs and no protected test IDs.
- [ ] Confirm severity supports of 25,422, 2,547, and 279.
- [ ] Confirm O1 uses exactly the 31 training-derived exclusions and 99 predictors.
- [ ] Confirm the 1% CV-and-validation rule selects E02-full and retains all 130 predictors.

## Retained experiment-configuration audit

- [ ] Verify the retained Issue #46 configuration uses `OCT-SPLIT-001`, seed 42, and folds 0-4.
- [ ] Verify category pooling and the encoder are refitted inside every fold.
- [ ] Verify the categorical mask covers all 116 categorical inputs for E02-full.
- [ ] Verify the receipt settings match the executed HGB pipeline.
- [ ] Verify row-level E02-full predictions reproduce validation MAE 1,151.244420041798 within floating-point tolerance.
- [ ] Verify test rows are not summarized, fitted, predicted, or scored.

## Interpretation and limitations

- [ ] Confirm high-loss support and underprediction limitations are documented.
- [ ] Confirm anonymous predictors are not assigned business meaning or causal effects.
- [ ] Confirm the report treats the results as team findings and does not claim a final selected model.
- [ ] Confirm Issue #48 remains the owner of the November handoff and team decision process.
- [ ] Record every discrepancy, disagreement, environment difference, and unresolved limitation.
- [ ] Confirm the Gate 1 register remains unchanged.

## Review result

**Status:** Pending

**Disagreements or limitations:** Pending independent review

**Date:** Pending
