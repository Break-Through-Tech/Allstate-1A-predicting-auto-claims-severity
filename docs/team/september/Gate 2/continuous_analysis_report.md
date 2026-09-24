# Issue #17: Continuous-Analysis Method

**Status:** Independent review approved

**Owner(s):** Liam Stapley, Ragib Nehal

**Reviewer:** Ragib Nehal

**Method version:** 1.0.0

## Scope

Analyze the distributions, target associations, and relationships among all 14 continuous predictors (`cont1` through `cont14`).

The analysis uses the authoritative source dataset and follows the approved September analysis contract.

## Final Artifacts

| Artifact | Location |
|---|---|
| Continuous-analysis notebook | `notebooks/liam-stapley/continuous_analysis.ipynb` |
| Generated analysis evidence | `notebooks/final-deliverables/September/Gate 2/continuous_analysis_evidence/` |
| Data dictionary | `notebooks/final-deliverables/September/Gate 2/data_dictionary.csv` |
| Analysis contract | `notebooks/final-deliverables/September/Gate 2/Plain_language_analysis_contract.md` |

The generated evidence includes the continuous-field inventory, target correlations, predictor correlations, strongest predictor pairs, quantile-bin inventory, bin-level summaries, derived-field registry, and analysis figures.

## Method

### 1. Continuous-Field Inventory

All 14 continuous predictors are analyzed using their delivered 0-to-1 scale.

For each field, the notebook calculates descriptive statistics, observed minimum and maximum, unique-value count, and missingness.

A histogram and boxplot are generated for every continuous predictor.

### 2. Target Correlations

Pearson and Spearman correlations are calculated between each continuous predictor and both:

- Original `loss`
- `log1p(loss)`

This produces 56 target-correlation coefficients.

All coefficients are treated as marginal associations. They are not interpreted as feature-importance scores or evidence of causation.

Original `loss` remains the reporting and future model-evaluation scale.

### 3. Quantile Binning

Each continuous predictor is quantile-binned using a default of 10 requested bins.

The method uses `pd.qcut()` with `duplicates="drop"` when repeated values prevent 10 distinct bin boundaries.

The actual bin count and calculated boundaries are recorded for each predictor. Artificial boundaries are not introduced to force 10 bins.

For every observed bin, the notebook calculates:

- Support (number of claims)
- Mean raw `loss`
- Median raw `loss`
- First and third quartiles of raw `loss`
- Raw `loss` interquartile range (Q3 − Q1)

Support, mean loss, and median loss are plotted together for each continuous predictor.

### 4. Predictor-Predictor Correlations

A Pearson correlation matrix is calculated for all 14 continuous predictors.

The notebook generates an annotated correlation heatmap and a table of the strongest absolute predictor-predictor correlations.

Each unique predictor pair is recorded once, excluding self-correlations.

### 5. Feature Handling

No continuous predictor is removed during September solely because of weak target correlation or strong predictor-predictor correlation.

All 14 continuous predictors are retained for further analysis.

## Results

| Output | Coverage |
|---|---:|
| Continuous predictors analyzed | 14 |
| Histograms | 14 |
| Boxplots | 14 |
| Target-correlation coefficients | 56 |
| Unique predictor-predictor pairs | 91 |
| Quantile-bin inventories | 14 |
| Bin-level support and target-pattern plots | 14 |
| Annotated Pearson correlation heatmaps | 1 |

The generated continuous-field inventory records the distribution summaries, ranges, and unique-value counts for all 14 predictors.

The target-correlation table contains Pearson and Spearman coefficients against original and log-transformed loss.

The bin inventory records the requested and actual bin counts and boundaries. The bin-level summary contains support, mean loss, median loss, and loss IQR for each observed bin.

The strongest-pairs table and annotated heatmap document the relationships among continuous predictors.

### Quantile-Bin Results

The recorded bin inventory indicates that `cont2` produced 9 bins and `cont5` produced 8 bins. The other 12 continuous predictors produced 10 bins.

These reduced bin counts result from repeated values preventing the requested number of distinct quantile boundaries.

The actual counts and boundaries are preserved in the generated evidence and derived-field registry.

## Limitations

The original meanings, units, and transformations of the continuous predictors are unknown. Their observed relationships cannot be assigned specific real-world interpretations.

Pearson and Spearman correlations describe marginal associations and do not establish causation or independent feature importance.

Quantile-bin boundaries are specific to the observed dataset. Repeated values can result in unequal bin support and fewer than 10 bins.

Mean loss may be affected by high-cost claims, so median loss, IQR, and bin support are reported alongside it.

The analysis is exploratory and does not determine individual claim reserves or establish production readiness.

## Verification

- [x] Final notebook runs successfully from a fresh kernel.
- [x] All 14 continuous predictors are included in the inventory.
- [x] Every predictor has a histogram and boxplot.
- [x] All 56 target-correlation coefficients are generated.
- [x] Quantile-bin counts and boundaries match the saved evidence.
- [x] Every observed bin has the required support and target statistics.
- [x] Support and mean/median loss plots are generated for all 14 predictors.
- [x] Annotated Pearson heatmap and strongest-pairs table are generated.
- [x] No continuous predictors were removed based solely on correlations.
- [x] Generated evidence and derived-field definitions are consistent with the data dictionary.
- [x] Independent review completed.

**Reviewer:** Ragib Nehal

**Review date:** 2026-09-23

**Artifact version:** Notebook SHA-256 `dfd2d8d959e60ff9109ddb1e45715852b3398f3db9da35f4c37f7f5f219a1cc1`

**Review notes:** Approved. The notebook was rerun from a fresh kernel in an isolated sandbox using the authoritative source file (SHA-256 `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03`). All nine code cells completed without errors, all notebook validation messages passed, and the regenerated bundle contained the expected 37 manifest entries and 38 total files. Structural, numerical, manifest-integrity, bin-coverage, and visual checks passed. The regenerated CSV and JSON content matched the published evidence semantically, with maximum floating-point drift of `1.36e-12`. File hashes were not byte-identical because the published bundle used Windows, Python 3.12.8, and Matplotlib 3.9.2, while the sandbox used macOS, Python 3.14.7, and Matplotlib 3.11.2; observed differences were limited to line endings, insignificant floating-point serialization, and plot rendering. All 29 figures displayed the same analytical content and were readable. No original notebook or published artifact was modified during review.

## Completion

The continuous-analysis notebook and generated evidence cover the required methods in Issue #17.

The independent review is complete and approved. Once this reviewed report is merged, Issue #17 can be closed.
