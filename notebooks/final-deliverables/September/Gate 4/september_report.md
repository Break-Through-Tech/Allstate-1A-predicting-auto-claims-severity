# September Report: Understanding Allstate Claim Severity

Plain-language handoff for Issue #22, written from the frozen Gate 2/Gate 3
evidence in `notebooks/final-deliverables/September/`.

## What one row represents

Each row in `data/allstate_claims_data.csv` is one anonymized auto-insurance
claim. `id` identifies the row only and is excluded from any distribution or
target-effect interpretation. `cat1`-`cat116` are anonymous nominal
categorical fields — their codes carry no order. `cont1`-`cont14` are
anonymous continuous fields scaled to 0-1; we don't know their original units.
`loss` is the claim's total paid amount and is the project's regression
target.

## What the target represents, and why its distribution matters

`loss` is strictly positive and heavily right-skewed (skewness 3.795). Most
claims are modest, but a small share are very large:

| Statistic | Value |
| --- | --- |
| Mean | $3,037.34 |
| Median | $2,115.57 |
| 95th percentile | $8,508.54 |
| Maximum | $121,012.25 |

Because the mean sits well above the median, a handful of large claims pull
the average up. Reserve planning has to account for that tail, not just a
typical claim. We use `log1p(loss)` only to make plots readable — every
headline statistic above, and future MAE evaluation, stays in original
dollar units.

## Most important data-quality findings

- The delivered file matches its recorded identity exactly: 188,318 rows, 132
  columns, 0 missing cells, 0 duplicate rows, and a unique `id` for every row
  (`Gate 3/data_quality_evidence/validation_results.csv`).
- All 116 `cat*` fields and 14 `cont*` fields, plus `loss`, pass their schema
  and range checks — the dataset needed very little repair.
- A clean dataset does not mean an easy dataset: level support, distribution
  shape, and target relationships still need the analysis described below
  (`anomaly_register.csv` entries EDA-NB-001 through EDA-NB-006).

## Categorical cardinality and support patterns

- 72 of 116 categorical fields have only 2 observed levels; 88 have at most 4.
- A few fields are high-cardinality: `cat116` (326 levels), `cat110` (131
  levels), `cat109` (84 levels).
- 523 levels across 39 fields fall below our declared rare-level threshold of
  188 supporting rows (14,721 affected rows total).
- 31 fields have one level holding more than 99% share, and 9 fields have
  fewer than two levels meeting the support threshold — target comparisons on
  those fields are unreliable because they're driven by very small groups.

## Continuous distributions, target relationships, and redundancy

- No continuous predictor has a strong linear marginal relationship with raw
  `loss`. The strongest absolute Pearson correlations are `cont2` (0.142),
  `cont7` (0.120), and `cont3` (0.111) — weak, but not evidence of low
  predictive value once combined with other features or modeled nonlinearly.
- Binned mean/median/spread views show patterns a single correlation
  coefficient can hide; several fields show non-monotonic target behavior
  across bins even with a weak overall correlation.
- Several continuous predictors are strongly correlated with each other:
  `cont11`-`cont12` (0.994), `cont1`-`cont9` (0.930), and `cont6`-`cont10`
  (0.883). This redundancy matters for later linear-model interpretation, but
  no feature was removed in September.

## What remains unknown because predictors are anonymous

We do not know what any `cat*` or `cont*` field actually measures (vehicle
attributes, policy terms, geography, etc. are only illustrative examples from
the project overview, not a confirmed mapping). That means we can describe
associations, not causes, and we cannot say a given field is "really" about
any specific real-world quantity.

## What was deferred to October

- Model comparison, hyperparameter tuning, target encoding, feature
  selection, SHAP analysis, and dashboard development were explicitly out of
  scope for September and have not started.
- Deciding how to encode high-cardinality and rare categorical levels for
  modeling.
- Investigating the strongly correlated continuous predictors for their
  effect on linear-model interpretation.

## Important limitations

- The meanings of the `cat*` and `cont*` predictors remain anonymous. Statistical patterns cannot be assigned confirmed business meanings without additional documentation.
- Marginal association does not establish causation or complete predictive usefulness. A weak individual correlation does not mean a feature will be unhelpful in a multivariable or nonlinear model.
- Large claims are relatively sparse but economically meaningful. They should not be removed simply because they are uncommon.
- The project contains one labeled claims dataset. September analysis cannot establish whether these distributions or relationships will remain stable in future periods or external populations.
- `log1p(loss)` and other transformed target views are visualization tools, not model-evaluation results. Model evaluation remains on original-unit `loss`.
- September EDA does not establish production readiness, authorize automated claim decisions, or determine an appropriate reserve for an individual claim.

## What the evidence does not justify

- It does not establish causation for any observed association.
- It does not determine an individual claim's reserve.
- It does not prove production readiness or authorize automated claims
  decisions.
- `log1p(loss)` plots are for readability only, not a stand-in for
  evaluation on the original scale.
