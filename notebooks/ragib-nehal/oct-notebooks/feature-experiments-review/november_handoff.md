# Issue #46 November Handoff: Deferred Optional Experiments

**Status:** Draft for independent review  
**Owner:** Ragib Nehal  
**Workflow Run:** `OCT-RN-FEATURE-REVIEW-001`  
**Modeling data / split:** `OCT-MD-001` / `OCT-SPLIT-001`

## October feature decision

Optional experiment O1 removed 31 categorical fields whose most common level
exceeded 99% of the frozen training partition. The reduced 99-predictor HGB
configuration was compared with the full 130-predictor HGB configuration using
the same five training folds and one limited validation consultation.

O1 did not meet the predeclared selection rule. Its mean CV MAE was 1,172.58
versus 1,171.51 for the full model, and its validation MAE was 1,152.50 versus
1,151.24. These are regressions of 0.0915% and 0.1094%, respectively. The
October decision is therefore to retain all 130 predictors.

The excluded fields were identified from training frequency, not from weak
September marginal correlations or correlation with another predictor. Their
anonymous names do not establish business meaning or causal effects.

## Deferred hypotheses

### O2 — correlated continuous pairs

**Hypothesis:** Reducing the recorded correlated continuous pairs may change
MAE little for the tree model and may help a linear model.

**Reason deferred:** Correlation alone does not justify deleting a predictor.
The selected tree model can retain redundant predictors, and Ridge already uses
regularization. Any future O2 run must predeclare the exact pair member removed,
fit all decisions inside training data, and use the frozen comparison design.

### O3 — fold-safe data-driven feature selection

**Hypothesis:** Feature selection fitted independently inside each CV fold may
retain most predictive accuracy with fewer columns.

**Reason deferred:** O3 introduces another learned selection surface after the
limited October validation comparison. It is not needed to pass Gate 3. A
future run must learn ranking and top-k thresholds separately inside every
training fold and must not consult the protected test partition.

### O4 — log-transformed target

**Hypothesis:** Training Ridge on `log1p(loss)` and back-transforming with
`expm1` may reduce original-unit MAE by damping the upper tail.

**Reason deferred:** O4 changes the training target rather than feature
inclusion, and it is not required for Gate 3. If resumed, every score must be
calculated after back-transformation in original `loss` units.

## November boundary

These hypotheses are not approved experiments merely because they are listed
here. Before resuming one, the team must register an owner, training-only
procedure, validation-consult budget, stopping rule, software environment, and
comparison target. The October test partition remains protected until the
separate final-evaluation gate.
