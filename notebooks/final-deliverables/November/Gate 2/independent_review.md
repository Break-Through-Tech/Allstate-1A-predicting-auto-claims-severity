# November Gate 2 Independent Review

## Reviewer

**Reviewer:** Ella Zou (not the evaluation author)

**Review date:** 2026-11-17

**Evaluation author:** Jonathan Deng

**Reviewed commit:** `ffdcb781f5cb076cc7369646920a63cd9dd390e7` (branch `jonathan`, "final evaluation notebook")

**Review procedure:** the eight independent-review steps in `notebooks/final-deliverables/November/Gate 1/frozen_final_evaluation_plan.md` (branch `rn-issue-57`)

**Verification script:** `notebooks/final-deliverables/November/Gate 2/verification/reproduce_final_test_evaluation.py`

**Environment:** isolated Python 3.9.6 virtual environment with CatBoost 1.2.10, pandas 2.3.3, and NumPy 2.0.2. The author's environment was Python 3.14.4, pandas 3.0.6, and NumPy 2.5.3; CatBoost matched exactly.

## Checks

The verification script ran 25 automated checks; all passed.

- [x] **1. Frozen hashes and partition counts.** The SHA-256 hashes of the source data, split manifest, saved `.cbm` model, 75-feature list, and tail-threshold file all match the frozen plan. Partitions are 131,822 train, 28,248 validation, and 28,248 test, and the manifest joins one-to-one on `id` (188,318 rows).
- [x] **2. Overall MAE recomputed.** Recomputed from `final_test_predictions.csv`: `1141.571999`. This matches the receipt and `final_test_model_comparison.csv`.
- [x] **3. Constant baselines on the same IDs.** The training constants reproduce: mean `3038.8403` and median `2115.39`. Their test MAEs reproduce: `1963.447313` (mean) and `1806.345236` (median).
- [x] **4. Segment membership, support, and MAE.** All segment labels match the frozen training thresholds (p90 `6401.738`, p99 `14024.1433`).

  | Segment | Claims | MAE |
  |---|---:|---:|
  | Below p90 | 25,424 | 870.38 |
  | p90 to p99 | 2,559 | 2,982.06 |
  | p99 and above | 265 | 9,386.40 |

- [x] **5. Model and feature configuration.**
  - The model loads from the saved `.cbm` file: MAE loss, depth 8, learning rate 0.08, 500 trees, seed 42.
  - The model's feature order matches the 75-feature list; 61 of the features are categorical.
- [x] **6. No post-test model changes.**
  - The model and feature-list files were last changed in commit `164653a` (2026-11-08), before test scoring.
  - The evaluation notebook contains no `fit`, cross-validation, or feature-importance calls.
  - The reviewed branch adds only the five Gate 2 files.
- [x] **7. Fresh deterministic inference.**
  - A fresh prediction run from the saved model matches the saved predictions to a maximum absolute difference of `1.82e-12`.
  - All 28,248 predictions are finite and non-negative.
  - Saved predictions cover exactly the 28,248 test IDs, and the saved `loss` values match the source.
- [x] **8. Decision recorded** (below).

## Findings

**Metrics.** Every reported metric reproduces exactly:
- CatBoost test MAE: 1,141.57
- improvement over the training-mean constant: 41.86%
- improvement over the training-median constant: 36.80%

The test MAE falls between the October CV result (1,153.58 ± 7.19) and the October validation result (1,136.34).

**Artifact discrepancies.** These are not metric defects, but they are differences from the frozen plan's "Planned Gate 2 Outputs" that the team should resolve or accept before Gate 2 approval:

1. **Paths differ from the plan.**
   - The notebook is `final_test_evaluation.ipynb`, not the planned `final_evaluation.ipynb`.
   - The outputs are in `test_evaluation_outputs/`, not the planned `final_evaluation_results/`.
   - Two file names differ from the plan:
     - `final_test_model_comparison.csv` instead of `final_evaluation_summary.csv`
     - `final_test_evaluation_receipt.json` instead of `final_evaluation_receipt.json`
2. **Planned outputs are missing:** `largest_absolute_errors.csv`, `final_evaluation_checks.csv`, and `final_evaluation_summary.md`.
3. **`final_test_predictions.csv` is missing planned columns:** signed error, plus mean- and median-constant predictions and errors.
4. **`final_test_tail_diagnostics.csv` covers CatBoost only.** The plan asks for per-model segment MAE, including both constants.
5. **The receipt is incomplete.** It does not record the Git commit, working-tree status, UTC run time, or output-file hashes required by plan step 1.

These items can be fixed by extending the evaluation notebook's output step. That would not change the model, features, constants, thresholds, or metric code, so the frozen plan permits a deterministic rerun.

## Decision

- [x] Critical final metrics independently reproduced
- [ ] Gate 2 approved
- [ ] Gate 2 blocked

**Notes:** The final metrics are verified with no metric, alignment, or reproducibility discrepancy. Gate 2 approval is pending the team's resolution of the artifact discrepancies above and approval of the November Gate 1 frozen plan (Issue #57).
