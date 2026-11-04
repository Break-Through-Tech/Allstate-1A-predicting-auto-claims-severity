# Issue #46: Feature Experiments Report

**Status:** Ready for independent review

**Owner:** Ragib Nehal

**Reviewer:** Mia Chavez (pending)

**Artifact version:** Workflow Run `OCT-RN-FEATURE-REVIEW-001`; notebook code commit `b22c13bdb56c939225000bf820ab8642f99a5726`; exact file hashes in `notebooks/ragib-nehal/oct-notebooks/feature-experiments-review/receipt/artifact_manifest.csv`

## Scope

Issue #46 records the October feature inclusion decision, runs optional
experiment O1, analyzes prediction errors including high-loss claims, checks
overfitting and prediction failures, and prepares an independent reproduction
and Gate 3 approval record. O2-O4 are explicitly deferred as findings for the
November handoff process. The protected test partition is outside this work.

The resulting comparison is evidence for the team, not a final model-selection
decision. Retaining E02-full means only that O1 did not justify replacing its
130-predictor configuration in this experiment. Issue #47 governs completion
and any provisional November candidate, while Issue #48 owns the November
handoff and team decision process.

## Final artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Executed analysis | `analysis/error_analysis.ipynb` | Reproduces E02, runs O1, applies the selection rule, and exports diagnostics. |
| Feature comparison | `outputs/feature_experiment_comparison.csv` | Records fold and validation MAE, runtime, feature counts, and the retained run for this experiment. |
| Feature decisions | `outputs/feature_decisions.csv` | Records the O1 decision and O2-O4 deferrals. |
| Row-level evidence | `outputs/validation_predictions.csv` | Supports independent MAE and error-diagnostic recalculation for 28,248 validation claims. |
| Error diagnostics | `outputs/error_diagnostics.csv` | Reports support, MAE, signed error, error quantiles, underprediction, and failure counts. |
| Largest errors | `outputs/largest_errors.csv` | Records the retained Issue #46 comparison configuration's 25 largest validation absolute errors. |
| Run receipt | `receipt/run_receipt.json` | Binds inputs, code, settings, environment, consultations, and output hashes. |
| Artifact manifest | `receipt/artifact_manifest.csv` | Records the exact path, SHA-256, and size of each bundle file. |
| November findings | `records/november_handoff.md` | Supplies O2-O4 hypotheses and deferral reasons to the Issue #48 handoff process. |
| Verification | `verification/verify_feature_experiments_review.py` | Independently checks the evidence contract and exact artifact versions. |

All paths are relative to this draft bundle.

## Method

- Modeling data `OCT-MD-001`, split `OCT-SPLIT-001`, seed 42, training
  131,822 claims, and validation 28,248 claims were fixed throughout.
- The protected 28,248-claim test partition was excluded before feature
  analysis. It was not summarized, fitted, predicted, or scored.
- The full E02 reproduction and O1 used HGB with absolute-error loss, learning
  rate 0.1, 63 maximum leaves, 50 minimum samples per leaf, 200 maximum
  iterations, early stopping, and random state 42.
- Category pooling used the 132-claim training threshold. A fresh encoder and
  model were fitted inside each of the five recorded training folds.
- O1 removed 31 categorical fields whose most common training level exceeded
  99% support, leaving 85 categorical and 14 continuous predictors.
- O1 could replace the full feature set only if both mean CV MAE and validation
  MAE improved by at least 1%.
- The run used Python 3.12.12, scikit-learn 1.6.1, pandas 2.3.3, and NumPy
  2.3.5. Validation was consulted once for the E02 reproduction and once for
  the new O1 configuration.

## Results

| Run | Predictors | Train 5-fold CV MAE | CV SD | Validation MAE | Issue #46 result |
|---|---:|---:|---:|---:|---|
| E02-full | 130 | 1,171.51 | 5.87 | 1,151.24 | Retained comparison configuration |
| O1 | 99 | 1,172.58 | 6.64 | 1,152.50 | Not retained |

O1 regressed mean CV MAE by 0.0915% and validation MAE by 0.1094%. It did not
meet either side of the 1% improvement rule, so the recorded feature decision
is to retain all 130 predictors for this experiment. This does not confirm a
final selected model or final feature set. O2-O4 are deferred with reasons in
`records/november_handoff.md` for consideration through Issue #48.

For the retained E02 reproduction, validation MAE was 874.15 below training
p90 (25,422 claims), 3,007.94 from p90 to p99 (2,547 claims), and 9,450.11 at
or above p99 (279 claims). Mean signed error was -315.09 overall and -9,450.11
in the p99 segment, showing substantial underprediction of the largest claims.
All 279 p99 claims were underpredicted. These segments are diagnostics, not
additional selection metrics.

The full model's validation MAE was 20.26 lower than its CV mean, about 3.45 CV
standard deviations in the optimistic-for-validation direction. This is not
the usual overfitting direction, but it reinforces the limitation of drawing a
general conclusion from one split. No HGB prediction was negative or
non-finite. The previously reviewed Ridge predictions contained 270 negative
values and no non-finite values.

## Anomalies and limitations

- The retained HGB comparison configuration still performs poorly on large
  claims; the p99 segment has MAE 9,450.11 and only 279 validation claims.
- September EDA used the full labeled file, so October validation is protected
  from fitting but is not wholly unseen by the broader project.
- One random internal split cannot establish temporal or population stability.
- The issue #45 review rerun used newer libraries. This run deliberately uses
  the repository-pinned scikit-learn 1.6.1 environment and reproduces the same
  within-experiment conclusion with a validation MAE within 0.08.
- The predictors are anonymous. Model coefficients, splits, or importance
  scores describe model behavior only; they do not establish a predictor's
  business meaning, causal effect, or suitability for an individual claim
  decision.
- O1 tests one predeclared exclusion rule. It does not establish that every
  retained field is individually necessary.
- Issue #46 does not establish a final selected model. That conclusion remains
  subject to the Issue #47 completion process and Issue #48 team handoff.

## Verification

- [x] Author executed the notebook from a clean code commit and fresh kernel.
- [x] Author verifier independently recomputed hashes, feature rules, row
  coverage, MAEs, severity supports, decision logic, and receipt provenance.
- [x] Required outputs were generated inside the draft bundle.
- [ ] Independent reviewer reran the notebook from the recorded artifact version.
- [ ] Independent reviewer rebuilt the comparison table and audited the retained Issue #46 configuration.
- [ ] Full-team Gate 3 decisions were recorded.

**Reviewed by:** Mia Chavez (pending)

**Review date:** Pending

**Review notes:** Independent reproduction has not started. No reviewer
agreement or disagreement is recorded yet.

## Completion

The author draft is ready for independent review. Issue #46 and Gate 3 remain
open. The Gate 1 experiment register has not been changed, the artifacts have
not been promoted, and no team approval or final model selection has been
inferred.
