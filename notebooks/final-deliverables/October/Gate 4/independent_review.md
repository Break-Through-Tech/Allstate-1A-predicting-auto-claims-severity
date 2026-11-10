# October Independent Review

## Reviewer

**Reviewer:** Ragib Nehal

**Review date:** 2026-11-10

**Reviewed commit:** `164653a2f5a88e07109dda7e08f00bc08ed6c9a4`

## Checks

- [x] Source hash matches approved October artifact bundle.
- [x] Partition-manifest hash matches approved split.
- [x] Train / validation counts are correct.
- [x] No train / validation overlap exists.
- [x] Protected test partition is unused for fitting, selection, prediction, and scoring.
- [x] Mean baseline MAE reproduces.
- [x] Median comparator MAE reproduces.
- [x] Final CatBoost model loads successfully.
- [x] Final feature list contains 75 unique predictors.
- [x] Validation predictions align one-to-one with validation IDs.
- [x] Final validation MAE reproduces in original `loss` units.
- [x] Training-only fitting / preprocessing protections are preserved.
- [x] Final pipeline runs from a clean kernel.
- [x] Recorded model configuration matches the saved artifact.
- [x] No blocking discrepancy remains.

## Findings

The final pipeline was executed in a fresh isolated Python 3.12 kernel using the
recorded package versions. The source, partition-manifest, and serialized-model
SHA-256 hashes matched their receipts. The run loaded the saved model and
reproduced validation MAE `1136.341877632517` across 28,248 unique validation
claims. Reproduced predictions differed from the saved predictions by at most
`3.64e-12`; all predictions were finite and none were negative.

The recorded five-fold result (`1153.5829266911792 ± 7.189688568401656`), the
75-feature list, and tail supports (`25,422 / 2,547 / 279`) matched the saved
artifacts. The model contains 500 trees and records MAE loss, depth 8, learning
rate 0.08, and seed 42. Validation prediction IDs had zero overlap with the
protected-test IDs, and no protected-test predictions or metrics were found.

The feature ranking used validation observations for permutation and SHAP
importance, including validation labels for permutation importance. This is a
documented validation-informed selection limitation, not training or protected-
test leakage. The protected test must remain reserved for the final unbiased
evaluation. The pipeline currently reads the complete source and manifest before
filtering to validation, so documentation should say the test was not *used*
rather than claiming its rows were never read.

The review environment used Python 3.12.12 rather than the receipt's Python
3.12.8; NumPy 1.26.4, pandas 2.2.2, CatBoost 1.2.10, and scikit-learn 1.5.1
matched exactly and the reproduced outputs were unchanged. Historical XGBoost
and SHAP package versions were not captured by the authoring notebook and are
recorded as unavailable rather than inferred. The experiment register now
preserves all 11 extended CatBoost/XGBoost, feature-selection, screening, and
final-promotion records, including unsuccessful runs.

## Decision

- [x] Gate 4 approved
- [ ] Gate 4 blocked

**Notes:** The independent technical review is approved with the documented
validation-exposure and historical-version limitations. Full-team Gate 4
approval remains a separate project decision.
