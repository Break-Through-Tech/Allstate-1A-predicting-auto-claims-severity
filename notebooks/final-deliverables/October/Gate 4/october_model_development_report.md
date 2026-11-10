# October Model Development Report

## Overview

October focused on establishing a reproducible modeling process for Allstate claim severity prediction using the frozen modeling dataset `OCT-MD-001` and split `OCT-SPLIT-001`.

The work progressed from constant baselines through linear models, tree-based models, gradient boosting, XGBoost, and CatBoost. The final October recommendation is a feature-selected CatBoost regression model using 75 predictors.

The protected test partition remains unused. All model-selection results reported here are retrospective validation results and should not be interpreted as verified future or first-filing performance.

---

## Data and Split Design

The frozen modeling dataset contains 188,318 claims.

The approved split contains:

| Partition | Claims |
|---|---:|
| Train | 131,822 |
| Validation | 28,248 |
| Protected test | 28,248 |

Training includes five fixed cross-validation folds with approximately 26,364 claims per fold.

The split uses seed 42 and was designed to preserve the target distribution using loss quantile bins.

The source and partition manifest are versioned and hash-verified before modeling.

The protected test partition has not been used for model fitting, feature selection, model comparison, prediction, or scoring.

---

## Inputs and Encoding

The source dataset contains:

- 116 anonymous categorical predictors: `cat1` through `cat116`
- 14 anonymous continuous predictors: `cont1` through `cont14`
- `id`
- target `loss`

`id` and `loss` are excluded from model inputs.

Because the predictors are anonymous, importance scores and coefficients are interpreted only as evidence of predictive usefulness. They do not establish business meaning or causal relationships.

Preprocessing differs appropriately by model family.

The following descriptions summarize each compared technique in terms the team
can use with the Challenge Advisor. Unless noted otherwise, learned models use
all 130 predictors. Every model produces one numeric estimate of claim `loss` in
the original target units; no target transformation is applied.

| Model | Input fields and encoding | Key settings used in the comparison | Basic learning approach | Prediction output |
|---|---|---|---|---|
| Training-mean constant | Uses no predictor fields. It calculates one constant from the training `loss` values. | Training mean `3038.84`. | Assigns every claim the average training loss; it does not learn relationships between predictors and loss. | The same predicted `loss`, `3038.84`, for every claim. |
| Training-median constant | Uses no predictor fields. It calculates one constant from the training `loss` values. | Training median `2115.39`. | Assigns every claim the middle training loss, which is the strongest constant predictor under MAE. | The same predicted `loss`, `2115.39`, for every claim. |
| Linear Regression | Uses `cat1`–`cat116` after median/mode imputation and one-hot encoding with unseen levels ignored; uses `cont1`–`cont14` after median imputation and standardization. | Ordinary least squares with 1,051 fitted coefficients. | Fits one weight for each encoded input so that their weighted sum best matches training losses. | A weighted-sum estimate of claim `loss`. |
| Ridge Regression | Uses all categorical fields after training-derived rare-level pooling and one-hot encoding; continuous fields are standardized. | `alpha=100`; rare-level threshold `132` training claims. | Learns a linear weight for each encoded input while shrinking the weights to reduce overfitting. | A regularized weighted-sum estimate of claim `loss`. |
| Random Forest | Uses median/mode imputation and ordinal categorical codes; unseen categories map to `-1`. Continuous fields are used without scaling after imputation. | 80 trees; maximum depth 18; `max_features=0.7`; minimum 2 claims per leaf; seed 42. | Fits many decision trees to different samples and predictor subsets, then averages their predictions to reduce the instability of one tree. | The average predicted `loss` across the 80 trees. |
| HistGradientBoosting | Uses training-derived pooled ordinal categorical codes, an explicit categorical-feature mask, and unseen categories treated as missing; continuous fields are unscaled. | Absolute-error loss; learning rate 0.1; up to 63 leaves per tree; minimum 50 claims per leaf; maximum 200 rounds. | Adds small trees sequentially, with each tree correcting errors left by the existing ensemble. | The combined trees' estimate of claim `loss`. |
| XGBoost | Uses all categorical fields through native categorical-tree support with categories defined from training; continuous fields are used directly. | Absolute-error objective; histogram trees; maximum depth 6; learning rate 0.08; maximum 300 trees; 30-round CV early-stopping patience; seed 42. | Adds trees sequentially, using gradient information to focus each new tree on errors made by the preceding trees. | The sum of the boosted trees expressed as predicted claim `loss`. |
| CatBoost | Uses the selected 75 predictors. Categorical fields are supplied as categorical/string values for native handling; continuous fields are used directly. | MAE loss; depth 8; learning rate 0.08; 500 boosting iterations; seed 42. | Adds symmetric trees sequentially and uses CatBoost's ordered categorical statistics to learn from categorical values while limiting target leakage. | The final boosted ensemble's estimate of claim `loss`. |

---

## Baselines

Two constant predictors were retained as references.

| Model | 5-fold CV MAE | Validation MAE |
|---|---:|---:|
| Training mean | 1,968.12 | 1,962.92 |
| Training median | 1,810.48 | 1,805.09 |

The training-mean model is the required project baseline.

The median comparator is also useful because the project evaluates models using mean absolute error.

---

## Approaches Tested

October modeling included:

| Model | CV MAE | Validation MAE |
|---|---:|---:|
| Linear Regression | 1,310.31 | 1,290.13 |
| Ridge Regression | 1,308.55 | 1,290.43 |
| Random Forest | 1,243.54 | 1,223.51 |
| XGBoost | 1,183.31 | 1,162.00 |
| HistGradientBoosting | 1,172.29 | 1,151.17 |
| CatBoost, 130 predictors | 1,160.00 | 1,142.33 |
| CatBoost, top 75, 250 iterations | 1,159.79 | 1,141.14 |
| CatBoost, top 75, 500 iterations | **1,153.58** | **1,136.34** |

Boosted-tree approaches consistently outperformed the linear and Random Forest alternatives.

HistGradientBoosting was the strongest model after the initial controlled comparison. Later CatBoost experiments improved on that result and became the provisional October selection.

---

## Feature Experiments

### CatBoost feature ranking

Three importance measures were used:

- model-based feature importance
- permutation importance
- SHAP importance

Their rankings were aggregated into one feature ranking.

CatBoost was then evaluated using all 130 predictors and the top 75, 50, and 30 ranked predictors.

| Feature set | CV MAE | CV SD |
|---|---:|---:|
| Top 75 | 1,159.79 | 7.59 |
| All 130 | 1,160.00 | 6.89 |
| Top 50 | 1,161.12 | 6.69 |
| Top 30 | 1,167.15 | 6.86 |

The top-75 model produced essentially equivalent or slightly better predictive performance while reducing the model by 55 predictors.

The improvement over all 130 predictors was small relative to fold-to-fold variation, so the main benefit is model simplification rather than a large predictive gain.

### HGB dominant-category experiment

Issue #46 separately tested whether removing 31 categorical predictors whose dominant training level exceeded 99% support improved the retained HGB configuration.

It did not.

Mean CV MAE changed from approximately 1,171.51 to 1,172.58 and validation MAE changed from approximately 1,151.24 to 1,152.50.

The experiment therefore retained all 130 predictors for that HGB comparison.

This does not conflict with the CatBoost top-75 result because the models and feature-selection methods are different.

Additional feature hypotheses from Issue #46 were deferred to November.

---

## Final CatBoost Iteration

The initial CatBoost feature-selection models consistently reached the original 250-iteration limit.

A focused follow-up increased the maximum number of boosting iterations to 500 while retaining:

- top 75 predictors
- MAE loss
- depth 8
- learning rate 0.08
- seed 42

The final five-fold result was:

- CV MAE: **1,153.58**
- CV SD: **7.19**
- mean best iteration: **497.2**

The best iterations remained close to the new 500-round limit.

The final fitted model was then trained on all 131,822 training claims and serialized as a reusable CatBoost `.cbm` artifact.

---

## Error Patterns

Prediction error increases substantially for high-loss claims.

The common diagnostic uses training thresholds:

- p90 loss: 6,401.74
- p99 loss: 14,024.14

Validation support is:

| Segment | Claims |
|---|---:|
| Below p90 | 25,422 |
| p90 to p99 | 2,547 |
| p99 and above | 279 |

These segment results are diagnostics rather than replacement model-selection metrics.

Large claims remain considerably harder to predict across all tested approaches. The p99 group also contains only 279 validation claims, so small differences between models in that range should not be treated as conclusive.

---

## Provisional October Selection

The provisional November candidate is the top-75-feature `CatBoostRegressor`.

Configuration:

- MAE loss
- depth 8
- learning rate 0.08
- maximum 500 iterations
- seed 42
- 75 predictors

Five-fold CV MAE is **1,153.58 ± 7.19**.

Final validation MAE is **1,136.34**.

The model substantially outperforms both constant predictors on the same validation claims and improves CV performance over the previous HistGradientBoosting leader.

The model is provisional because final unbiased evaluation on the reserved test partition has not yet occurred.

---

## What Model Outputs Mean

The final model produces one numeric prediction per claim.

That value represents the model's estimate of claim `loss` in the same units as the original target.

A validation MAE of X means that, across the validation claims, predictions differ from observed claim losses by X units on average in absolute terms.

This is a retrospective evaluation on the frozen validation sample. It does not establish future-period performance, first-filing usefulness, causal interpretation, or operational reserve accuracy.

---

## Limitations

Several limitations should remain visible when interpreting October results.

September EDA used the full labeled dataset before the October partitions were frozen. The validation set therefore was not completely unseen by the broader project.

Later permutation and SHAP importance calculations also used validation observations. Feature-selection decisions based on the aggregate ranking are therefore validation-informed.

This makes preservation of the protected test partition especially important for final evaluation.

The predictors are anonymous, limiting business interpretation.

The p99 validation segment is small.

A single random split cannot demonstrate temporal stability or performance under future distribution shifts.

Model-specific preprocessing and software environments also differ across experiments, so runtime comparisons are less controlled than MAE comparisons.

---

## October Conclusion

October produced a reproducible modeling pipeline, multiple independently evaluated model families, documented feature experiments, error diagnostics, and a provisional final candidate.

The strongest current candidate is the top-75 CatBoost model.

The protected test partition remains unused and should only be opened under the approved November final-evaluation process.

October model selection should therefore be considered complete once Gate 4 reproduction and full-team approval are recorded.
