# Issue #46 Findings for the November Handoff

**Status:** Draft findings for independent review and team consideration

**Owner:** Ragib Nehal

**Workflow Run:** `OCT-RN-FEATURE-REVIEW-001`

**Modeling data / split:** `OCT-MD-001` / `OCT-SPLIT-001`

**Handoff owner:** Issue #48, November handoff and communication

## Scope and decision boundary

This document is an Issue #46 input to the team process owned by Issue #48. It
is not the approved November handoff, does not name a final selected model, and
does not authorize final evaluation or deployment. Issue #47 separately governs
October completion and whether the evidence supports naming a provisional
candidate for November.

The results below are experimental findings for team review. References to the
full E02 reproduction mean only that its 130-predictor configuration was
retained as the comparison outcome for O1. They do not confirm E02, or any other
approach, as the project's final selected model.

## Issue #46 feature-experiment finding

Optional experiment O1 removed 31 categorical fields whose most common level
exceeded 99% of the frozen training partition. The reduced 99-predictor HGB
configuration was compared with the full 130-predictor HGB configuration using
the same five training folds and one limited validation consultation.

O1 did not meet the predeclared selection rule. Its mean CV MAE was 1,172.58
versus 1,171.51 for the full model, and its validation MAE was 1,152.50 versus
1,151.24. These are regressions of 0.0915% and 0.1094%, respectively. Within
this specific O1 comparison, the evidence supports retaining all 130 predictors
instead of adopting the 99-predictor variant. This is a finding for the team,
not confirmation of the final model or final feature set.

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

Issue #48 owns consolidation of these findings into the November handoff,
full-team presentation, approvals, dissent, unresolved risks, and Gate 4
record. Issue #47 owns the completion decision and any provisional candidate
language. Until those processes are completed, Issue #46 records no final
selected model.
