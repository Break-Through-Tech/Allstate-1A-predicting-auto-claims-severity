# Issue #45: Controlled model comparison

**Status:** Complete

**Author/Owner:** Junaid Pathan

**Reviewer:** Ragib Nehal

**Artifact version:** Workflow Run `OCT-JP-MODEL-COMPARISON-001`; review rerun from commit `7c5ba0c`; merged in PR #55 as commit `87c736e`

## Scope

Issue #45 compares two approved and distinct learned approaches against the required training-mean baseline and training-median comparator under the frozen October evaluation design. The work covers training-only model selection, a limited validation comparison, one evidence-driven iteration, target-tail diagnostics, stability and prediction checks, an experiment register, and advisor-ready model explanations. The protected test partition is outside this work and was not fitted, summarized, predicted, or scored.

## Final artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Controlled comparison notebook | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/task_45_controlled_model_comparison.ipynb` | Executes the frozen split checks, preprocessing, cross-validation, validation comparison, diagnostics, iteration, and exports. |
| Model comparison | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/model_comparison.csv` | Records CV and validation MAE, baseline improvements, claim counts, complexity, and runtime for the selected comparisons. |
| Experiment register | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/experiment_register.csv` | Preserves hypotheses, settings, negative results, interpretations, and next decisions for all 11 registered runs. |
| Tuning-grid results | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/tuning_grid_results.csv` | Records the complete Ridge and HistGradientBoosting training-fold searches, including unselected settings. |
| Tail diagnostics | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/tail_error_diagnostics.csv` | Reports validation MAE and support counts below training p90, from p90 to p99, at or above p99, and overall. |
| Validation predictions | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/validation_predictions.csv` | Supplies row-level validation targets and predictions for independent metric verification. |
| Pooled vocabulary | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/pooled_vocabulary.csv` | Records the training-derived categorical vocabulary and rare-level pooling evidence. |
| Teammate cross-check | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/teammate_crosscheck.csv` | Compares the results with Jonathan Deng's independent model run. |
| Run metadata | `notebooks/final-deliverables/October/Gste 3/controlled_model_comparison/model_comparison_results/run_metadata.json` | Records hashes, split and modeling versions, seed, partitions, software versions, runtime, validation consultations, and test policy. |

## Method

- Modeling data version `OCT-MD-001`, split version `OCT-SPLIT-001`, Workflow Run `OCT-JP-MODEL-COMPARISON-001`, and seed 42 were used throughout.
- The source and frozen partition manifest were checked against SHA-256 hashes before modeling.
- The working data contained 131,822 training claims and 28,248 validation claims. The five recorded `cv_fold` assignments contained 26,365, 26,365, 26,364, 26,364, and 26,364 claims.
- All settings were selected using the five training folds. Each preprocessing pipeline was refitted inside each fold. Validation was consulted once for each selected comparison and was not used for fitting.
- Both learned approaches used the same 130 predictors: `cat1` through `cat116` and `cont1` through `cont14`. `id` and `loss` were excluded from model inputs.
- Rare categorical levels were pooled using the training-derived minimum frequency of 132. Ridge used pooled one-hot encoding and standardized continuous fields. HistGradientBoosting used pooled ordinal codes, a categorical mask for the 116 categorical fields, and missing-value handling for unseen levels.
- The shared primary metric was mean absolute error in original `loss` units. Target-tail measurements were diagnostics only and did not replace the selection metric.
- Ridge searched `alpha` values 1, 10, 100, and 1,000. HistGradientBoosting compared four approved learning-rate, leaf-count, and minimum-leaf-size settings.
- The evidence-driven iteration changed only `max_iter`, from 200 to 400, after the first selected boosted model used all 200 available rounds.
- The review rerun used Python 3.14.2, scikit-learn 1.9.1, pandas 3.0.5, and NumPy 2.5.1. These installed dependencies successfully executed the full comparison, and their versions are preserved in the metadata.

## Results

| Run | Model | Train 5-fold CV MAE | CV SD | Validation MAE | Validation claims | Better than mean | Better than median | Complexity | Runtime |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| B01 | Training-mean constant | 1,968.12 | 5.76 | 1,962.92 | 28,248 | 0.00% | -8.74% | One constant | 0.00 s |
| B02 | Training-median constant | 1,810.48 | 6.20 | 1,805.09 | 28,248 | 8.04% | 0.00% | One constant | 0.00 s |
| E01 | Ridge, `alpha=100` | 1,308.55 | 7.82 | 1,290.43 | 28,248 | 34.26% | 28.51% | 670 inputs plus intercept | 24.12 s |
| E02 | HistGradientBoosting, 200 rounds | 1,172.29 | 6.29 | 1,151.17 | 28,248 | 41.35% | 36.23% | Up to 63 leaves per round | 106.28 s |
| E02 iteration 1 | Same model, `max_iter=400` | 1,172.36 | 6.41 | 1,151.15 | 28,248 | 41.36% | 36.23% | Early stopping at 201 rounds | 74.57 s |

Ridge selected `alpha=100`, which was not a grid edge. The selected boosted configuration used learning rate 0.1, 63 maximum leaves, and 50 minimum samples per leaf. Its validation MAE was 139.26 lower than Ridge, approximately 17.8 CV standard deviations, providing clear evidence for the boosted approach.

Increasing `max_iter` from 200 to 400 changed CV MAE by +0.08 and validation MAE by -0.02. The change was within one CV standard deviation and the validation gain was approximately 0.002%, below the 1% stopping rule. The iteration therefore supports stopping, not another adjustment. E02 at 200 rounds remains the CV-selected model.

The target-tail diagnostic used training p90 of 6,401.74 and p99 of 14,024.14. There were 25,422 validation claims below p90, 2,547 from p90 to p99, and 279 at or above p99. HistGradientBoosting had lower MAE than Ridge overall and below p90, while Ridge was better in the p90-to-p99 band: 2,770.1 versus 3,006.9. At or above p99, both remained weak, with MAE of 9,629.5 for Ridge and 9,446.5 for HistGradientBoosting. These segment results remain diagnostics rather than selection criteria.

The learned models' validation MAE was 18.12 to 21.22 below CV MAE. This is not the usual overfitting direction, although the approximately 3.3-CV-SD gap for the boosted models warrants caution when generalizing from one split. No model produced non-finite predictions. Ridge produced 270 negative validation predictions, which were retained and documented; both boosted runs produced none.

Nine validation cells contained a category level unseen during training: one each in `cat105`, `cat110`, and `cat113`, and six in `cat116`. Ridge routed unseen levels through the rare or all-zero one-hot behavior; HistGradientBoosting treated them as missing. The independent teammate cross-check matched both baselines exactly and Ridge within 1.62 MAE. Boosted-model differences were attributable to differing settings and preprocessing and do not reverse the selected approach.

## Anomalies and limitations

- The review environment contained newer libraries than the Gate 1 reference environment: scikit-learn 1.9.1 rather than 1.6.1, pandas 3.0.5 rather than 2.3.3, and NumPy 2.5.1 rather than 2.0.2. The run is a successful environment-variant replication, not an exact version-matched reproduction. Versions are recorded, source and manifest hashes passed, and the principal model-selection conclusion remained unchanged.
- The review run metadata records `git_dirty: true` because the notebook, generated evidence, dependency setup, and this review were being updated in the working tree. The reviewed artifacts were subsequently merged in PR #55 as commit `87c736e`, which is the durable artifact version.
- The selected HGB leaf count of 63 was the largest value tested, so the grid does not establish whether a larger value would improve CV MAE.
- The p99 diagnostic contains only 279 validation claims. Differences between models in this segment are not strong enough to support a separate selection decision.
- September exploration used the full labeled dataset, so the October validation partition is not wholly unseen by the broader project.
- A single random split cannot establish temporal or population stability. The protected test partition remains unused and reserved for a later gate.

## Verification

- [x] Final notebook runs from a fresh kernel.
- [x] Required outputs were generated and checked.
- [x] Issue requirements have been completed.
- [x] Calculated outputs match the recorded source and configuration.
- [x] Independent review completed, if required.

**Reviewed by:** Ragib Nehal

**Review date:** 2026-11-03

**Review notes:** Approved. The reviewer reran the notebook with the required dependencies available and confirmed that all analysis cells completed without errors. Independent recomputation from `validation_predictions.csv` reproduced all five recorded validation MAEs to numerical precision. The review also confirmed 28,248 unique validation rows, the recorded partition counts and test exclusion, all 11 experiment-register entries, tail support counts, and the complete eight-file result bundle. The newer software environment and dirty working-tree state are documented limitations rather than unreported discrepancies.

## Completion

Issue #45's controlled model comparison deliverables and independent review are complete. The selected result is HistGradientBoosting E02 at 200 maximum rounds; the single-variable 400-round iteration did not produce a reliable improvement and meets the stopping rule. The protected final test partition remains unused. The reviewed notebook, result bundle, and report were merged in PR #55 as commit `87c736e`; issue #45 remains open.
