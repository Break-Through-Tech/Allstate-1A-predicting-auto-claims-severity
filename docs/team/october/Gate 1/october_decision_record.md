# October Decision Record

## September recommendations

| ID | September recommendation | October decision | Owner | Handling |
|---|---|---|---|---|
| OCT-001 | Test rare-level handling strategies | Experiment | TBD | Compare leakage-safe categorical handling strategies using training-only mappings. |
| OCT-002 | Assess near-constant categorical fields | Experiment | TBD | Compare retained vs reduced feature sets using held-out MAE. |
| OCT-003 | Test nonlinear models for continuous predictors | Experiment | TBD | Include nonlinear/tree-based regression approaches in model comparison. |
| OCT-004 | Address collinearity in linear models | Experiment | TBD | Compare retaining correlated predictors, regularization, feature reduction, or other model-specific approaches. No automatic removal. |
| OCT-005 | Establish constant baselines | Required | TBD | Fit mean and median baselines on training data only. |
| OCT-006 | Inspect high-loss performance | Experiment | TBD | Supplement overall MAE with severity-stratified error analysis. |
| OCT-007 | Test feature-selection strategies | Experiment | TBD | Compare feature sets using the same claim-level train/validation/test split. Model-specific preprocessing is allowed. |
| OCT-008 | Preserve interpretability/business usefulness | Required consideration | Team | Consider interpretability alongside predictive performance. |
| OCT-009 | Assess future distribution stability | Deferred | Team | Requires future-period or external data not currently available. |

## Challenge Advisor guidance incorporated

### Feature engineering

Extensive feature engineering is not a primary October priority because the predictor meanings are anonymous.

Primary focus:

- encoding;
- feature selection;
- model choice; and
- model-specific preprocessing.

### Correlated predictors

The team may experiment with:

- retaining correlated predictors;
- dropping one of a pair;
- combining features;
- regularization; or
- dimensionality reduction.

Retaining correlated predictors is acceptable for predictive modeling unless validation evidence suggests otherwise.

### Fair model comparison

All comparable models should use the same claim-level train/validation/test split.

Different models may use different preprocessing or feature-engineering approaches.

### Input-availability decision

The Challenge Advisor previously confirmed that the supplied predictor fields may be assumed to be available at the time of prediction.

Therefore, no unresolved input-timing dependency blocks the first October modeling run.

## Gate reopening rule

An October experiment does not reopen a September gate unless it changes a frozen September artifact, source interpretation, field role, target definition, or evidence conclusion.

New modeling decisions should create a new October modeling-data/model version rather than rewriting September evidence.

## October approval

- [ ] Modeling contract reviewed
- [x] September recommendations triaged
- [x] Challenge Advisor guidance recorded
- [x] Carryover limitations documented
- [x] Initial modeling-data version approved
- [ ] GitHub Projects board updated