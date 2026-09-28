# Issue #18: Data-Quality Evidence

**Status:** Ready for review

**Owner(s):** Ragib Nehal

**Reviewer:** Pending

**Artifact version:** 1.0

## Scope

Reproduce the Gate 1 source profile from the frozen Allstate source and configuration; report the exact dataset dimensions, feature-role counts, identifier uniqueness, missingness, duplicate total, and observed numeric ranges; confirm that clean source data reduces repair work without removing the need to study level support, distributions, and target relationships; and resolve or document every EDA and workflow anomaly.

## Final artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Issue #18 notebook | [ragib_nehal_task_9.ipynb](../../../../notebooks/ragib-nehal/ragib_nehal_task_9.ipynb) | Reproducible source verification, profiling, EDA checks, anomaly triage, and evidence publication workflow. |
| Run manifest | [run_manifest.json](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/run_manifest.json) | Records the frozen source identity, runtime versions, artifact inventory, row counts, schemas, and SHA-256 hashes. |
| Reproduced source profile | [source_profile.csv](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/source_profile.csv) | Exact 132-field reproduction of the frozen Gate 1 profile. |
| Validation results | [validation_results.csv](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/validation_results.csv) | Consolidates 28 source, schema, role, profile, integrity, and blocking-resolution checks. |
| Numeric ranges | [numeric_ranges.csv](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/numeric_ranges.csv) | Preserves observed and frozen endpoints for the identifier, 14 continuous predictors, and target. |
| Categorical support | [categorical_support.csv](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/categorical_support.csv) | Records cardinality, rare-level support, affected rows, and dominant-level shares for 116 categorical predictors. |
| Distribution summary | [distribution_summary.csv](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/distribution_summary.csv) | Records summary statistics, skewness, IQR fences, and tail counts for 14 continuous predictors and `loss`. |
| Continuous target relationships | [continuous_target_relationships.csv](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/continuous_target_relationships.csv) | Records Pearson and Spearman relationships with raw and log-transformed loss, plus quantile-bin coverage. |
| Continuous quantile bins | [continuous_quantile_bins.csv](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/continuous_quantile_bins.csv) | Preserves target summaries for each realized continuous-predictor quantile bin. |
| Categorical target relationships | [categorical_target_relationships.csv](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/categorical_target_relationships.csv) | Summarizes supported and rare levels and field-level target differences for all categorical predictors. |
| Categorical level target relationships | [categorical_level_target_relationships.csv](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/categorical_level_target_relationships.csv) | Preserves loss and log-loss summaries for all 1,139 observed categorical levels. |
| Anomaly register | [anomaly_register.csv](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/anomaly_register.csv) | Preserves each non-blocking finding's affected count, severity, owner, status, evidence, handling rule, and likely impact. |

## Method

The notebook verifies `data/allstate_claims_data.csv` before loading it. The frozen source is 70,025,339 bytes with SHA-256 `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03`. It then checks the ordered 132-column schema and assigns feature roles from the frozen configuration rather than inferred data types.

Categorical source columns are loaded explicitly as `object` so the current pandas environment reproduces the Gate 1 `source_dtype` labels deterministically. This addresses an environment-level `str` versus `object` inference difference without changing source values.

The reproduced profile is compared with the frozen Gate 1 profile using exact ordered values and data types. Integrity checks cover identifier completeness and uniqueness, total cell-level missingness, and fully duplicated rows. Numeric endpoints are compared with the frozen profile, and all continuous predictors are checked against the configured `[0, 1]` domain.

EDA uses the following recorded rules:

- A categorical level is rare when it occurs in fewer than 188 rows, approximately 0.1% of the source.
- A categorical field is dominant when one level represents more than 99% of rows.
- Absolute skewness above 1 is flagged, and observations beyond 1.5 times the IQR are counted as distribution-tail evidence rather than presumed errors.
- Continuous target relationships use Pearson and Spearman correlations against both `loss` and `log1p(loss)`, plus up to ten quantile bins.
- Tied quantile boundaries are handled with `duplicates="drop"`; actual bin counts and complete row assignment are verified.
- Categorical target comparisons retain every observed level, while strong interpretations are limited to levels meeting the 188-row support threshold.

Evidence files are written through a temporary staging directory, read back for schema and row-count validation, published to the Gate 3 evidence directory, and checked against the SHA-256 hashes recorded in the run manifest.

## Results

The frozen profile was reproduced exactly. The verified source contains **188,318 rows and 132 columns**, with the following feature roles:

- 1 identifier
- 116 categorical predictors
- 14 continuous predictors
- 1 regression target

The identifier contains 188,318 unique values, with no missing or repeated identifiers. The dataset contains **0 missing cells** and **0 fully duplicated rows**. All 16 numeric fields—the identifier, 14 continuous predictors, and `loss`—match the frozen observed minimum and maximum values, and all continuous predictors remain within `[0, 1]`.

All 28 consolidated validation checks passed, including source identity, ordered schema, feature roles, exact profile reproduction, integrity, numeric ranges, distribution summaries, and continuous and categorical target-relationship coverage. No blocking anomaly remains unresolved.

The clean source substantially reduces data-repair work: no imputation, identifier repair, deduplication, or numeric-range correction is required. It does not make EDA complete. Level support, distribution shape, and target relationships still reveal sparse categories, near-constant predictors, skew and tail sensitivity, tied bin boundaries, and limits on supported categorical comparisons.

## Anomalies and limitations

Six non-blocking findings are preserved in the [anomaly register](../../../../notebooks/final-deliverables/September/Gate%203/data_quality_evidence/anomaly_register.csv):

1. **Rare categorical levels — medium severity; feature engineering/modeling owner.** There are 523 levels below the 188-row threshold across 39 fields, affecting 14,721 distinct source rows. Source values are retained; any pooling or encoding must be fitted on training folds and must handle unseen levels. Sparse groups may otherwise produce unstable target summaries and encoded effects.
2. **Dominant categorical levels — low severity; feature engineering/modeling owner.** Thirty-one fields contain a level representing more than 99% of rows. The fields are retained, but incremental value must be assessed during validation and minority-level results must not drive conclusions. Near-constant predictors may add little signal and make minority comparisons unstable.
3. **Strong numeric skew — medium severity; EDA/modeling owner.** Two fields exceed absolute skewness 1: `cont9` at 1.072429 and `loss` at 3.794958. Raw values are preserved; robust summaries and raw-versus-`log1p(loss)` relationships are compared because means, Pearson correlations, and fitted objectives may be upper-tail sensitive.
4. **IQR tail observations — medium severity; EDA/modeling owner.** There are 27,547 row-field observations outside the 1.5-times-IQR fences across `cont7`, `cont9`, `cont10`, and `loss`. These observations are treated as distribution-tail evidence rather than errors; deletion or clipping requires later model-validation evidence. Tail values may affect averages, correlations, and fitted models.
5. **Reduced quantile bins — low severity; EDA workflow owner; resolved.** Tied edges reduce `cont2` to 9 bins and `cont5` to 8 bins instead of the requested 10. The workflow drops duplicate edges, records actual bin counts, and confirms complete row assignment. Comparison granularity is reduced, but no observations are lost.
6. **Insufficient supported categorical comparisons — medium severity; EDA/modeling owner.** Nine fields have only one level meeting the 188-row support threshold. All level summaries are retained, but no strong target-relationship claim is made for those fields because apparent differences depend on sparse groups.

The pandas `str` versus `object` inference difference is documented in the notebook as an environment-compatibility note, not a data anomaly. Loading the categorical columns explicitly as `object` restores deterministic reproduction without changing values, roles, missingness, uniqueness, or numeric ranges.

The predictors remain anonymous, so the analysis can describe statistical relationships but cannot assign business meaning or causal interpretation to individual `cat*` and `cont*` fields. This work establishes data-quality and EDA evidence; it does not establish model performance or production readiness.

## Verification

- [ ] Final notebook runs from a fresh kernel.
- [x] Required outputs were generated and checked.
- [x] Issue requirements have been completed.
- [x] Calculated outputs match the recorded source and configuration.
- [ ] Independent review completed, if required.

**Reviewed by:** Pending

**Review date:** Pending

**Review notes:** Awaiting an independent fresh-kernel run and reviewer sign-off.

## Completion

The Issue #18 analysis and evidence-generation work is complete and ready for review. The frozen Gate 1 profile is reproduced, every requested exact result is reported, the continuing need for level-support, distribution, and target-relationship analysis is demonstrated, all blocking checks pass, and every identified non-blocking finding is preserved with its required ownership and handling metadata.

Independent fresh-kernel execution and reviewer approval remain outstanding before the artifact bundle can be marked approved.
