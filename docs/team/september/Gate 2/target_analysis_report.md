# Issue #10: Target-Analysis Method

**Status:** Ready for final verification

**Authors:** Mia Chavez and Junaid Pathan

**Reviewer:** Liam Stapley

**Review result:** Minor changes requested

## Scope

Establish the target-analysis methodology for September EDA, including the required descriptive statistics, visualizations, plot settings, and use of the original target scale.

## Final Artifacts

| Artifact | Location |
|---|---|
| Target-analysis notebook | `notebooks/final-deliverables/September/Gate 2/target_analysis.ipynb` |
| Analysis contract | `notebooks/final-deliverables/September/Gate 2/Plain_language_analysis_contract.md` |

## Method

The notebook analyzes `loss` using the authoritative source dataset, `data/allstate_claims_data.csv`.

It generates the required descriptive statistics and percentiles, a raw loss histogram, a `log1p(loss)` histogram, a raw loss boxplot, and a percentile table in original loss units.

Both histograms use 100 bins. The raw histogram displays values through the 99th percentile for readability, while the full dataset is retained for descriptive statistics.

No sampling is used.

The log-transformed target is used for visualization only. Original `loss` remains the reporting and future model-evaluation scale.

## Results

The saved notebook output reports:

| Statistic | Observed value |
|---|---:|
| Count | 188,318 |
| Mean | $3,037.34 |
| Median | $2,115.57 |
| Standard deviation | $2,904.09 |
| Minimum | $0.67 |
| Maximum | $121,012.25 |
| Skewness | 3.795 |
| 25th percentile | $1,204.46 |
| 50th percentile | $2,115.57 |
| 75th percentile | $3,864.05 |
| 90th percentile | $6,401.74 |
| 95th percentile | $8,508.54 |
| 99th percentile | $13,981.20 |

The target distribution is right-skewed, with a mean exceeding the median and a long upper tail.

The raw histogram is restricted to values through the 99th percentile for readability. Approximately 1.00% of observations fall outside its displayed range. The raw boxplot retains the full observed range.

## Independent Review

Liam reviewed the target-analysis notebook against the requirements in Issue #10.

The notebook includes all required summary statistics, target views, and reporting conventions.

The following improvements were identified:

1. Add explicit source identity and target-validity assertions before generating the analysis outputs.
2. Clarify that the raw histogram's 99th-percentile restriction affects only the displayed visualization, not the underlying dataset or calculated statistics.

These changes do not require replacing the existing analysis methodology.

## Limitations

The raw histogram does not display the uppermost 1% of observed losses. This restriction is disclosed and does not apply to the full-distribution summary statistics or raw boxplot.

The log-transformed visualization is not a replacement for original-dollar reporting or MAE evaluation.

The target analysis does not establish model performance or determine individual reserves.

## Verification

- [x] Required target summary and percentiles reviewed.
- [x] Required target visualizations reviewed.
- [x] Plot settings and upper-tail restriction reviewed.
- [x] Original-loss reporting convention confirmed.
- [ ] Source identity assertions added and verified.
- [ ] Final notebook rerun after changes.

**Reviewer:** Liam Stapley

**Review status:** Minor changes requested

**Final review date:** Pending

**Artifact commit:** Pending

## Completion

The target-analysis method covers the requirements in Issue #10.

The issue can be closed once the requested source-validation and documentation changes are made and the final notebook is verified.