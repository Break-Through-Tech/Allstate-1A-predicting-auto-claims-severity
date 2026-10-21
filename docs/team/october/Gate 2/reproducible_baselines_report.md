# Issue #43: Reproducible Baselines

**Status:** Complete  
**Owner:** Ella Zou  
**Independent reviewer:** Liam Stapley  
**Milestone:** October – Gate 2

## Scope

Implement and independently verify the required constant baselines using the frozen October split.

The required baseline predicts the training mean `loss` for every validation claim. The comparator predicts the training median `loss`.

Both are evaluated using MAE in original `loss` units on the frozen validation partition.

## Final artifacts

- `notebooks/final-deliverables/October/Gate 2/constant_baselines.ipynb`
- `notebooks/final-deliverables/October/Gate 2/baseline_results.csv`
- `notebooks/final-deliverables/October/Gate 2/baseline_predictions.csv`
- `notebooks/final-deliverables/October/Gate 2/baseline_checks.csv`
- `notebooks/final-deliverables/October/Gate 2/baseline_run_receipt.json`
- `tests/test_october_baseline_artifacts.py`
- `notebooks/liam-stapley/verify_baselines.py`

## Frozen data and split

- Modeling-data version: `OCT-MD-001`
- Split version: `OCT-SPLIT-001`
- Training claims: 131,822
- Validation claims: 28,248
- Primary metric: MAE
- Metric units: original `loss` units

The run receipt records the frozen source and partition-manifest hashes, notebook code hash, Git commit, runtime/library versions, and baseline outputs.

## Results

| Model | Role | Fitted constant | Validation MAE |
|---|---|---:|---:|
| Training mean constant | Required baseline | 3,038.840255 | 1,962.918654 |
| Training median constant | Comparator | 2,115.39 | 1,805.086353 |

The median comparator performs better under MAE, which is expected for a constant predictor because the median minimizes absolute error.

This does not replace the required mean baseline. Both are retained and reported.

## Validation protections

- Both constants are fit using training `loss` only.
- Both models are evaluated on validation only.
- Reserved test targets and test scores remain unused.
- No full-file descriptive mean or median is presented as held-out model performance.

## Prediction checks

`baseline_predictions.csv` contains one row per validation claim with:

- `id`
- `training_mean_constant`
- `training_median_constant`

Checks confirm:

- exactly 28,248 validation predictions;
- unique validation IDs;
- exact validation-ID coverage;
- finite predictions; and
- saved prediction values match the fitted constants.

## Independent verification

Liam Stapley independently recomputed the baselines using:

`notebooks/liam-stapley/verify_baselines.py`

The independent calculation reproduced:

- training mean constant: 3,038.840255
- training median constant: 2,115.39
- mean-baseline validation MAE: 1,962.918654
- median-baseline validation MAE: 1,805.086353

The independent script also verified the training/validation claim counts and `baseline_predictions.csv` ID coverage.

## Automated verification

The full test suite passes after adding the saved prediction artifact and verification tests.

The baseline artifact tests independently verify:

- training-only fitting;
- validation-only evaluation;
- fitted constants;
- claim counts;
- validation MAE;
- frozen source/split hashes;
- run receipt consistency;
- notebook code hash;
- finite predictions;
- one prediction per validation claim; and
- protection of the reserved test partition.

## Limitations

These are constant baselines intended to establish a reproducible reference point.

They do not use predictor features and do not represent candidate production models.

Their purpose is to provide a minimum benchmark for later October model experiments.

## Completion

All Issue #43 requirements are complete.

The required mean baseline and median comparator are reproducible, ID-aligned, tied to the frozen split/source, and independently verified.