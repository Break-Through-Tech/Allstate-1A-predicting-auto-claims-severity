# Controlled Model Comparison Summary (issue #45)

Notebook: `task_45_controlled_model_comparison.ipynb`. Raw outputs: `model_comparison_results/`.

## Design (fixed for every row)

- Modeling data `OCT-MD-001`, split `OCT-SPLIT-001` (train 131,822 / validation 28,248; test rows dropped at load and not used), seed 42.
- Tuning: the 5 recorded `cv_fold` folds inside train, pipeline refit per fold. Validation is a limited comparison check.
- Metric: MAE in original `loss` units, one shared function for baselines and models.
- Preprocessing follows `docs/team/october/Gate 1/preprocessing_plan.md` (rare-level pooling at 132 train claims, categorical mask for trees).
- Workflow run `OCT-JP-MODEL-COMPARISON-001`; code commit `3f51455`, clean tree; Python 3.10.0, scikit-learn 1.7.2, pandas 2.3.3, numpy 2.2.6.

## Comparison (original loss units)

| Run | Model | Train 5-fold CV MAE (+/- SD) | Validation MAE | Validation claims | vs mean baseline | vs median comparator | Complexity | Runtime |
|---|---|---:|---:|---:|---:|---:|---|---:|
| B01 | Training mean constant | 1,968.12 (5.76) | 1,962.92 | 28,248 | 0.00% | -8.74% | 1 constant | 0 s |
| B02 | Training median constant | 1,810.48 (6.20) | 1,805.09 | 28,248 | +8.04% | 0.00% | 1 constant | 0 s |
| E01 | Ridge, alpha 100 | 1,308.55 (7.82) | 1,290.43 | 28,248 | +34.26% | +28.51% | 670 inputs + intercept | 169 s |
| E02 | HistGradientBoosting, lr 0.1, 63 leaves, min leaf 50 | 1,171.25 (7.06) | 1,149.93 | 28,248 | +41.42% | +36.29% | 200 rounds, up to 63 leaves | 315 s |
| E02-iter1 | Same, `max_iter` 200 to 400 | 1,170.89 (7.16) | 1,149.97 | 28,248 | +41.42% | +36.29% | 228 rounds, up to 63 leaves | 339 s |

Positive percentages mean lower validation MAE than the baseline.

## Iteration (one changed variable)

The selected boosted model used all 200 allowed rounds. Raising only `max_iter` to 400 moved CV MAE by -0.36 (fold SD 7.06) and validation MAE by +0.04. Early stopping ended at 228 rounds. The change is well inside fold-to-fold noise and fails the 1% stopping rule, so the result is a negative one and iteration stops. The selected model is E02 (200 rounds); E02-iter1 is equivalent.

## Diagnostics (not a selection metric)

Validation MAE by segment, using training p90 6,401.74 and p99 14,024.14:

| Segment | Support | Median constant | Ridge | HGB |
|---|---:|---:|---:|---:|
| loss < p90 | 25,422 | 1,168.5 | 1,050.7 | 873.5 |
| p90 to p99 | 2,547 | 6,593.7 | 2,770.1 | 3,008.2 |
| loss >= p99 | 279 | 16,093.8 | 9,629.5 | 9,377.3 |

- HGB is best overall and on ordinary claims, but Ridge is better on the p90 to p99 band (2,770 vs 3,008). The p99 segment has only 279 claims, so the Ridge vs HGB difference there (about 250) should not be read as settled.
- Large claims remain poorly predicted by every model: p99 MAE is still about 9,400 to 9,600.

## Checks

- Overfitting: validation MAE is 18 to 21 below CV MAE for the learned models (2.3 to 3.0 fold SDs). The gap is in the optimistic-for-validation direction, so there is no sign of overfitting; likely explanations are fold size and sampling, not tuning on validation.
- Stability: fold SDs are 6 to 8. HGB beats Ridge by 140 validation MAE (about 18 fold SDs), a clear difference. Differences among HGB grid settings (1,171 to 1,178) are close to fold SD and are weak evidence.
- Grid edge: the best HGB leaf count (63) was the largest tried, so a larger value was not tested.
- Failed predictions: none non-finite. Ridge makes 270 negative loss predictions on validation (not clipped); HGB makes none.
- Category handling: 9 validation cells hold a level unseen in train (cat105 1, cat110 1, cat113 1, cat116 6). Ridge sends them to the rare bucket; HGB treats them as missing.

## Cross-check against Jonathan Deng's independent run

Baselines match to the cent. Ridge matches within 1.6 (1,290.43 vs 1,288.81). Boosted trees differ: 1,149.93 here vs 1,187.53 (his lr 0.08) and 1,209.22 (his lr 0.04). Differences in preprocessing (rare-level pooling and the categorical mask here) are a plausible but untested explanation. His lowering of the learning rate also did not help.

## Caveats

- scikit-learn 1.7.2 was used locally; `preprocessing_plan.md` pins 1.6.1. Results may shift slightly under 1.6.1.
- September EDA used the full labeled file, so validation is not wholly unseen evidence.
- One split cannot show stability over time. Test was not used.
- Independent verification (issue subtask) is still open: a teammate should recompute validation MAE from `model_comparison_results/validation_predictions.csv`.
