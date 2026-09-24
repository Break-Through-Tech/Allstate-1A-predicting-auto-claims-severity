# Issue #16: Categorical-Analysis Method

**Status:** Reviewed; methodology confirmation pending  
**Authors:** @ezixuan27 and @jonathandeng7  
**Reviewer:** Liam Stapley  
**Review result:** Numerical requirements covered; plotting approach and rare-level threshold require confirmation

## Scope

Analyze all 116 anonymous categorical predictors, including their observed category levels, support, and marginal relationships with claim severity.

The analysis uses raw `loss` for numerical target summaries and `log1p(loss)` for readable low-cardinality visualizations.

## Artifacts

| Artifact | Location |
|---|---|
| Categorical-analysis notebook | `notebooks/final-deliverables/September/Gate 2/task_6.ipynb` |
| Categorical inventory | `notebooks/final-deliverables/September/Gate 2/categorical_inventory.csv` |
| Level-to-target tables | `notebooks/final-deliverables/September/Gate 2/categorical_level_target_tables.csv` |
| Data dictionary | `notebooks/final-deliverables/September/Gate 2/data_dictionary.csv` |

## Method

### Categorical inventory

The notebook calculates the following for all 116 `cat*` predictors:

- Cardinality
- Most- and least-common level support
- Most-common level share
- Minimum and median level support
- Number of levels below the rare-level threshold

### Rare-level rule

A level is classified as rare when its support is fewer than 188 claims, approximately 0.1% of the 188,318 delivered observations.

This threshold is used to identify levels with limited support and keep high-cardinality visualizations readable. It is an EDA display and support rule, not an instruction to remove observations, category levels, or predictors.

### Level-to-target analysis

The notebook generates raw-unit target summaries for every observed level of every categorical predictor. Each entry includes:

- Level support
- Mean raw `loss`
- Median raw `loss`
- First and third quartiles of raw `loss`
- Interquartile range

Rare levels remain in the numerical tables.

### Low-cardinality analysis

Fields with four or fewer observed levels are classified as low-cardinality.

The notebook generates boxplots of `log1p(loss)` for eight selected low-cardinality fields and provides raw-unit level-to-target summaries.

The plotting approach is selective; the complete numerical tables retain results for all low-cardinality fields.

### High-cardinality analysis

The notebook generates ordered point views for `cat116`, `cat110`, and `cat109`.

These views focus on adequately supported levels rather than displaying hundreds of category labels. The rare tail is summarized separately.

The full numerical tables retain all observed levels, including those omitted from the selected plots.

### Categorical encoding

The analysis uses original categorical labels. It does not calculate categorical associations using arbitrary alphabetic-to-integer codes.

## Results

| Output | Observed result |
|---|---:|
| Categorical predictors analyzed | 116 |
| Observed field-level combinations | 1,139 |
| Fields with exactly two levels | 72 |
| Fields with four or fewer levels | 88 |
| Fields containing at least one rare level | 39 |
| Fields with one level exceeding 99% support | 31 |
| Low-cardinality fields plotted | 8 |
| High-cardinality fields plotted | 3 |

The categorical inventory covers all 116 source predictors. The level-to-target table covers all 1,139 observed field-level combinations.

The generated plots provide selected readable views, while the numerical tables preserve the results for the remaining fields.

## Independent Review

Liam reviewed `task_6.ipynb` against Issue #16.

The notebook covers the required categorical inventory, level-to-target statistics, recorded rare-level rule, and categorical encoding restriction.

Two methodology decisions remain:

1. Confirm that the team approves the rare-level threshold of fewer than 188 claims and its rationale.
2. Confirm that the selected plotting approach satisfies the issue's low- and high-cardinality visualization requirements, or expand the plotting coverage if needed.

The notebook and generated CSVs should also be verified against the final committed version before the issue is closed.

## Limitations

The individual meanings of the anonymous categorical predictors are unknown. Differences in target summaries cannot be assigned specific real-world explanations or interpreted as causal effects.

Target summaries for rare levels may be unstable because they are based on limited support.

The visualizations cover selected categorical fields rather than every predictor. Complete numerical results remain available for all observed category levels.

The rare-level threshold is an EDA display and support rule, not an automatic data-cleaning or feature-removal rule.

## Verification

- [x] Inventory covers all 116 categorical predictors.
- [x] Required cardinality and support statistics are present.
- [x] Rare-level threshold and rationale are documented.
- [x] Level-to-target tables cover all observed field-level combinations.
- [x] Low-cardinality plots and raw-unit summaries are present for selected fields.
- [x] High-cardinality plots and separate rare-tail summaries are present for selected fields.
- [x] Original categorical labels are preserved.
- [x] No arbitrary numeric encoding is used for categorical associations.
- [ ] Team confirms the rare-level threshold.
- [ ] Team confirms the plotting coverage or expands it.
- [ ] Final committed notebook and generated CSVs are verified.

**Reviewer:** Liam Stapley  
**Final review date:** Pending  
**Artifact commit:** Pending

## Completion

The numerical categorical analysis covers all 116 predictors.

Issue #16 can be closed after the rare-level threshold and plotting approach are confirmed, the final committed artifacts are verified, and the review record is updated.