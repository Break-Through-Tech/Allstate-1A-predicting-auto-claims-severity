# Controlled Model Comparison Summary (Issue #45)

Initial controlled comparison notebook: `task_45_controlled_model_comparison.ipynb`  
Initial raw outputs: `model_comparison_results/`  
Additional experiments: `notebooks/liam-stapley/liam_model_experiments.ipynb`  
Final comparison: `final_model_comparison.ipynb`

## Design

- Modeling data: `OCT-MD-001`
- Frozen split: `OCT-SPLIT-001`
- Train: 131,822 claims
- Validation: 28,248 claims
- Test: 28,248 claims, still protected and unused for model selection
- Seed: 42
- Cross-validation: five recorded `cv_fold` folds inside the training partition
- Primary metric: MAE in original `loss` units
- Model-specific preprocessing, feature selection, and tuning were allowed while keeping the same claim-level split across models.
- Validation was used as a limited comparison set after training-fold experimentation.

The initial controlled comparison used the approved Ridge and HistGradientBoosting preprocessing. Later CatBoost and XGBoost experiments used model-specific categorical handling appropriate for those model families.

## Initial Controlled Comparison

| Run | Model | Train 5-fold CV MAE (+/- SD) | Validation MAE | Validation claims | vs mean baseline | vs median comparator |
|---|---|---:|---:|---:|---:|---:|
| B01 | Training mean constant | 1,968.12 (5.76) | 1,962.92 | 28,248 | 0.00% | -8.74% |
| B02 | Training median constant | 1,810.48 (6.20) | 1,805.09 | 28,248 | +8.04% | 0.00% |
| E01 | Ridge, alpha 100 | 1,308.55 (7.82) | 1,290.43 | 28,248 | +34.26% | +28.51% |
| E02 | HistGradientBoosting, lr 0.1, 63 leaves, min leaf 50 | 1,172.29 (6.29) | 1,151.17 | 28,248 | +41.35% | +36.23% |
| E02-iter1 | Same model, `max_iter` 400 | 1,172.36 (6.41) | 1,151.15 | 28,248 | +41.36% | +36.23% |

The 400-round HGB iteration produced only a 0.02 MAE validation improvement and slightly worse CV MAE. This was within fold-to-fold variation, so the 200-round HGB remained the selected result from the initial controlled comparison.

## Additional Model Experiments

The controlled comparison was extended with two additional regression approaches:

- `CatBoostRegressor`
- `XGBRegressor`

Both initially used all 130 predictors and were evaluated using the same five frozen training folds and validation partition.

The full-feature CatBoost model outperformed the initial XGBoost model and the previous HGB leader. This motivated additional CatBoost feature-selection experiments.

## Feature Importance and Selection

Feature importance was evaluated using:

- model-based importance;
- permutation importance;
- SHAP importance.

The three measures were converted to ranks and aggregated into one feature ranking.

CatBoost was then evaluated using the top 75, 50, and 30 ranked predictors.

| Feature set | Features | 5-fold CV MAE | CV SD |
|---|---:|---:|---:|
| Top 75 | 75 | 1,159.79 | 7.59 |
| All features | 130 | 1,160.00 | 6.89 |
| Top 50 | 50 | 1,161.12 | 6.69 |
| Top 30 | 30 | 1,167.15 | 6.86 |

The top-75 subset slightly improved CV MAE while reducing the model from 130 to 75 predictors. More aggressive reduction to 50 or 30 predictors worsened performance.

The top-75 feature set was therefore retained for final CatBoost tuning.

## Final CatBoost Iteration

The strongest top-75 CatBoost configuration was given additional boosting capacity, increasing the maximum number of iterations from 250 to 500 while retaining:

- MAE loss;
- depth 8;
- learning rate 0.08;
- seed 42;
- native categorical handling.

The five-fold result was:

| Model | Features | CV MAE | CV SD | Mean best iteration |
|---|---:|---:|---:|---:|
| CatBoostRegressor, top 75, 500 iterations | 75 | **1,153.58** | **7.19** | **497.2** |

The selected model used almost the entire 500-iteration allowance across folds, with best iterations between 494 and 499.

Final validation MAE: **[INSERT FINAL 500-ITERATION VALIDATION MAE]**

## Model Progression

The main modeling progression was:

`Constant baselines`  
→ `Linear / Ridge`  
→ `Random Forest / HistGradientBoosting`  
→ `XGBoost / CatBoost`  
→ `Feature importance ranking`  
→ `Top-75 CatBoost`  
→ `500-iteration top-75 CatBoost`

HistGradientBoosting was the strongest model after the initial controlled comparison at 1,151.17 validation MAE. CatBoost later provided stronger cross-validation evidence and a smaller final feature set, leading to the updated final recommendation.

## Tail Diagnostics

The original HGB comparison used training thresholds:

- p90 = 6,401.74
- p99 = 14,024.14

with validation support:

| Segment | Support |
|---|---:|
| `loss < p90` | 25,422 |
| `p90 to p99` | 2,547 |
| `loss >= p99` | 279 |

The original selected HGB produced:

| Segment | HGB MAE |
|---|---:|
| `loss < p90` | 874.2 |
| `p90 to p99` | 3,006.9 |
| `loss >= p99` | 9,446.5 |

The final CatBoost model is evaluated using the same thresholds and support counts in `final_catboost_tail_diagnostics.csv`.

Tail performance remains a diagnostic rather than a replacement selection metric. The p99 segment contains only 279 validation claims, so small differences in that range should be interpreted cautiously.

## Stability and Prediction Checks

- All models use the same frozen claim-level split.
- CatBoost's final CV SD of 7.19 is similar to the variability observed in the earlier learned models.
- The final CatBoost CV result improves on the selected HGB CV MAE of 1,172.29 by approximately 18.71 MAE.
- The top-75 feature-selection result was reproduced across all five frozen training folds.
- The final model uses MAE loss, which limits the influence of very large residuals relative to squared-error training while retaining high-loss claims in the dataset.
- No test rows were used for model training, feature selection, tuning, prediction, or scoring.

## Cross-Check Against Jonathan Deng's Experiments

Jonathan independently evaluated Linear Regression, Ridge, Random Forest, and HistGradientBoosting.

His results included:

| Model | CV MAE | Validation MAE |
|---|---:|---:|
| Linear Regression | 1,310.31 | 1,290.13 |
| Ridge | 1,307.37 | 1,288.81 |
| Random Forest | 1,243.54 | 1,223.51 |
| HGB, lr 0.08 | 1,203.84 | 1,187.53 |
| HGB, lr 0.04 | 1,224.38 | 1,209.22 |

These experiments independently supported the broader conclusion that nonlinear boosted-tree approaches outperform the linear and random-forest alternatives on this dataset.

## Final Recommendation

The final recommended model is the **top-75-feature CatBoostRegressor with MAE loss, depth 8, learning rate 0.08, and 500 boosting iterations**.

The recommendation is based primarily on MAE in original loss units, supported by five-fold CV stability, high-loss diagnostics, and model simplicity.

The selected CatBoost configuration improves substantially over the required constant baselines and improves CV performance over the previous HistGradientBoosting leader while using 55 fewer predictors.

The protected test partition remains unused and should be reserved for final evaluation after model selection is complete.

## Caveats

- September EDA used the full labeled dataset, so later modeling hypotheses were not developed without any prior exposure to validation claims.
- A single frozen split cannot establish temporal or population stability.
- High-loss tail estimates are noisy because only 279 validation claims fall at or above the training p99 threshold.
- CatBoost, XGBoost, and earlier sklearn experiments were run under different model-specific preprocessing and software environments. Their claim-level split and evaluation metric remain comparable, but runtime comparisons should be interpreted cautiously.
- Feature importance identifies predictive usefulness but cannot provide semantic interpretation because the predictors are anonymous.