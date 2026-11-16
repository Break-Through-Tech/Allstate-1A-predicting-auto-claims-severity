# Issue #57: October Handoff and November Plan

**Status:** Ready for review

**Owner(s):** Ragib Nehal and Liam Stapley

**Reviewer:** Pending

**Artifact version:** Working tree based on commit
`4c50ff47c76da18882b113bf3e00a8d311e2e633`; final commit pending

## Scope

Issue #57 transfers the October modeling work into the November evaluation and
presentation milestone. The handoff confirms the frozen top-75 CatBoost
candidate, its required artifacts and preprocessing contract, and the unused
status of the protected test partition. It also freezes the final-evaluation
procedure and assigns initial presentation sections before the team opens the
test partition.

The issue does not include protected-test scoring. Issue #58 will execute the
frozen plan after November Gate 1 review and approval.

## Final artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Issue #57 handoff report | `docs/team/november/Gate 1/october_handoff_and_november_plan_report.md` | Maps each issue requirement, subtask, and deliverable to evidence and records remaining approval work. |
| Frozen final-evaluation plan | `notebooks/final-deliverables/November/Gate 1/frozen_final_evaluation_plan.md` | Freezes the model, inputs, metric, baselines, diagnostics, execution procedure, outputs, and defect policy before test scoring. |
| Presentation outline | `notebooks/final-deliverables/November/Gate 1/presentation_outline.md` | Defines the presentation story, initial slide scope, and section ownership. |
| October decision record | `notebooks/final-deliverables/October/Gate 4/decision_record.md` | Records the provisional candidate and the October model-selection decision. |
| October-to-November handoff | `notebooks/final-deliverables/October/Gate 4/november_handoff.md` | Carries forward October artifacts, limitations, deferred work, priorities, and Challenge Advisor questions. |
| October independent review | `notebooks/final-deliverables/October/Gate 4/independent_review.md` | Records the reproduced validation result, artifact checks, protected-test status, and technical approval. |
| Reproduction instructions | `notebooks/final-deliverables/October/Gate 4/reproducing_results.md` | Documents the reviewed process for reproducing the frozen candidate's validation evidence. |
| Saved CatBoost model | `notebooks/liam-stapley/model_experiment_outputs/final_top75_catboost_model.cbm` | Stores the fitted model that November will evaluate without retraining. |
| Final feature list | `notebooks/liam-stapley/model_experiment_outputs/final_catboost_features.csv` | Stores the ordered set of 75 selected predictors. |
| Frozen split manifest | `notebooks/final-deliverables/October/Gate 1/partition_manifest.csv` | Assigns each claim to the fixed train, validation, or protected-test partition. |
| Reference inference pipeline | `notebooks/final-deliverables/October/Gate 3/final_model_pipeline.ipynb` | Supplies the reviewed model-loading, feature-selection, CatBoost preparation, prediction, and MAE code. |
| Preprocessing contract | `notebooks/final-deliverables/October/Gate 1/preprocessing_plan.md` | Documents leakage controls and model-specific preprocessing requirements. |

## Method

The handoff uses the approved October Gate 4 evidence rather than rerunning
model selection. The frozen evaluation plan identifies each required input by
repository path and SHA-256 hash. It requires the Gate 2 runner to stop if a
hash, partition count, feature count, or ID-alignment check fails.

The selected candidate is the saved `CatBoostRegressor` with 75 predictors,
MAE loss, depth 8, learning rate 0.08, no more than 500 iterations, and seed 42.
The inference code converts the selected categorical values to strings and
passes continuous values directly to the saved model. It does not standardize,
one-hot encode, transform the target, refit the model, or recalculate feature
rankings.

November will measure MAE in original `loss` units. The final comparison will
apply the frozen training-mean constant of `3038.8402548133095` and the frozen
training-median constant of `2115.39` to the same 28,248 test claims. The plan
also fixes the segment thresholds, integrity checks, extreme-error table, and
October comparison rules before scoring begins.

## Issue requirements and subtasks

| Requirement or subtask | Status | Evidence |
|---|---|---|
| Confirm October Gate 4 approval and freeze the provisional CatBoost candidate. | Ready for team approval | The independent technical review approved Gate 4 and found no blocking defect. The decision record identifies the top-75 CatBoost candidate. Full-team handoff approval remains pending. |
| Confirm the saved model, 75-feature list, split manifest, evaluation code, and preprocessing requirements. | Confirmed | The frozen plan records the paths, hashes, feature count, model configuration, and inference contract. The final pipeline supplies reviewed reference evaluation code. |
| Verify that the protected test partition was not used during model selection. | Confirmed | The October independent review found no test fitting, selection, prediction, or scoring. It also found no saved protected-test metric. The source and manifest were read before validation filtering, so this report describes the test as unused rather than unread. |
| Carry forward limitations, anomalies, deferred experiments, and Challenge Advisor questions. | Confirmed | The carry-forward register below consolidates the October handoff items and points to their source. |
| Freeze the final-evaluation procedure, metric, baselines, and diagnostics before opening the test partition. | Complete; approval pending | The frozen final-evaluation plan fixes MAE, both constants, segment thresholds, checks, diagnostics, outputs, and review requirements. It contains no protected-test result. |
| Prohibit tuning or feature selection after viewing final test results unless reviewers confirm a defect. | Confirmed | The final-evaluation plan defines a narrow defect policy and prohibits hyperparameter changes, feature changes, retraining, and result-driven replacement. |
| Finalize the presentation outline and assign initial sections. | Complete | The outline assigns each section to one or more initial owners and reserves placeholders for independently verified Gate 2 results. |

## Results

The handoff freezes the top-75 CatBoost candidate with the following October
reference results:

| Result | MAE |
|---|---:|
| Five-fold training CV mean | 1,153.5829266911792 |
| Five-fold training CV standard deviation | 7.189688568401656 |
| October validation | 1,136.341877632517 |
| Training-mean constant on validation | 1,962.918654312225 |
| Training-median constant on validation | 1,805.0863526621356 |

The frozen split contains 131,822 training claims, 28,248 validation claims,
and 28,248 protected-test claims. The October independent review reproduced
the validation MAE across all validation claims, confirmed 75 unique selected
predictors, matched the saved model configuration, and found no protected-test
predictions or scores.

The presentation outline covers the problem, data, experimental design, model
comparison, feature experiments, final evaluation, error analysis, final
pipeline, conclusions, and Q&A. It assigns initial sections to Liam Stapley,
Mia Chavez, Ragib Nehal, Jonathan Deng, Junaid Pathan, and Ella Zou. The final
evaluation slides remain placeholders until Issue #58 produces independently
verified test results.

### Deliverable status

| Issue #57 deliverable | Status | Evidence |
|---|---|---|
| Approved October to November handoff | Ready for review | This report and the October Gate 4 evidence assemble the handoff; formal team approval remains pending. |
| Frozen final-evaluation plan | Delivered; approval pending | `notebooks/final-deliverables/November/Gate 1/frozen_final_evaluation_plan.md` |
| Confirmed final model, configuration, and required artifacts | Delivered | The artifact table and frozen plan record the model, feature list, split, pipeline, preprocessing, hashes, and configuration. |
| Presentation outline with initial ownership | Delivered | `notebooks/final-deliverables/November/Gate 1/presentation_outline.md` |

## Carry-forward register

### Limitations and anomalies

- September EDA used the full labeled dataset before the October split was
  frozen. October validation results do not represent evidence untouched by
  the broader project.
- CatBoost permutation and SHAP rankings used validation observations, so the
  selected feature set is validation-informed.
- The October reference pipeline read the complete source and split manifest
  before filtering to validation. Reviewers confirmed that it did not use test
  rows for fitting, selection, prediction, or scoring.
- The p99 validation segment contains 279 claims. Small differences in that
  segment carry substantial sampling uncertainty.
- Anonymous predictors support statistical importance statements but not
  business labels or causal claims.
- The single random split does not measure future-period or temporal stability.
- Historical XGBoost and SHAP package versions were not captured. The October
  review left them recorded as unavailable instead of inferring versions.
- Model families used different software environments and appropriate
  model-specific preprocessing. MAE remains comparable on fixed claims, but
  runtime does not form a controlled benchmark.
- The October handoff's team-review table contains an outdated roster. The
  latest November planning document confirms the active presentation team as
  Liam Stapley, Mia Chavez, Ragib Nehal, Jonathan Deng, Junaid Pathan, and Ella
  Zou. The November presentation outline uses this updated roster.

### Deferred experiments

Issue #46 tested removing 31 dominant categorical predictors from the retained
HGB configuration. The reduced 99-feature model did not improve CV or
validation MAE, so the HGB comparison retained all 130 predictors. Optional
hypotheses O2, O3, and O4 remain deferred. They must not delay final evaluation
or presentation work, and the team must not use final test performance to
decide whether to revive them.

### Challenge Advisor questions

1. When should the team open the protected test partition, and should the team
   use it only once after approving the frozen October configuration?
2. Should the final presentation retain high-loss segment performance as a
   diagnostic beside overall MAE, or emphasize another secondary metric?
3. How much feature-importance discussion is useful when the predictors remain
   anonymous?
4. Should the team revisit deferred Issue #46 hypotheses only if time remains
   after final evaluation and presentation work?
5. How should the presentation relate retrospective validation performance to
   possible first-filing use without overstating operational evidence?

## Anomalies and limitations

No blocking artifact, split, leakage, metric, or reproducibility defect remains
from the October technical review. The limitations in the carry-forward
register remain active for final evaluation and presentation claims.

Formal team approval remains outstanding. The report cannot convert the
independent technical approval into full-team approval, and Issue #57 cannot
close until the team records that decision.

The report records October CV and validation evidence only. It contains no
protected-test score, and no protected-test scoring was performed while
preparing the November Gate 1 artifacts.

## Verification

- [x] The referenced October final pipeline ran from a fresh isolated kernel;
      Issue #57 adds no new executable notebook.
- [x] Required November Gate 1 outputs were generated and checked.
- [ ] Issue requirements have been completed; independent review and formal
      handoff approval remain outstanding.
- [x] Calculated outputs match the recorded source and frozen configuration.
- [ ] Independent review completed, if required.

**Reviewed by:** Pending

**Review date:** Pending

**Review notes:** Pending. The reviewer should verify the requirement mapping,
artifact paths and hashes, protected-test status, presentation ownership, and the
absence of any unapproved model or feature change.

## Completion

The Issue #57 artifact package is ready for independent review. The final model
and evaluation procedure are frozen, the presentation outline has initial
owners, and the protected test remains unscored. The remaining work is to
complete the independent review, record formal November Gate 1 approval and the
final commit, update the issue checklist, and then close Issue #57.
