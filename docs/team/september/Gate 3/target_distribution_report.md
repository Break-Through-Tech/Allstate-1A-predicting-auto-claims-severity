# Issue #19: Target-Distribution Evidence

**Status:** Ready for review

**Owner(s):** Ragib Nehal

**Reviewer:** Pending

**Artifact version:** 1.0

## Scope

Reproduce and explain the required target-distribution verification values from the frozen Allstate claims source; explain the long right tail and the different purposes of raw and transformed views; report high-loss observations as part of the severity distribution; and keep every headline business statistic in original `loss` units.

## Final artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Issue #19 notebook | [ragib_nehal_task_10.ipynb](../../../../notebooks/ragib-nehal/ragib_nehal_task_10.ipynb) | Reproducible source verification, target analysis, interpretation, artifact generation, and validation workflow. |
| Target-distribution summary | [target_distribution_summary.csv](../../../../notebooks/final-deliverables/September/Gate%203/target_distribution_evidence/target_distribution_summary.csv) | Records the original-unit summary statistics, percentiles, skewness, IQR threshold, high-loss count and share, and raw-histogram clipping disclosure. |
| Target-distribution views | [target_distribution_views.png](../../../../notebooks/final-deliverables/September/Gate%203/target_distribution_evidence/target_distribution_views.png) | Combines the p99-limited raw histogram, full-range `log1p(loss)` histogram, and full-range raw boxplot. |

## Method

The notebook locates `data/allstate_claims_data.csv` without relying on a personal absolute path. Before analysis, it verifies the frozen source size of 70,025,339 bytes, SHA-256 digest `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03`, expected shape of 188,318 rows by 132 columns, and ordered schema. It also confirms that `loss` contains no missing, non-finite, or non-positive values.

The target summary reports count, mean, median, standard deviation, minimum, maximum, raw skewness, and the 25th, 50th, 75th, 90th, 95th, and 99th percentiles. High-loss observations use the previously established 1.5-times-IQR rule. Values above the upper fence are counted and retained as severity-distribution evidence rather than presumed errors.

The combined figure uses 100 bins for each histogram and the full dataset without sampling. The raw histogram displays values through the 99th percentile, $13,981.20, so the body of the distribution remains readable; 1,884 observations, approximately 1.000% of rows, lie beyond that visual limit. The `log1p(loss)` histogram uses the full transformed range, and the raw boxplot preserves the complete original-unit range.

`log1p(loss)` is used only for visualization. It does not replace the original target, original-unit business reporting, or future MAE calculation.

## Results

The Issue #19 notebook reproduced the required local verification values, allowing only normal rounding differences:

| Statistic | Observed value |
|---|---:|
| Count | 188,318 |
| Mean `loss` | $3,037.34 |
| Median `loss` | $2,115.57 |
| Standard deviation | $2,904.09 |
| Minimum | $0.67 |
| 25th percentile | $1,204.46 |
| 50th percentile | $2,115.57 |
| 75th percentile | $3,864.05 |
| 90th percentile | $6,401.74 |
| 95th percentile | $8,508.54 |
| 99th percentile | $13,981.20 |
| Maximum | $121,012.25 |
| Raw skewness | 3.795 |

The mean exceeds the median, raw skewness is strongly positive, and the maximum is far above the 95th percentile. In plain language, most claims have lower or moderate loss amounts, while a comparatively small number of severe claims extend far into higher values and form a long right tail.

The raw views preserve the financial magnitude of the target and show how far severe losses extend. The transformed view compresses large values so the shape and concentration of the complete distribution are easier to see. These views answer different questions and do not change the underlying records.

The 1.5-times-IQR upper fence is $7,853.42. There are 11,554 observations above this threshold, representing 6.135% of the 188,318 claims. These observations remain part of the severity distribution.

## Anomalies and limitations

The long upper tail is a non-blocking distribution finding, not evidence of invalid data. No high-loss observation is removed, clipped, replaced, or classified as erroneous because this analysis found no independent evidence that any target value is invalid. If a future review identifies a specific validity concern, the affected row must be recorded in the anomaly register and preserved until the concern is resolved.

The raw histogram limits its displayed x-axis to the 99th percentile and therefore does not show the uppermost 1.000% of observations. This visual restriction is disclosed in the figure and summary CSV; it does not affect the calculations, the full-range transformed histogram, or the full-range raw boxplot.

The transformed histogram is not directly interpretable in original claim-loss units. Headline statistics therefore remain on the raw `loss` scale. This work describes the observed target distribution; it does not establish model performance, determine individual claim reserves, or justify a future target transformation without held-out MAE evidence.

## Verification

- [x] Final notebook runs from a fresh kernel.
- [x] Required outputs were generated and checked.
- [x] Issue requirements have been completed.
- [x] Calculated outputs match the recorded source and configuration.
- [ ] Independent review completed, if required.

**Reviewed by:** Pending

**Review date:** Pending

**Review notes:** Independent review has not yet been completed.

## Completion

The Issue #19 target-distribution analysis and evidence-generation work is complete and ready for review. The frozen source identity and target validity were verified, every required statistic was reproduced, the long right tail and high-loss observations were documented without altering the source, and the raw and transformed views preserve their distinct purposes. Independent review remains outstanding before the artifact bundle can be marked approved.
