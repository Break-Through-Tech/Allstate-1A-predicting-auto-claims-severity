# Issue #21: Findings and Limitations

**Status:** Approved
**Owner:** Ragib Nehal
**Independent reviewer:** Liam Stapley
**Register version:** 2.0.0

## Scope

Synthesize the September data-quality, target, categorical, and continuous
evidence into one canonical findings register. Separate measurements from
interpretations and possible October modeling tests, document the limits of the
available data, and provide a source-level recalculation workflow for an
independent reviewer.

## Final artifacts

- The executable synthesis notebook is
  [`ragib_nehal_task_13.ipynb`](../../../../notebooks/ragib-nehal/ragib_nehal_task_13.ipynb).
- The canonical register remains
  [`findings_register.csv`](../../../../notebooks/final-deliverables/September/Gate%202/findings_register.csv).
- The Gate 3 evidence bundle is in
  [`findings-and-limitations/`](../../../../notebooks/final-deliverables/September/Gate%203/findings-and-limitations/).
- Independent-review status is recorded in
  [`independent_review_register.csv`](../../../../notebooks/final-deliverables/September/Gate%202/independent_review_register.csv).

The evidence bundle contains `finding_evidence_checks.csv`,
`independent_recalculation_results.csv`, and `run_manifest.json`.

## Method

The notebook verifies the frozen source SHA-256, ordered schema, and exact
188,318-row by 132-column shape before analysis. It recalculates the source
integrity checks, target summary, representative categorical cardinalities,
Pearson and Spearman continuous-to-target correlations, all 91 unique
continuous-feature Pearson correlations, and continuous quantile-bin target
summaries directly from `data/allstate_claims_data.csv`.

The canonical register retains its existing 16-column schema. Every finding has
a stable ID, exact evidence path and hash, evidence locator, observed result,
interpretation, limitation, and a separate possible October implication.
Modeling proposals are not presented as conclusions from the EDA.

Existing human review metadata is preserved only when the referenced evidence
hash is unchanged. A changed evidence version returns the finding to pending
review.

## Findings

### F-001: Raw loss has a long right tail

Mean loss is $3,037.34, median loss is $2,115.57, the 95th percentile is
$8,508.54, the maximum is $121,012.25, and raw skewness is 3.795. These values
directly show a strongly right-skewed severity distribution. They do not show
that high-loss records are invalid.

### F-002: The source table is complete and row-unique

The source has 188,318 rows, 132 columns, zero missing cells, 188,318 unique
identifiers, and zero fully duplicated rows. This creates a light repair burden,
but it does not establish semantic validity or eliminate the need for
training-only preprocessing.

### F-003: Categorical cardinality is mixed

The source contains 116 categorical predictors. Seventy-two have exactly two
levels and 88 have at most four, while `cat109`, `cat110`, and `cat116` have 84,
131, and 326 levels. High cardinality and rare support are reasons to test
appropriate encoders, not automatic reasons to remove fields.

### F-004: Marginal linear continuous-to-target relationships are weak

The strongest absolute raw Pearson correlations with `loss` are `cont2` at
0.142, `cont7` at 0.120, and `cont3` at 0.111. Every continuous predictor is
below 0.15 in absolute value. This is direct evidence about marginal linear
association, not evidence of low conditional or nonlinear predictive value.

### F-005: Binned target views show patterns hidden by one coefficient

`cont1` has raw Pearson correlation -0.010, but its binned median loss falls to
$1,937.03 in bin 7 and rebounds to $2,237.60 in bin 9. For `cont2`, mean loss
rises from $2,120.27 in the first realized bin to $3,481.26 in the last, while
the median is not monotonic throughout. These descriptive views are consistent
with nonlinear or non-monotonic patterns, but their shapes may change outside
this dataset.

### F-006: Selected continuous predictors are strongly redundant

The strongest continuous-feature pairs are `cont11`–`cont12` at 0.994,
`cont1`–`cont9` at 0.930, and `cont6`–`cont10` at 0.883. These relationships can
complicate later linear-model coefficient interpretation, but they do not prove
that either member of a pair is unnecessary.

### F-007: Interpretation and external-validation limits remain

The predictor names are anonymous, so statistical patterns cannot be assigned
specific business meanings or causal explanations. The repository supplies one
claims CSV and no separate test or future-period dataset. October can still
create untouched internal validation partitions, but future-period and external
generalization will remain unmeasured.

## Possible October tests

- Compare mean-constant, median-constant, linear, and nonlinear approaches using
  MAE in original `loss` units on untouched validation data.
- Fit encoders, rare-level handling, transformations, and any bin boundaries on
  training partitions only, including explicit handling for unseen levels.
- Review errors across the severity distribution rather than relying only on an
  overall average.
- Compare retained and reduced correlated-feature sets using held-out MAE and
  interpret coefficients cautiously when redundant predictors coexist.

These are proposed tests, not modeling decisions or claims of expected
performance.

## Verification

- [x] Frozen source hash, shape, schema, missingness, uniqueness, and duplicate
  checks pass.
- [x] Required target and categorical values are recalculated from the source.
- [x] All 14 continuous-to-target relationships and all 91 unique continuous
  pairs are recalculated.
- [x] Seven stable findings link to current evidence paths and SHA-256 hashes.
- [x] Automated comparisons support at least five headline findings.
- [x] Modeling tests are separated from directly observed results.
- [x] A named non-author has independently rerun and inspected the calculations.
- [x] Reviewer, date, decision, disagreements, and limitations are recorded.

## Independent review

Liam Stapley completed the independent review on 2026-10-04. The review covered
the target summary, representative categorical cardinalities, continuous-to-
target correlations, the strongest continuous-feature pairs, headline finding
checks, limitations, and the canonical register. No blocking disagreement was
recorded. The review metadata and the current semantically equivalent F-006
evidence hash are synchronized across the register, evidence bundle, and review
records.
