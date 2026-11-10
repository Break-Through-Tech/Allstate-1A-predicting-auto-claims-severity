# November Modeling Handoff

## Purpose

This handoff transfers the approved October modeling work into the November Evaluation and Presentation milestone.

October established the experimental design, frozen data split, baselines, model comparison process, provisional candidate, feature experiments, diagnostic framework, and reproducibility requirements.

November should focus on final evaluation, interpretation, presentation, and clear documentation rather than restarting broad model exploration.

---

## Approved October Inputs

### Modeling versions

- Modeling data: `OCT-MD-001`
- Frozen split: `OCT-SPLIT-001`
- Seed: 42
- Train claims: 131,822
- Validation claims: 28,248
- Protected test claims: 28,248

### Required metric

Primary metric:

`MAE` in original `loss` units

Tail-segment MAE remains a diagnostic.

### Constant references

- Mean validation MAE: 1,962.92
- Median validation MAE: 1,805.09

---

## Provisional November Candidate

The provisional candidate is:

`CatBoostRegressor`

Configuration:

- top 75 selected predictors
- MAE loss
- depth 8
- learning rate 0.08
- maximum 500 iterations
- seed 42
- native categorical handling

October evidence:

- five-fold CV MAE: 1,153.58
- CV SD: 7.19
- final validation MAE: 1,136.34

The fitted model is preserved as a `.cbm` artifact and can be loaded without retraining.

The candidate remains provisional until final evaluation is completed under the approved November process.

---

## Approved Pipeline

The final pipeline:

1. verifies the frozen source and split;
2. loads the selected 75-feature list;
3. selects those predictors;
4. converts selected categorical inputs to the representation expected by CatBoost;
5. loads the saved fitted model;
6. generates predictions in original `loss` units;
7. calculates MAE and diagnostics.

No standardization, one-hot encoding, output transformation, or target transformation is required by the selected CatBoost model.

---

## October Artifacts to Carry Forward

November should use the approved versions of:

- September handoff
- October modeling contract
- frozen source manifest
- frozen split manifest
- evaluation plan
- baseline outputs
- leakage-safe preprocessing documentation
- experiment register
- controlled model-comparison results
- CatBoost/XGBoost experiment outputs
- feature-ranking results
- feature-selection results
- validation predictions
- tail diagnostics
- final model comparison
- final fitted CatBoost model
- selected 75-feature list
- final pipeline
- reproduction instructions
- independent-review records
- Gate 4 decision record

Final Gate 4 references:

- Artifact Bundle ID: `[FINAL ARTIFACT BUNDLE ID]`
- Workflow Run ID: `[FINAL WORKFLOW RUN ID]`
- Approved commit: `[FINAL COMMIT]`

---

## Issue #46 Feature Experiment Handoff

Issue #46 tested removing 31 categorical predictors whose dominant training category exceeded 99% support from the retained HGB configuration.

The reduced 99-feature HGB model did not improve CV or validation MAE.

That experiment therefore retained all 130 predictors for the HGB comparison.

Additional optional hypotheses O2, O3, and O4 were deferred to November.

These are optional and should not automatically displace higher-priority final evaluation and presentation work.

---

## Outstanding Limitations and Risks

### Validation exposure

September EDA used the full labeled dataset.

Later CatBoost permutation and SHAP importance analysis also used validation observations.

The October validation evidence is therefore useful for model development but should not be described as fully independent future-performance evidence.

### High-loss claims

Prediction error remains substantially larger for high-loss claims.

Only 279 validation claims fall at or above the training p99 threshold, limiting confidence in small model differences within that segment.

### Anonymous predictors

Predictor importance should be described statistically.

No anonymous feature should be assigned business or causal meaning without additional domain evidence.

### Temporal generalization

October uses a single random frozen split and does not demonstrate stability across future time periods.

---

## November Priorities

### 1. Freeze the model-selection decision

Do not continue broad hyperparameter or feature searches unless a blocking defect is discovered.

The October CatBoost configuration should remain frozen before opening the protected test set.

### 2. Final evaluation

Use the protected test partition only under the approved November evaluation process.

Report the test result as a final internal held-out evaluation, not as guaranteed future-period or first-filing performance.

Compare the final result with:

- mean constant
- median constant
- October CV evidence
- October validation evidence

### 3. Error analysis

Repeat the agreed diagnostics on the final evaluation set.

Include:

- overall MAE
- ordinary-loss segment
- p90-to-p99 segment
- p99-and-above segment
- prediction validity
- any extreme failures

### 4. Predictor interpretation

If time permits, summarize the strongest statistical predictors using the existing importance evidence.

Do not assign anonymous predictors business labels or causal interpretations.

### 5. Presentation

Prepare a clear explanation of:

- business problem
- frozen experimental design
- baseline
- approaches tested
- why CatBoost was selected
- feature-selection result
- final evaluation
- high-loss limitations
- what model outputs mean
- limitations and next steps

### 6. Documentation

Preserve:

- exact final evaluation code
- final model artifact
- selected feature list
- run receipt
- predictions
- evaluation table
- diagnostic tables
- presentation figures
- final conclusions

---

## Questions for the Challenge Advisor

The team should confirm the following as November evaluation proceeds:

1. When should the protected test partition be opened, and should it be used only once after the October model configuration is frozen?

2. For the final presentation, should high-loss segment performance remain a diagnostic alongside overall MAE, or should another secondary metric be emphasized?

3. Given that predictors are anonymous, how much feature-importance discussion is useful in the final presentation beyond identifying statistically influential fields?

4. Should the deferred Issue #46 feature hypotheses be revisited only if time remains after final evaluation and presentation work?

5. How should the team describe the relationship between retrospective validation performance and potential first-filing usefulness without overstating operational evidence?

---

## Gate 4 Handoff Record

Gate 4 passes when:

- required October results reproduce;
- no blocking data, split, leakage, metric, comparison, or reproducibility defect remains;
- the provisional model decision is documented;
- the protected test partition remains reserved;
- all six team members review the complete October evidence.

### Team Review

| Team member | Decision | Notes |
|---|---|---|
| Liam Stapley | Pending | |
| Mia Chavez | Pending | |
| Bernardo Xie He | Pending | |
| Prisha Agarwal | Pending | |
| Ragib Nehal | Pending | |
| Junaid Pathan | Pending | |

If the active six-person roster differs, update this table before approval.

Any dissent or unresolved risk should be recorded rather than silently removed.

---

## November Handoff Decision

Once Gate 4 is approved, October modeling is frozen and the top-75 CatBoost model becomes the provisional candidate transferred into November.

November work should prioritize final evaluation and communication.

Broad October-style model searching should not resume unless the final review identifies a blocking defect or the Challenge Advisor explicitly recommends reopening model selection.
