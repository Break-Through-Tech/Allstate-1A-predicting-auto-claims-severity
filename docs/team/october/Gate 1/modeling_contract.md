# October Modeling Contract

## Prediction task

Estimate one claim's final paid amount (`loss`) from the anonymous claim fields available in the modeling dataset.

This should not be described as an up-front claim estimator until the Challenge Advisor confirms which predictor fields are available when a claim is first filed.

## September handoff

Approved September handoff artifacts:

- `notebooks/final-deliverables/September/Gate 4/artifact_bundle_checklist.md`
- `notebooks/final-deliverables/September/Gate 4/september_report.md`
- `notebooks/final-deliverables/September/Gate 4/october_recommendation_register.csv`
- `notebooks/final-deliverables/September/Gate 4/october_modeling_handoff.md`
- `notebooks/final-deliverables/September/Gate 4/handoff_review_record.md`
- `notebooks/final-deliverables/September/Gate 4/completion_review_record.md`

Frozen September reproducibility receipt:

- Workflow Run ID: `G3-20260929T042604Z-5ece32b7`
- Gate 1 Artifact Bundle ID: `GATE1-3c893f22f14ced97`
- Gate 2 Artifact Bundle ID: `GATE2-8e529ab389c94c3d`
- Gate 3 Artifact Bundle ID: `GATE3-c4860456366d67d3`
- Source SHA-256: `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03`

## Frozen modeling dataset

Source:

`data/allstate_claims_data.csv`

Dataset shape:

- 188,318 rows
- 132 columns

Field roles:

- `id`: identifier only
- `cat1`-`cat116`: categorical predictors
- `cont1`-`cont14`: continuous predictors
- `loss`: regression target

Initial modeling inputs:

- include `cat1`-`cat116`
- include `cont1`-`cont14`
- exclude `id`
- exclude `loss`

All 188,318 valid source rows are eligible for the initial modeling split unless a later documented experiment explicitly changes the modeling-data version.

## Target and metric

Target:

`loss`

Primary comparison metric:

MAE in original `loss` units.

Every reported model score must identify:

- modeling-data version;
- partition or fold;
- claim count;
- preprocessing/model configuration; and
- evaluation code/version.

`log1p(loss)` remains an EDA/visualization field and is not the primary evaluation scale.

## Evaluation design

The same claim-level train/validation split must be used across comparable models.

Different model families may use different preprocessing, encoding, feature-selection, or feature-engineering approaches when appropriate.

The comparison remains fair as long as:

- the same claims are assigned to the same training and validation partitions;
- learned preprocessing is fit using training data only;
- validation data remains excluded from fitting/tuning;
- each preprocessing/model configuration is documented; and
- all reported scores use the same defined evaluation metric and validation claims.

The exact split design and random seed must be frozen before the first comparable model run and recorded in `notebooks/final-deliverables/October/modeling_run_manifest.json`.

## Required baselines

The first modeling comparison must include:

1. mean-constant baseline fitted on training `loss`;
2. median-constant baseline fitted on training `loss`.

Both must be evaluated on the same held-out validation partition using MAE in original loss units.

## Candidate modeling work

October may evaluate:

- linear regression;
- regularized linear regression;
- random forest regression;
- gradient boosting regression;
- XGBoost regression;
- CatBoost regression; and
- other justified regression approaches.

No winning model is selected in this contract.

## Feature and preprocessing hypotheses inherited from September

September EDA exposed the team to the full labeled dataset before the internal modeling split.

Relevant hypotheses include:

- rare and high-cardinality categorical levels may require specialized encoding;
- some categorical predictors are highly dominant;
- continuous predictors have weak marginal linear relationships with `loss`;
- binned target views suggest some nonlinear or non-monotonic relationships;
- several continuous predictor pairs are highly correlated.

These are prior EDA observations, not untouched validation discoveries.

Any October feature-selection, preprocessing, or model experiment motivated by these findings must be described as informed by September full-file EDA.

## Feature engineering

Because the predictor meanings are anonymous, semantic feature engineering is not a primary October focus.

Challenge Advisor guidance indicates that previous teams did not do extensive feature engineering because the feature definitions are unavailable. October work should therefore prioritize:

- categorical encoding;
- feature selection;
- model choice; and
- model-specific preprocessing.

Statistically defined transformations or interactions may still be tested if justified, but they should be treated as optional experiments rather than required modeling work.

Any derived feature must remain reproducible and must not use validation information during construction where the transformation is learned from data.

## Correlated predictors

September identified several strongly correlated continuous predictor pairs.

Challenge Advisor guidance confirmed that there is no single required treatment. October may experiment with:

- leaving correlated predictors in;
- dropping one member of a correlated pair;
- combining correlated features;
- regularization;
- dimensionality-reduction techniques; or
- other model-specific approaches.

For predictive modeling, retaining correlated predictors may be acceptable. Their presence is more important to consider when interpreting coefficients or other feature-level effects.

No correlated predictor is removed automatically before model comparison.

## Challenge Advisor guidance

The following October modeling questions were discussed with the Challenge Advisor:

### Feature engineering

Because feature meanings are anonymous, extensive feature engineering is not recommended as a primary focus. The team should prioritize encoding, feature selection, and model choice.

### Correlated continuous predictors

Acceptable approaches include:

- dropping one feature;
- combining features;
- regularization;
- dimensionality reduction; or
- retaining the correlated predictors.

The team may experiment with these approaches. Retaining correlated predictors is likely acceptable for predictive modeling.

### Fair model comparison

Comparable models should use the same claim-level train/test or train/validation split.

Model-specific preprocessing and feature engineering may differ as long as the underlying claims in each partition remain the same.

### Input availability

The Challenge Advisor previously confirmed that the supplied predictor fields can be assumed to be available at the time of prediction.

For October modeling, all approved predictor fields may therefore be treated as eligible inputs from an availability/leakage-timing perspective.

This does not remove the need for standard train/validation leakage controls during preprocessing and model fitting.

## Modeling limitations

- Predictor meanings remain anonymous.
- September EDA used the full labeled dataset before the October split.
- A later internal validation partition is held out from modeling, but it is not wholly unseen in the same sense as an external dataset because September EDA informed modeling hypotheses.
- The supplied dataset cannot establish future-period distribution stability.
- Model performance will not by itself establish production readiness or determine an individual claim reserve.