# October Modeling Handoff

No winning model is selected in this handoff. This document identifies the frozen September evidence and the modeling boundaries October work should begin from.

## Frozen source and field roles

- Source: `data/allstate_claims_data.csv`
- Rows: 188,318
- Columns: 132
- Source SHA-256: `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03`
- Field roles:
  - 1 identifier: `id`
  - 116 categorical predictors: `cat1`-`cat116`
  - 14 continuous predictors: `cont1`-`cont14`
  - 1 regression target: `loss`
- Frozen field-role reference: `notebooks/final-deliverables/September/Gate 2/data_dictionary.csv`

## Target and evaluation metric

`loss` in original dollar units remains the regression target.

Primary evaluation metric: MAE on untouched validation data in original `loss` units.

`log1p(loss)` remains an exploratory visualization field and does not replace the original target or evaluation scale.

## Split / cross-validation design

October will create the train/validation split before fitting any learned preprocessing.

The exact split proportion or cross-validation design and random seed must be selected and recorded before model fitting begins.

Validation data must remain untouched during preprocessing and model fitting.

All compared models should use the same approved modeling-data version and evaluation split unless an experiment explicitly documents otherwise.

## Baseline plan

October begins with:

1. Mean-constant baseline fitted using training `loss` only.
2. Median-constant comparator fitted using training `loss` only.

Both are evaluated on untouched validation data using original-unit MAE.

Full-dataset descriptive constant MAE must not be reported as held-out performance.

## Leakage-safe preprocessing

Any learned preprocessing must be fitted on training data only, including:

- rare-level support thresholds;
- categorical encoders;
- unseen-category handling;
- scalers or transformations;
- imputation rules;
- feature-selection thresholds; and
- data-dependent bin boundaries.

Validation frequencies must not be used to modify training preprocessing.

## High-cardinality and unseen categories

The September evidence identifies:

- `cat116`: 326 levels
- `cat110`: 131 levels
- `cat109`: 84 levels

October should compare appropriate categorical handling strategies rather than treating these fields as automatically unusable.

Previously unseen validation categories must map to an explicit unknown/unseen representation supported by the selected encoder.

## Correlated-feature interpretation

Strong continuous predictor pairs include:

- `cont11`-`cont12`: r = 0.994
- `cont1`-`cont9`: r = 0.930
- `cont6`-`cont10`: r = 0.883

These relationships do not justify automatic removal, but they should be considered when interpreting individual linear-model coefficients.

## Candidate model families

Candidate regression families may include:

- mean-constant baseline;
- median-constant comparator;
- linear regression;
- regularized linear regression;
- random forest regression;
- gradient boosting regression;
- XGBoost regression;
- CatBoost regression; and
- neural-network regression if time and evidence justify it.

These are candidate experiments only. No winning model has been selected.

## Required validation evidence

Every candidate model should record:

- exact modeling-data version;
- split or cross-validation design;
- random seed;
- preprocessing configuration;
- features used;
- validation MAE in original `loss` units;
- additional metrics used;
- performance across the loss distribution where useful;
- treatment of unseen categorical levels; and
- limitations.

Because large-claim underprediction may be operationally important, October should supplement overall MAE with severity-stratified error analysis rather than relying on one aggregate score alone.

## Interpretability and business use

Model evaluation should consider both predictive performance and interpretability.

Validated findings should be translated into business-facing recommendations where the evidence supports them.

Anonymous predictors must not be assigned unsupported real-world meanings.

The final pipeline should be designed so preprocessing, feature definitions, and models can be updated reproducibly when new data becomes available.

## Unresolved questions for the Challenge Advisor

Potential follow-up questions for October:

1. Are there additional error metrics or severity bands Allstate would prefer alongside MAE for monitoring underprediction of high-loss claims?
2. If multiple models have similar validation performance, how should the team prioritize interpretability, maintainability, and operational usefulness?
3. If future-period data becomes available, what stability checks would be most useful before relying on the model operationally?

## October starting point

October planning begins from the approved September handoff, recommendation register, findings register, and frozen Artifact Bundle.

No speculative implementation ticket should be treated as approved September work before the handoff is accepted.