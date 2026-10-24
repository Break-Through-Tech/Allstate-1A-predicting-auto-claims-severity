# October Experiment Plan


## 1. Fixed elements

| Item | Value |
|---|---|
| Modeling-data version | `OCT-MD-001` (130 predictors, 188,318 eligible claims) |
| Split | `OCT-SPLIT-001`: train 131,822 / validation 28,248 / test 28,248, seed 42 |
| Folds | 5 recorded folds inside train (`cv_fold` in the manifest) |
| Primary metric | MAE in original `loss` units |
| Test partition | Not used in October |
| Model random seed | 42 |

## 2. Required baselines

The Challenge Advisor's required training-mean constant and the training-median comparator were run on the frozen split (run `OCT-BASE-20261021T040859Z-1d82244e`). I recomputed both from the manifest and source file, and they match to four decimals.

| Baseline | Constant fitted on train | Validation MAE |
|---|---|---|
| Training mean constant (required) | 3,038.84 | 1,962.92 |
| Training median constant (comparator) | 2,115.39 | 1,805.09 |

The median constant is 8.0% better than the mean constant. The median is the correct constant to beat, because it minimizes absolute error for a constant prediction.

Two items on the baseline receipt need a decision before Gate 1 closes:

- It records `git_dirty: true`, so the code version is not a clean commit.
- It records scikit-learn 1.5.1, pandas 2.2.2 and numpy 1.26.4. The split manifest records 1.6.1, 2.3.3 and 2.0.2.

The constants are plain train statistics, so the numbers are not in doubt. The cleanest fix is to rerun the baseline notebook from a clean commit on the pinned versions and record that receipt as the approved one. The alternative is to record the mismatch as a documented deviation.

## 3. Model approaches to test after the baselines

Two approaches are required. Both use the same claims in every partition. Preprocessing follows `preprocessing_plan.md`.

### A. Regularized linear regression

- **Hypothesis:** Much of the usable signal is additive across the many binary and low-cardinality categorical fields. A regularized linear model should beat the median constant, but it will leave error on the nonlinear continuous patterns September found (for example, cont2's mean loss rising from about 2,100 to 3,500 while its median stays flat).
- **Practical reason:** Fast, easy to explain, and regularization handles about 670 one-hot columns and the correlated continuous pairs. It speaks directly to OCT-004 and OCT-008 (interpretability).
- **First configuration:** Ridge on pooled one-hot categoricals plus standardized continuous fields. The penalty strength is tuned over a log-spaced grid with the 5 recorded folds.
- **Variants:** `log1p` target with `expm1` back-transform; a Gamma-log GLM.
- **What would count against it:** A validation MAE at or above the median constant's 1,805.09.

### B. Gradient-boosted trees

- **Hypothesis:** Non-monotonic continuous effects and categorical interactions matter, so boosted trees should beat approach A. An absolute-error objective should do better on MAE than squared error, because the target is right-skewed.
- **Practical reason:** Handles mixed types without scaling, tolerates correlated predictors, and supports categorical fields natively. It speaks directly to OCT-003.
- **First configuration:** `HistGradientBoostingRegressor` with `loss="absolute_error"` and the categorical mask from the preprocessing plan. It needs no new dependency. Tuning covers a small grid over learning rate, leaf count and minimum leaf size, plus early stopping that uses a slice of training rows only.
- **Variant:** XGBoost, which the project overview names. `xgboost` is not in `requirements.txt` today, so using it means adding and pinning the dependency first.
- **What would count against it:** No validation gain over approach A, which would suggest the nonlinear signal is weak.

### Not in the first comparison

- Explicit target encoding and CatBoost (see the preprocessing plan, section 9).
- Random forest: optional if time permits.
- Semantic feature engineering: not a priority, because the predictors are anonymous.

## 4. Comparison plan

- **Primary:** validation MAE for each configuration, reported as an absolute value and as a percent change against the median constant (1,805.09) and the mean constant (1,962.92).
- **Stability:** cross-validation MAE mean and standard deviation across the 5 folds, so a validation gain can be judged against fold-to-fold spread.
- **Severity-stratified MAE (OCT-006):** report MAE separately for claims at or below the training 90th percentile (6,401.74), between the 90th and 99th (14,024.14), and above the 99th. In validation there are 2,826 claims above the 90th and 279 above the 99th. For the median constant, MAE is about 7,532 on claims above the 90th and about 1,169 on the rest, so most absolute error sits in the tail and overall MAE alone can hide it.
- **Run order:** reproduce the baselines, then approach A, then approach B, then at most 3 validation-guided iterations.
- **Stopping rule (from `OCT-SPLIT-001`):** stop after 3 validation-guided iterations, or earlier if an iteration improves validation MAE by less than 1% over the best previous result. Every validation MAE is logged, including poor ones.
- **Selection limits:** tune only inside the 5 training folds. Validation is a limited comparison check, not a tuning set.

## 5. Optional experiments (if time permits)

Each uses the same split and is labeled optional in the register.

- O1: drop near-constant categorical fields (OCT-002).
- O2: handle correlated continuous pairs by dropping one member or using regularization (OCT-004).
- O3: data-driven feature selection fitted inside CV folds (OCT-007).
- O4: `log1p` training target with `expm1` back-transform.

## 6. Experiment record

Every run gets one row in `experiment_register.csv` before and after it runs. A planned row states the hypothesis and the comparison. A completed row adds results and cost. The columns cover:

- hypothesis and feature set;
- partition manifest version and SHA-256;
- preprocessing configuration and model configuration;
- seed, tuning method, library versions;
- code version (git commit) and whether the working tree was clean;
- run receipt ID (same structure as `baseline_run_receipt.json`);
- resource cost (wall-clock seconds, peak memory, hardware);
- planned comparison and validation-consultation count.

An approved run must have a clean working tree. A run on a dirty tree is recorded but not used as approved evidence.

## 7. Independent verification

A teammate who did not write the plan or the code checks four things:

1. **Split manifest:** both SHA-256 values, partition counts, and fold sizes.
2. **Leakage boundaries:** the checks listed in `preprocessing_plan.md`, section 11.
3. **Metric code:** an independent recomputation of validation MAE, as `tests/test_october_baseline_artifacts.py` does for the baselines.
4. **Approved plan:** that the plan, register template and approval record agree with each other.

The reviewer's name and result go in `gate1_approval_record.md`.

## 8. Open decisions for the team

- Rare-level threshold of 132 training claims (0.1% of train).
- Scikit-learn gradient boosting first, XGBoost as a variant only if the dependency is added.
- CatBoost and target encoding deferred.
- Whether to rerun the baselines on a clean commit or record the deviation.
- Which teammate owns each experiment row (owners are blank in the register).

## 9. Limitations

- September full-file EDA informed these hypotheses, so validation is not wholly unseen evidence.
- One internal split cannot show stability over time (OCT-009 stays deferred).
- Validation has only 279 claims above the 99th percentile, so tail-error estimates are noisy.
- Model performance alone does not establish production readiness or an individual claim reserve.