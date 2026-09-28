# Issue #20: Categorical Evidence

**Status:** Complete  
**Evidence notebook:** `categorical_evidence.ipynb`  
**Gate:** 3

## Scope

Verify the frozen categorical-analysis evidence and document the cardinality, support, dominant-level, high-cardinality, and target-pattern evidence required by Issue #20.

The Gate 3 notebook uses the frozen Gate 2 categorical inventory and level-to-target tables rather than redefining the categorical-analysis method.

## Artifacts

| Artifact | Location |
|---|---|
| Evidence notebook | `notebooks/final-deliverables/September/Gate 3/Categorical-evidence/categorical_evidence.ipynb` |
| Verification summary | `notebooks/final-deliverables/September/Gate 3/Categorical-evidence/categorical_evidence_summary.csv` |
| Low-support evidence | `notebooks/final-deliverables/September/Gate 3/Categorical-evidence/low_support_evidence.csv` |
| Dominant-level evidence | `notebooks/final-deliverables/September/Gate 3/Categorical-evidence/dominant_level_evidence.csv` |
| Uneven target evidence | `notebooks/final-deliverables/September/Gate 3/Categorical-evidence/uneven_target_evidence.csv` |
| High-cardinality evidence | `notebooks/final-deliverables/September/Gate 3/Categorical-evidence/high_cardinality_evidence.csv` |

## Results

The categorical inventory contains all 116 `cat*` predictors.

The required starting checks were reproduced:

| Check | Result |
|---|---:|
| Categorical fields | 116 |
| Fields with exactly 2 observed levels | 72 |
| Fields with at most 4 observed levels | 88 |
| `cat116` observed levels | 326 |
| `cat110` observed levels | 131 |
| `cat109` observed levels | 84 |

The frozen level-to-target table contains 1,139 observed field-level combinations.

## Low-Support Evidence

The rare-level threshold remains fewer than 188 claims, approximately 0.1% of the full 188,318-row dataset.

The evidence review identifies 39 categorical fields containing at least one rare level.

Every flagged level is reported with its support, the full-dataset denominator, row share, raw mean loss, raw median loss, and raw loss IQR.

Rare levels remain in the evidence. They are not automatically removed or combined.

## Dominant Levels

For Gate 3 evidence review, fields whose most-common level represents at least 99% of all rows are flagged as highly dominant.

31 fields meet this review condition.

Each dominant-level comparison reports the level's support, the 188,318-row denominator, and observed share.

This is an evidence flag only and does not imply that the field should be removed.

## Uneven Target Patterns

The notebook ranks fields by the spread in raw median loss between their lowest- and highest-median adequately supported levels.

Only levels with at least 188 observations are used for this ranking.

Each comparison records both category levels, their supports, full-dataset shares, raw median losses, and the observed difference.

These are marginal descriptive patterns. They do not establish causation or feature importance.

## High-Cardinality Fields

`cat116`, `cat110`, and `cat109` were reviewed separately.

High cardinality is not treated as evidence that a predictor is unusable.

The evidence table records total levels, adequately supported levels, rare levels, rare-row support, and rare-row share. Rare levels remain represented in the frozen level-to-target table.

## Raw Target Evidence

Every one of the 1,139 categorical field-level comparisons includes:

- level support;
- raw mean `loss`;
- raw median `loss`;
- raw first and third quartiles; and
- raw interquartile range.

`log1p(loss)` is used only as a visualization scale in the categorical-analysis method and does not replace the raw-unit evidence.

## Limitations

The categorical predictors are anonymized, so observed differences cannot be assigned specific real-world explanations.

Low-support category summaries may be unstable.

Dominance and median-loss spread are descriptive EDA evidence and are not automatic feature-selection rules.

No category or categorical predictor is removed as part of this Gate 3 evidence review.

## Verification

- [x] Inventory covers all 116 categorical fields.
- [x] Required starting cardinality checks reproduced.
- [x] Low-support fields and levels identified with support and denominator.
- [x] Dominant levels identified with support and denominator.
- [x] Uneven target patterns identified with support and denominator.
- [x] High-cardinality fields reviewed without assuming they are unusable.
- [x] Rare levels retained during EDA.
- [x] Every categorical target comparison includes support and raw target summaries.

## Completion

The Gate 3 categorical evidence satisfies the requirements of Issue #20.

The issue can be closed after the notebook and generated evidence files are committed.