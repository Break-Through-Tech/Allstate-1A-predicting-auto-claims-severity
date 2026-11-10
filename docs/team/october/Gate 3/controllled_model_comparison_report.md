# Issue #45: Controlled Model Comparison

**Status:** Ready for final review

**Original Author/Owner:** Junaid Pathan  
**Extended Modeling:** Liam Stapley  
**Original Reviewer:** Ragib Nehal  
**Final Extension Reviewer:** Pending

**Original artifact version:** Workflow Run `OCT-JP-MODEL-COMPARISON-001`; review rerun from commit `7c5ba0c`; merged in PR #55 as commit `87c736e`

---

## Scope

Issue #45 compares multiple regression approaches against the required training-mean baseline and training-median comparator under the frozen October evaluation design.

The initial controlled comparison evaluated Ridge Regression and HistGradientBoosting. The work was later extended with independent Linear Regression and Random Forest results, followed by XGBoost and CatBoost experiments, feature-importance analysis, feature selection, and a targeted final CatBoost iteration.

The work covers:

- frozen train and validation partitions;
- five-fold cross-validation inside the training partition;
- model-specific preprocessing;
- baseline comparison;
- model tuning;
- evidence-driven iteration;
- feature-importance analysis;
- feature-selection experiments;
- target-tail diagnostics;
- stability and prediction checks;
- saved validation predictions;
- final model serialization;
- a reproducible final inference pipeline.

The protected test partition remains outside the model-selection process and has not been fitted, predicted, or scored.

---

## Final Artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Original controlled comparison notebook | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/task_45_controlled_model_comparison.ipynb` | Executes the original Ridge/HGB comparison, cross-validation, validation comparison, diagnostics, and iteration. |
| Original model comparison | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/model_comparison.csv` | Records the original baselines, Ridge, and HistGradientBoosting results. |
| Original experiment register | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/experiment_register.csv` | Preserves hypotheses, settings, negative results, interpretations, and next decisions from the original controlled comparison. |
| Original tuning-grid results | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/tuning_grid_results.csv` | Records Ridge and HistGradientBoosting training-fold searches. |
| Original tail diagnostics | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/tail_error_diagnostics.csv` | Reports original validation MAE by claim-loss segment. |
| Original validation predictions | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/validation_predictions.csv` | Provides row-level predictions for independent verification of the original comparison. |
| Liam model experiments | `notebooks/liam-stapley/liam_model_experiments.ipynb` | Evaluates CatBoost, XGBoost, feature importance, feature selection, and final CatBoost iteration. |
| Full-feature comparison | `notebooks/liam-stapley/model_experiment_outputs/full_feature_model_comparison.csv` | Records the initial full-feature CatBoost and XGBoost comparison. |
| Aggregate feature ranking | `notebooks/liam-stapley/model_experiment_outputs/aggregate_feature_ranking.csv` | Combines model importance, permutation importance, and SHAP rankings. |
| Feature-selection CV | `notebooks/liam-stapley/model_experiment_outputs/catboost_feature_selection_cv.csv` | Compares all 130 predictors with top-75, top-50, and top-30 CatBoost subsets. |
| Final CatBoost summary | `notebooks/liam-stapley/model_experiment_outputs/final_catboost_summary.csv` | Records the final selected CatBoost metrics and configuration. |
| Final CatBoost tail diagnostics | `notebooks/liam-stapley/model_experiment_outputs/final_catboost_tail_diagnostics.csv` | Reports final CatBoost MAE across the shared claim-loss ranges. |
| Final validation predictions | `notebooks/liam-stapley/model_experiment_outputs/final_catboost_validation_predictions.csv` | Preserves row-level predictions from the final fitted model. |
| Selected features | `notebooks/liam-stapley/model_experiment_outputs/final_catboost_features.csv` | Records the 75 predictors required by the final model. |
| Final fitted model | `notebooks/liam-stapley/model_experiment_outputs/final_top75_catboost_model.cbm` | Serialized fitted CatBoost model for reuse without retraining. |
| Final model comparison notebook | `notebooks/final-deliverables/October/Gate 3/final_model_comparison.ipynb` | Consolidates the strongest results from all major tested model families. |
| Final comparison outputs | `notebooks/final-deliverables/October/Gate 3/final_model_comparison_results/` | Stores the final overall, tail, and stability comparison tables. |
| Final model pipeline | `notebooks/final-deliverables/October/Gate 3/final_model_pipeline.ipynb` | Loads the frozen inputs, selected features, and saved CatBoost model and reproduces validation predictions without retraining. |
| Final pipeline outputs | `notebooks/final-deliverables/October/Gate 3/final_model_pipeline_results/` | Stores reproduced predictions and the final pipeline receipt. |

---

## Frozen Evaluation Design

- Modeling data version: `OCT-MD-001`
- Split version: `OCT-SPLIT-001`
- Seed: 42
- Training claims: 131,822
- Validation claims: 28,248
- Protected test claims: 28,248
- Training CV folds: 26,365, 26,365, 26,364, 26,364, and 26,364 claims
- Primary metric: mean absolute error in original `loss` units
- Source SHA-256: `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03`
- Partition-manifest SHA-256: `de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b`

The same frozen claim-level partitions were retained across model families.

Model-specific preprocessing was allowed. Ridge used one-hot encoding and standardized continuous predictors. HistGradientBoosting used pooled ordinal categorical representations. XGBoost used its categorical tree support. CatBoost used its native categorical handling.

`id` and `loss` were excluded from model inputs.

---

## Required Baselines

The frozen training-mean constant was the required project baseline. A training-median constant was also retained because it provides a useful comparator for MAE.

| Model | 5-fold CV MAE | CV SD | Validation MAE |
|---|---:|---:|---:|
| Training-mean constant | 1,968.12 | 5.76 | 1,962.92 |
| Training-median constant | 1,810.48 | 6.20 | 1,805.09 |

Every learned model materially improved on both constant comparators.

---

## Initial Controlled Comparison

The original controlled comparison evaluated Ridge Regression and HistGradientBoosting using the frozen design.

| Run | Model | Train 5-fold CV MAE | CV SD | Validation MAE | Validation claims |
|---|---|---:|---:|---:|---:|
| B01 | Training-mean constant | 1,968.12 | 5.76 | 1,962.92 | 28,248 |
| B02 | Training-median constant | 1,810.48 | 6.20 | 1,805.09 | 28,248 |
| E01 | Ridge, `alpha=100` | 1,308.55 | 7.82 | 1,290.43 | 28,248 |
| E02 | HistGradientBoosting, 200 rounds | 1,172.29 | 6.29 | 1,151.17 | 28,248 |
| E02 iteration 1 | HGB with `max_iter=400` | 1,172.36 | 6.41 | 1,151.15 | 28,248 |

Ridge selected `alpha=100`.

The selected HistGradientBoosting configuration used:

- learning rate 0.1;
- maximum 63 leaves;
- minimum 50 samples per leaf;
- maximum 200 boosting rounds.

Increasing only `max_iter` from 200 to 400 changed CV MAE by approximately +0.08 and validation MAE by approximately -0.02. Early stopping ended at 201 rounds.

The difference was substantially below the project's 1% stopping threshold and within normal CV variability. The original controlled comparison therefore correctly retained E02 at 200 rounds.

At this stage, HistGradientBoosting was the strongest tested model.

---

## Independent Model Cross-Check

Jonathan Deng independently evaluated several model families using the same modeling problem.

| Model | CV MAE | Validation MAE |
|---|---:|---:|
| Linear Regression | 1,310.31 | 1,290.13 |
| Ridge | 1,307.37 | 1,288.81 |
| Random Forest | 1,243.54 | 1,223.51 |
| HistGradientBoosting, lr 0.08 | 1,203.84 | 1,187.53 |
| HistGradientBoosting, lr 0.04 | 1,224.38 | 1,209.22 |

The independent experiments supported the broader conclusion that nonlinear boosted-tree approaches outperformed the linear and Random Forest alternatives.

Differences between independent HistGradientBoosting runs reflect different preprocessing and model settings and did not change the overall model-family conclusion.

---

## CatBoost and XGBoost Extension

The comparison was extended with `CatBoostRegressor` and `XGBRegressor`.

Both models were trained as regression models because `loss` is a continuous target.

The initial experiments used all 130 predictors.

| Model | Features | 5-fold CV MAE | CV SD | Validation MAE |
|---|---:|---:|---:|---:|
| XGBRegressor | 130 | 1,183.31 | 6.86 | 1,162.00 |
| CatBoostRegressor | 130 | 1,160.00 | 6.89 | 1,142.33 |

CatBoost outperformed the initial XGBoost model and the previous selected HistGradientBoosting configuration.

The full-feature CatBoost result motivated a feature-importance and feature-selection analysis.

---

## Feature Importance

Three complementary importance measures were calculated:

- CatBoost model-based feature importance;
- permutation importance;
- SHAP importance.

Ranks from the three measures were aggregated to create a single feature-ranking table.

The highest-ranked predictors included `cat80`, `cat101`, `cat79`, `cat100`, `cont2`, `cat114`, `cat103`, `cat57`, `cat81`, and `cont7`.

Because the predictors are anonymous, the importance analysis is interpreted as evidence of predictive usefulness rather than semantic or causal importance.

### Validation-use caveat

The permutation and SHAP importance calculations used a fixed sample from the validation partition.

The resulting feature-ranking and top-75/top-50/top-30 experiments are therefore **validation-informed rather than purely training-derived**.

This is retained as a documented methodological limitation. The protected test partition was not used, so final unbiased evaluation remains available on test.

---

## Feature-Selection Experiments

CatBoost was evaluated using the complete feature set and progressively smaller subsets based on the aggregate ranking.

| Feature set | Feature count | 5-fold CV MAE | CV SD | Mean best iteration |
|---|---:|---:|---:|---:|
| Top 75 | 75 | 1,159.79 | 7.59 | 249.0 |
| All predictors | 130 | 1,160.00 | 6.89 | 249.0 |
| Top 50 | 50 | 1,161.12 | 6.69 | 249.0 |
| Top 30 | 30 | 1,167.15 | 6.86 | 247.8 |

The top-75 subset produced the lowest CV MAE, although its approximately 0.21 MAE advantage over all 130 predictors was much smaller than normal fold-to-fold variation.

On validation, the original top-75 CatBoost model produced MAE of approximately 1,141.14 compared with 1,142.33 for the full-feature CatBoost model.

This approximately 1.19 MAE improvement was only about 0.10%, so it should not be interpreted as a meaningful predictive improvement by itself.

The top-75 configuration was retained primarily because it achieved essentially equivalent or slightly stronger performance while reducing the predictor set from 130 to 75 variables.

More aggressive reduction to 50 or 30 predictors produced worse CV performance.

---

## Final CatBoost Iteration

The feature-selection experiments consistently reached the original maximum of approximately 250 boosting iterations.

A targeted follow-up therefore tested additional boosting capacity instead of running another broad tuning search.

The selected configuration retained:

- `CatBoostRegressor`
- 75 predictors
- MAE loss
- depth 8
- learning rate 0.08
- seed 42
- native categorical handling
- maximum 500 boosting iterations

The five-fold result was:

| Model | Features | CV MAE | CV SD | Mean best iteration |
|---|---:|---:|---:|---:|
| Final CatBoost | 75 | **1,153.58** | **7.19** | **497.2** |

The best iteration across folds remained near the new 500-round limit, with a mean best iteration of 497.2.

This improved CV MAE by approximately 6.21 compared with the initial top-75 model and by approximately 18.71 compared with the selected HGB result.

Final validation MAE: **1,136.34**

The final validation value should be reproduced directly by `final_model_pipeline.ipynb` from the saved `.cbm` artifact before this report is marked complete.

---

## Final Model Comparison

The major model families tested during Issue #45 can be summarized as follows.

| Model | Feature count | CV MAE | CV SD | Validation MAE |
|---|---:|---:|---:|---:|
| Mean constant | 0 | 1,968.12 | 5.76 | 1,962.92 |
| Median constant | 0 | 1,810.48 | 6.20 | 1,805.09 |
| Linear Regression | 130 | 1,310.31 | — | 1,290.13 |
| Ridge | 130 | 1,308.55 | 7.82 | 1,290.43 |
| Random Forest | 130 | 1,243.54 | — | 1,223.51 |
| XGBRegressor | 130 | 1,183.31 | 6.86 | 1,162.00 |
| HistGradientBoosting | 130 | 1,172.29 | 6.29 | 1,151.17 |
| Full-feature CatBoost | 130 | 1,160.00 | 6.89 | 1,142.33 |
| Top-75 CatBoost, 250 iterations | 75 | 1,159.79 | 7.59 | 1,141.14 |
| Final top-75 CatBoost, 500 iterations | 75 | **1,153.58** | **7.19** | **1,136.34** |

The final CatBoost configuration has the strongest five-fold training CV MAE of the tested approaches while using 55 fewer predictors than the original full-feature models.

---

## Tail Diagnostics

The common tail diagnostic uses thresholds derived from the training target distribution:

- p90: 6,401.74
- p99: 14,024.14

Validation support is:

| Segment | Claims |
|---|---:|
| `loss < p90` | 25,422 |
| `p90 <= loss < p99` | 2,547 |
| `loss >= p99` | 279 |

The original selected HGB model produced:

| Segment | HGB MAE |
|---|---:|
| `loss < p90` | 874.2 |
| `p90 <= loss < p99` | 3,006.9 |
| `loss >= p99` | 9,446.5 |

Final CatBoost tail results are stored in `final_catboost_tail_diagnostics.csv` and compared directly with HGB in `final_model_comparison.ipynb`.

Tail MAE remains a diagnostic rather than the primary selection metric.

The p99 group contains only 279 claims, so differences in this segment should be interpreted cautiously.

Large claims remain materially harder to predict than ordinary claims across all tested approaches.

---

## Prediction and Stability Checks

- The same frozen claim-level split was retained across model families.
- The final CatBoost CV SD of 7.19 is comparable with the fold variability observed in the earlier learned models.
- The final CatBoost CV MAE improves on the selected HGB result by approximately 18.71.
- No test rows were used during model fitting or scoring.
- The final model operates directly in original `loss` units.
- MAE loss limits the influence of large residuals relative to squared-error objectives without removing severe claims from training.
- The final pipeline applies no unnecessary scaling, one-hot encoding, or target transformation.
- CatBoost receives the selected categorical predictors using its native categorical handling.
- The final `.cbm` artifact allows predictions to be reproduced without repeating expensive cross-validation.

---

## Final Pipeline

The selected model is preserved as `final_top75_catboost_model.cbm`.

The final inference pipeline is intentionally minimal:

`Frozen source and split`  
→ `75 selected predictors`  
→ `categorical string preparation`  
→ `saved CatBoostRegressor`  
→ `prediction in original loss units`

No `StandardScaler`, output transformer, one-hot encoder, or target transformation is required for the selected CatBoost model.

The pipeline verifies the frozen source and partition hashes, loads the saved feature list and model, reproduces validation predictions, checks prediction validity, calculates MAE, and writes a compact run receipt.

The pipeline does not retrain or retune the model.

---

## Anomalies and Limitations

- September exploration used the full labeled dataset, so the October validation partition was not wholly unseen by the broader project.
- The later feature-ranking analysis used validation observations for permutation and SHAP importance. Feature-selection experiments derived from this ranking are therefore validation-informed.
- Because validation informed some later modeling decisions, the protected test partition is especially important for the final unbiased performance estimate.
- A single random split cannot establish temporal or population stability.
- The p99 diagnostic contains only 279 validation claims and therefore has substantially greater sampling uncertainty than the ordinary-claim segment.
- Predictors are anonymous, preventing semantic interpretation of feature importance.
- CatBoost, XGBoost, and the earlier sklearn experiments use model-specific preprocessing and were run under different software environments. Claim-level splits and MAE remain comparable, but runtime should not be treated as a perfectly controlled benchmark.
- The original independent review covered the Ridge/HGB controlled comparison. The later CatBoost extension changes the final recommendation and therefore requires a final independent verification before Issue #45 is closed.

---

## Original Independent Verification

The original controlled comparison was independently reviewed by Ragib Nehal on 2026-11-03.

The reviewer reran the controlled comparison and confirmed:

- all analysis cells completed without errors;
- the five original validation MAEs were independently reproduced from saved predictions;
- 28,248 unique validation rows were present;
- partition counts matched the frozen design;
- the test partition was excluded;
- all original experiment-register entries were present;
- tail support counts matched;
- the original result bundle was complete.

The original review therefore remains valid for the Ridge/HGB portion of Issue #45.

---

## Final Extension Verification

Before closing Issue #45, an independent reviewer should confirm:

- [ ] Final CatBoost `.cbm` model loads successfully.
- [ ] Final feature list contains 75 unique predictors.
- [ ] Final pipeline contains exactly 28,248 validation claims.
- [ ] Saved final validation predictions reproduce the reported validation MAE.
- [ ] Final five-fold CV result is 1,153.58 with CV SD 7.19.
- [ ] Final comparison tables match the saved experiment artifacts.
- [ ] Tail-support counts remain 25,422 / 2,547 / 279.
- [ ] No test predictions or test metrics were produced.
- [ ] Final pipeline executes from a fresh kernel.

**Final extension reviewed by:** Pending  
**Review date:** Pending  
**Review notes:** Pending

---

## Verification Checklist

- [x] Frozen source and split used.
- [x] Required mean baseline evaluated.
- [x] Median comparator evaluated.
- [x] Multiple distinct learned model families evaluated.
- [x] Five-fold training CV used for major selected models.
- [x] Validation MAE reported in original loss units.
- [x] Evidence-driven model iteration completed.
- [x] Negative and unsuccessful experiments retained.
- [x] Tail diagnostics completed.
- [x] Feature-importance analysis completed.
- [x] Feature-selection experiments completed.
- [x] Final fitted model serialized.
- [x] Final selected feature list saved.
- [x] Final model comparison produced.
- [x] Protected test partition remains unused.
- [ ] Final CatBoost pipeline reproduced from a fresh kernel.
- [ ] Final CatBoost extension independently verified.
- [ ] Extended CatBoost/XGBoost experiments added to the experiment register.

---

## Final Recommendation

The final recommended model is the **top-75-feature `CatBoostRegressor` using MAE loss, depth 8, learning rate 0.08, and a maximum of 500 boosting iterations**.

The model achieved the strongest five-fold training CV MAE among the tested approaches at **1,153.58 ± 7.19**, improving on the previous selected HistGradientBoosting result of 1,172.29 ± 6.29.

The final model also reduces the predictor set from 130 to 75 features.

The reduction should be viewed primarily as a simplification rather than a major predictive improvement because the original top-75 versus full-feature CatBoost difference was small relative to fold-to-fold variation.

The final validation result, tail diagnostics, stability evidence, saved model artifact, and reproducible final pipeline provide the supporting evidence for the recommendation.

The protected test partition remains unused and should provide the final unbiased evaluation after all model-selection decisions are frozen.

---

## Completion

The original controlled model comparison and independent review are complete.

Subsequent XGBoost, CatBoost, feature-importance, feature-selection, and targeted tuning experiments extended the original Issue #45 evidence and changed the recommended final model from HistGradientBoosting to CatBoost.

The modeling and model-selection work is complete.

Issue #45 should be closed after:

1. the saved CatBoost model is reproduced through the final pipeline;
2. the extended experiment register is updated; and
3. the final CatBoost extension receives independent verification.

After those checks, the final recommended Issue #45 model is the top-75-feature CatBoost configuration described above, and the protected test partition remains reserved for final evaluation.
