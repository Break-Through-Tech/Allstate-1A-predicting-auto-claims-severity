# Issue #46 Feature Experiments and Review Implementation Record

**Author:** Ragib Nehal

**Implementation date:** 2026-11-04

**Workflow Run:** `OCT-RN-FEATURE-REVIEW-001`

**Status:** Author verification complete; independent review pending

## Objective

Produce a self-contained draft evidence bundle for issue #46 without changing
the Gate 1 experiment register or promoting artifacts before independent
review.

## Delivered work

- Executed `error_analysis.ipynb` against `OCT-MD-001` and frozen split
  `OCT-SPLIT-001` using seed 42 and the five recorded training folds.
- Reproduced the full-feature E02 HGB model and compared it with O1, which
  removed 31 categorical fields identified solely from training frequency.
- Exported row-level validation predictions, feature decisions, model
  comparison results, error diagnostics, the 25 largest selected-model errors,
  a run receipt, and an artifact manifest.
- Added a standalone verifier plus mutation tests for source/manifest identity,
  claim-level target alignment, feature selection, predictions, every severity
  diagnostic, largest-error values, receipt provenance, notebook execution,
  and pending review state.
- Prepared the November deferral handoff, feature experiments issue report, independent-review
  checklist, reviewer evidence directory, and Gate 3 approval record.
- Grouped the draft bundle into `analysis/`, `outputs/`, `receipt/`, `verification/`,
  `review/`, and `records/`. `review/reviewer_reproduction/` is reserved for Mia
  Chavez's independently generated evidence. The canonical report remains in
  `docs/team/october/Gate 3/feature_experiments_report.md`.

## Decisions

O1 used 99 predictors after excluding 31 categorical fields whose dominant
training level exceeded 99% support. It produced mean CV MAE 1,172.58 and
validation MAE 1,152.50, compared with 1,171.51 and 1,151.24 for full E02.
Those changes were regressions of 0.0915% and 0.1094%, so O1 failed the
predeclared requirement for at least 1% improvement in both measures. The
recorded Issue #46 experiment decision is to retain all 130 predictors rather
than adopt O1. This is a finding for team consideration, not confirmation of a
final selected model or final feature set. Issue #47 governs completion and any
provisional candidate; Issue #48 owns the November handoff and team decision.

O2-O4 were deferred with their hypotheses and reasons preserved in
`records/november_handoff.md`. Correlation or weak marginal association alone was not
used to remove any field. Anonymous predictors were not assigned business
meaning or causal effects.

## Verification evidence

- Export paths in the notebook now write into `outputs/` and `receipt/`. That
  path edit changed the notebook code hash. The notebook was not re-run, and
  the five output CSV hashes did not change. The receipt and the notebook's
  printed receipt use the updated code hash.
- The final notebook ran from a fresh Python 3.12 kernel with scikit-learn
  1.6.1, pandas 2.3.3, and NumPy 2.3.5.
- The standalone verifier passed all frozen-input, row-coverage, metric,
  diagnostic, receipt, manifest, and pending-approval checks.
- Five mutation tests demonstrated that the verifier rejects claim-ID target
  reassignment, corrupted severity diagnostics, corrupted largest-error values,
  personal workspace paths, stale plans, and Markdown whitespace errors.
- Seventy-one relevant repository modeling tests passed.
- The full repository suite had 76 passes plus two pre-existing issue #21
  failures caused by its stale reference to the removed
  `notebooks/ragib-nehal/ragib_nehal_task_13.ipynb` path.
- All committed issue #46 files remain under this draft directory. The Gate 1
  experiment register is unchanged.

## Limitations

- The p99 validation segment contains only 279 claims and remains poorly
  predicted, with selected-model MAE 9,450.11.
- September EDA used the full labeled file, so validation is protected from
  fitting but is not wholly unseen by the broader project.
- One random split cannot establish temporal or population stability.
- O1 evaluates one predeclared exclusion rule and does not establish that every
  retained field is individually necessary.

## Review status

Mia Chavez's independent reproduction and selected-candidate audit have not
started. All six team decisions and the Gate 3 decision remain pending. Any
Gate 1 register update or artifact promotion requires a separate user-approved
post-review step.
