# Frozen Final-Evaluation Plan

**Milestone:** November Gate 1  
**Issues:** #57, with execution carried forward to #58  
**Status:** Frozen before protected-test scoring  
**Frozen date:** 2026-11-16  
**Primary metric:** Mean absolute error in original `loss` units  
**Protected-test claims:** 28,248  
**Approval:** Pending November Gate 1 review

## Purpose

This document fixes the final evaluation procedure before the team scores the
protected test partition. The evaluation will measure the saved October
CatBoost model without retraining it or changing its features, configuration,
or preprocessing.

The team will report the result produced by this procedure. Test performance
will not trigger another round of model tuning or feature selection.

## Frozen Inputs

| Input | Path | Frozen identity or value |
|---|---|---|
| Modeling data | `data/allstate_claims_data.csv` | `OCT-MD-001`; SHA-256 `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03` |
| Split manifest | `notebooks/final-deliverables/October/Gate 1/partition_manifest.csv` | `OCT-SPLIT-001`; SHA-256 `de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b` |
| Saved model | `notebooks/liam-stapley/model_experiment_outputs/final_top75_catboost_model.cbm` | SHA-256 `f2e364cf596c5fb6b36a7508b439a3f14a11e42b8a3faa3249543f70bfc8a27c` |
| Selected features | `notebooks/liam-stapley/model_experiment_outputs/final_catboost_features.csv` | 75 unique predictors; SHA-256 `b960c7574527e4f0bc7785353006f99c8d973be320efbe248ec9a5c55e99c2c0` |
| Reference inference pipeline | `notebooks/final-deliverables/October/Gate 3/final_model_pipeline.ipynb` | SHA-256 `eb48bd1ec10ad01f464c5487fa1b27ebc1e01f707ad98c2e3dcc2a79e0b122bb` |
| Baseline notebook | `notebooks/final-deliverables/October/Gate 2/constant_baselines.ipynb` | SHA-256 `c28e98b34d445bef9780254ca74067f829b517b58700106069acca6e18771cba` |
| Tail thresholds | `notebooks/final-deliverables/October/Gate 1/high_loss_support.csv` | SHA-256 `043462ad0f3c5ac28d2467ec259c1c4e2aa340f6b2be385c04f36ee2f7df08d9` |

The hashes above describe the files reviewed for this plan at commit
`4c50ff47c76da18882b113bf3e00a8d311e2e633`. Before evaluation, the runner
must stop if any hash differs. A planned repository move may change a path, but
the file hash must remain unchanged and the move must be documented.

## Frozen Candidate

| Setting | Frozen value |
|---|---|
| Model | `CatBoostRegressor` loaded from the saved `.cbm` file |
| Training claims | 131,822 |
| Selected predictors | 75, including 61 categorical predictors |
| Loss function | MAE |
| Tree depth | 8 |
| Learning rate | 0.08 |
| Maximum iterations | 500 |
| Random seed | 42 |
| Categorical handling | Convert selected categorical values to strings and use the saved model's native CatBoost handling |
| Numeric handling | Use selected continuous values directly |
| Target transformation | None |
| Scaling or one-hot encoding | None |

The evaluation code must load the saved model. It must not call `fit`, repeat
cross-validation, recalculate feature rankings, or train a replacement model.

## Frozen Reference Results

These October results provide context. They do not set a pass threshold for the
protected test result.

| Result | MAE |
|---|---:|
| Five-fold training CV mean | 1,153.5829266911792 |
| Five-fold training CV standard deviation | 7.189688568401656 |
| October validation | 1,136.341877632517 |
| Training-mean constant on validation | 1,962.918654312225 |
| Training-median constant on validation | 1,805.0863526621356 |

## Frozen Baseline Comparisons

The final evaluation will compare the CatBoost predictions with two constants
fitted during October on the training partition:

| Comparator | Frozen prediction for every test claim |
|---|---:|
| Required training-mean baseline | 3,038.8402548133095 |
| Training-median comparator | 2,115.39 |

The runner must not recalculate either constant from validation or test labels.
All three approaches must use the same 28,248 protected-test claims.

For each comparator, report:

- test MAE in original `loss` units;
- absolute MAE improvement from CatBoost;
- percentage MAE improvement from CatBoost; and
- the number of evaluated claims.

## Frozen Diagnostics

### Loss segments

Use the October training-loss thresholds without recalculating them:

| Segment | Rule |
|---|---|
| Ordinary-loss | `loss < 6401.738` |
| High-loss | `6401.738 <= loss < 14024.143299999967` |
| Highest-loss | `loss >= 14024.143299999967` |

For CatBoost and both constants, report each segment's support and MAE. For
CatBoost, also report mean signed error, median absolute error, underprediction
count, underprediction rate, maximum absolute error, and maximum observed loss.
Keep support beside every segment metric.

### Prediction checks

Record and require the following checks:

- exactly 28,248 test rows and 28,248 predictions;
- 28,248 unique test IDs;
- one prediction for every test ID and no prediction for a train or validation ID;
- source IDs and manifest IDs align one-to-one;
- all predictions, labels, and absolute errors are finite;
- no missing selected feature;
- 75 unique selected features and 61 selected categorical features;
- saved-model and input hashes match this plan;
- prediction order matches the saved output order; and
- MAE is computed as the mean of row-level absolute errors in original `loss`
  units.

Negative predictions do not invalidate the run. Record their count and minimum
value. Do not clip predictions unless a separately confirmed implementation
defect shows that the saved model was previously evaluated with an approved
clipping rule. No such rule exists at freeze time.

### Extreme errors

Preserve the 20 claims with the largest absolute errors. Record `id`, observed
`loss`, prediction, signed error, absolute error, and loss segment. Use this
table for failure-pattern review, not model revision.

### October comparison

Report the test MAE beside the frozen CV and validation results. Calculate the
absolute and percentage difference from each October reference. Flag the
difference for discussion when either condition holds:

- test MAE differs from October validation MAE by more than 2%; or
- test MAE falls outside the CV mean plus or minus two recorded CV standard
  deviations.

A flag requires an explanation of sampling, tail support, or distribution
differences. It does not authorize tuning or feature selection.

## Execution Procedure

The Gate 2 author will implement this procedure in
`notebooks/final-deliverables/November/Gate 2/final_evaluation.ipynb`.

1. Record the Git commit, working-tree status, UTC run time, Python version, and
   package versions.
2. Verify every frozen hash before selecting or scoring the test partition.
3. Load the source and manifest, join one-to-one on `id`, and confirm the frozen
   partition counts: 131,822 train, 28,248 validation, and 28,248 test.
4. Select only rows whose manifest partition equals `test` for inference and
   scoring.
5. Load the 75-feature list in its saved order. Confirm uniqueness, presence,
   and the 61-feature categorical subset.
6. Copy the selected columns and convert selected categorical columns to
   strings. Apply no other preprocessing.
7. Load the saved `.cbm` model and confirm its recorded configuration.
8. Generate one prediction per protected-test claim without fitting the model.
9. Apply the two frozen training-derived constants to the same test claims.
10. Compute overall MAE, baseline improvements, segment diagnostics, prediction
    checks, and the largest-error table.
11. Write all planned outputs before interpreting the result.
12. Rerun the notebook from a fresh kernel and confirm deterministic predictions
    and metrics.
13. Give the artifacts to a teammate who did not author the evaluation for an
    independent recomputation or verification.

The team may execute this frozen workflow more than once for deterministic
reproduction. Every execution must use the same model, features, constants,
thresholds, and metric code. The team must not use repeated executions to make
modeling decisions.

## Planned Gate 2 Outputs

Store the evaluation evidence under
`notebooks/final-deliverables/November/Gate 2/final_evaluation_results/`.

| Artifact | Required contents |
|---|---|
| `final_test_predictions.csv` | `id`, observed `loss`, CatBoost prediction, signed error, absolute error, mean prediction/error, median prediction/error, and segment |
| `final_evaluation_summary.csv` | Overall claim count and MAE for CatBoost, training mean, and training median, plus absolute and percentage improvements |
| `final_tail_diagnostics.csv` | Per-model segment support and MAE; expanded CatBoost error statistics |
| `largest_absolute_errors.csv` | The 20 largest CatBoost absolute errors and their segments |
| `final_evaluation_checks.csv` | One row per integrity, alignment, hash, count, and prediction-validity check |
| `final_evaluation_receipt.json` | Run identity, commit, dirty status, paths, hashes, configuration, versions, counts, metrics, and output hashes |
| `final_evaluation_summary.md` | Plain-language comparison with October evidence, limitations, and no-post-test-change confirmation |
| `independent_review.md` | Reviewer, reviewed commit, independent calculations, discrepancies, decision, and review date |

Do not hand-edit calculated CSV or JSON values. Generate them from the frozen
evaluation notebook.

## Defect and Rerun Policy

A disappointing result, a large CV/validation/test difference, or weak
high-loss performance is not a defect.

A confirmed defect is limited to a reproducible implementation or artifact
failure, such as:

- a frozen hash mismatch or corrupted file;
- selection of the wrong partition;
- duplicate, missing, or misaligned IDs;
- use of the wrong model or feature list;
- preprocessing that differs from the saved-model contract;
- incorrect MAE or diagnostic code; or
- incomplete or non-finite output caused by the evaluation implementation.

If a suspected defect appears, stop the workflow and preserve the failed run.
The author and independent reviewer must document the cause, affected outputs,
and correction before any rerun. A correction may repair evaluation code or
restore the frozen artifact. It may not tune hyperparameters, alter features,
retrain the model, or use test performance to choose a replacement. If the
frozen model itself proves invalid, reopen Gate 1 and treat the protected test
as exposed.

## Interpretation and Reporting Limits

- Describe the result as a final internal held-out evaluation.
- Do not describe it as proof of future-period, production, first-filing, or
  individual-reserve performance.
- State that September EDA used the full labeled dataset before the October
  split was frozen.
- State that later permutation and SHAP ranking used validation observations.
- Keep anonymous predictors anonymous and avoid causal claims.
- Report the highest-loss segment's support with its metrics.
- State that one random split does not measure temporal stability.
- Preserve unsuccessful, negative, or surprising results.

## Independent Review and Approval

A teammate other than the evaluation author must:

1. verify all frozen hashes and partition counts;
2. recompute overall MAE from `final_test_predictions.csv`;
3. recompute both constant-baseline MAEs on the same IDs;
4. verify segment membership, support, and segment MAE;
5. confirm the saved model and 75-feature configuration match this plan;
6. confirm no fitting, tuning, or feature selection occurred after test results
   became visible;
7. compare a fresh deterministic inference run with the saved predictions; and
8. record approval, discrepancies, and the exact reviewed commit.

Gate 2 cannot pass while a metric, alignment, artifact, or reproducibility
discrepancy remains unresolved.

## Freeze Decision

The team freezes the saved top-75 CatBoost model, its preprocessing, MAE, both
training-derived constants, the two training-loss thresholds, diagnostics, and
output requirements before protected-test scoring.

After test results become visible, the team will make no model, feature, or
threshold change unless the defect process above confirms an implementation or
artifact failure. The team will report the corrected frozen evaluation and keep
the failed evidence for traceability.
