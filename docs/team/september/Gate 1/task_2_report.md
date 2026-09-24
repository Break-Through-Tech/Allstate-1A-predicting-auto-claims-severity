# Issue #8: Schema and Integrity

**Status:** Ready for verification

**Owner(s):** Gate 1 team

**Reviewer:** Pending

## Scope

Validate the source schema, identifier integrity, missingness, duplicate rows, continuous predictor ranges, regression target, and categorical representation.

## Final artifacts

| Artifact | Location |
|---|---|
| Validation notebook | `notebooks/final-deliverables/September/Gate 1/task_2.ipynb` |
| Source profile | `notebooks/final-deliverables/September/Gate 1/profile.csv` |
| Validation results | `notebooks/final-deliverables/September/Gate 1/validation_results.csv` |
| Anomaly register | `notebooks/final-deliverables/September/Gate 1/anomaly_register.csv` |

## Method

Task 2 validates the authoritative source before generating the column profile and validation evidence.

Categorical fields are treated as unordered labels. Continuous fields are checked for numeric values within the documented 0-to-1 range. The regression target is checked for numeric, finite, and strictly positive values.

Calculated outputs are generated programmatically. Failed validation prevents publication of a new profile or validation-results file.

## Results

The completed workflow must establish:

- 188,318 rows and 132 columns.
- Exact documented header and column-role counts.
- Zero missing IDs and 188,318 unique IDs.
- Zero exact duplicate rows and zero missing cells.
- All continuous predictor values within the documented 0-to-1 range.
- Numeric, finite, strictly positive `loss` values.
- All 116 categorical predictors represented as unordered labels.
- One profile entry for each of the 132 source fields.

**Observed validation results:** See `validation_results.csv`.

**Clean workflow run:** Pending confirmation.

## Anomalies and limitations

The official anomaly register records confirmed anomalies and their handling decisions.

Successful validation checks are recorded in `validation_results.csv`, not as resolved anomalies.

**Confirmed anomalies:** Pending review of the current register and workflow results.

## Verification

- [ ] Clean workflow run completed.
- [ ] Source identity independently verified.
- [ ] Row, column, header, and role counts verified.
- [ ] Identifier uniqueness verified.
- [ ] Missingness and duplicate totals verified.
- [ ] Continuous ranges verified.
- [ ] Published artifacts checked for integrity.
- [ ] Anomalies and handling decisions reviewed.

**Reviewed by:** Pending

**Review date:** Pending

**Artifact version / commit:** Pending