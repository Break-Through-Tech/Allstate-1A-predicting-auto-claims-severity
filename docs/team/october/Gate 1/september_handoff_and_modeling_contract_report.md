# Issue #40: September Handoff and Modeling Contract

**Status:** Ready for team review  
**Owners:** Liam Stapley, Jonathan Deng  
**Milestone:** Modeling / October

## Scope

Formalize the transition from the approved September EDA handoff into October modeling.

The work freezes the initial modeling dataset, target, eligible features, evaluation metric, and modeling boundaries; incorporates September recommendations and limitations; records Challenge Advisor guidance; and establishes the requirements for fair model comparison.

## Deliverables

- `docs/team/october/Gate 1/modeling_contract.md`
- `docs/team/october/Gate 1/october_decision_record.md`
- `notebooks/final-deliverables/October/Gate 1/modeling_run_manifest.json`
- Updated GitHub Projects board

## September handoff

The October contract references the approved September Artifact Bundle and frozen source:

- Source: `data/allstate_claims_data.csv`
- Rows: 188,318
- Columns: 132
- Target: `loss`
- Eligible predictors: `cat1`-`cat116`, `cont1`-`cont14`
- Excluded inputs: `id`, `loss`
- Primary metric: MAE in original `loss` units

## Challenge Advisor guidance

The October contract incorporates the following guidance from Nancy Zhang:

- Because the predictor definitions are anonymous, extensive feature engineering is not recommended as a primary focus. The team should prioritize encoding, feature selection, and model choice.
- Highly correlated continuous predictors may be retained, removed, combined, regularized, or handled through dimensionality reduction depending on the model and validation results.
- Fair model comparison does not require identical preprocessing across models. Comparable models should use the same claim-level train/validation/test split.

## Evaluation boundaries

- The claim-level split is frozen before comparable modeling begins.
- Learned preprocessing is fitted on training data only.
- Validation data is used for model comparison and tuning; the test partition remains untouched until final evaluation.
- Mean- and median-constant baselines are required.
- MAE remains the primary comparison metric in original loss units.
- Model-specific preprocessing is allowed as long as validation and test leakage are avoided and the same claims remain in the same partitions.

## September EDA exposure

September EDA used the full labeled dataset before the October modeling split.

Feature-selection, preprocessing, and model hypotheses informed by that work are therefore documented as prior EDA exposure. Internal validation remains protected from model fitting, but it is not described as wholly unseen external evidence.

## Input-availability decision

The Challenge Advisor previously confirmed that the supplied predictor fields may be assumed to be available at the time of prediction.

Therefore, no unresolved input-timing dependency blocks the first October modeling run.

## Completion status

The modeling contract, October decision record, initial modeling manifest, and board plan are complete.

Issue #40 can close after full-team review and approval are recorded.