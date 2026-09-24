# Issue #15: Project-Specific Data Dictionary

**Status:** Approved

**Owner:** Liam Stapley

**Reviewer:** Ragib Nehal

**Dictionary version:** 1.1.0

## Scope

Create and maintain one shared, versioned data dictionary covering all 132 delivered fields and the derived fields introduced during September EDA.

## Final Artifacts

| Artifact | Location |
|---|---|
| Data dictionary | `notebooks/final-deliverables/September/Gate 2/data_dictionary.csv` |
| Initial dictionary notebook | `notebooks/liam-stapley/data_dictionary.ipynb` |
| Dictionary update notebook | `notebooks/liam-stapley/update_data_dictionary.ipynb` |
| Derived-field registry | `notebooks/final-deliverables/September/Gate 2/continuous_analysis_evidence/derived_field_registry.csv` |
| Bin inventory | `notebooks/final-deliverables/September/Gate 2/continuous_analysis_evidence/bin_inventory.csv` |
| Analysis contract | `notebooks/final-deliverables/September/Gate 2/Plain_language_analysis_contract.md` |

## Method

The initial dictionary was generated from the authoritative source dataset, the Gate 1 column profile, and the project's analysis contract.

Source-field metadata includes exact field names, approved roles, observed data types, ranges or category levels, unique-value counts, missingness, known units or scales, documented meanings, quality limitations, and approved September handling.

The update notebook reads the existing dictionary and the continuous-analysis evidence. It preserves source-field entries, updates existing derived-field definitions, and adds newly registered fields.

Calculated values are generated from the recorded source and analysis evidence rather than manually entered.

## Results

Dictionary version 1.1.0 covers 147 fields:

| Field type | Count |
|---|---:|
| Identifier | 1 |
| Anonymous nominal categorical predictors | 116 |
| Anonymous continuous predictors | 14 |
| Regression target | 1 |
| Derived target: `log1p_loss` | 1 |
| Continuous quantile-bin fields | 14 |
| **Total** | **147** |

The dictionary records `id` as an identifier used for integrity checks only, excluding it from distribution and target-effect interpretation.

All `cat*` fields are documented as anonymous nominal categorical predictors. All `cont*` fields are documented as anonymous continuous predictors on the delivered 0-to-1 scale. Their individual meanings, original units, and transformations remain unknown.

`loss` is documented as the positive continuous regression target representing the final paid claim amount in dollars.

The derived-field entries record stable names, purposes, inputs, exact derivations, allowed values, versions, and owners. The quantile-bin definitions use the recorded continuous-analysis method and actual bin boundaries rather than assuming that every predictor produces 10 bins.

## Limitations and Handling

The anonymous predictors have no documented mappings to real-world variables. Their meanings remain unresolved rather than being inferred from examples in the project overview.

Quantile-bin boundaries depend on the observed source distribution. Repeated predictor values may prevent the requested 10 distinct bins.

The dictionary follows the analysis contract's intended non-uses. September EDA does not establish causation, determine individual reserves, prove production readiness, or authorize automated claims decisions.

Newly created fields must be documented in a subsequent dictionary version before being included in the shared field inventory.

## Verification

- [x] The dictionary artifacts and update-notebook validation results were reviewed.
- [x] All 132 source fields are present exactly once.
- [x] All 15 registered derived fields are present exactly once.
- [x] Required metadata is populated for every field.
- [x] Quantile-bin definitions match the continuous-analysis evidence.
- [x] Anonymous predictor meanings remain marked as unknown.
- [x] Final CSV contains 147 unique fields and dictionary version 1.1.0.
- [x] A teammate has reviewed the published dictionary.

**Reviewer:** Ragib Nehal

**Review date:** 2026-09-24

**Review notes:** Approved. The published dictionary contains 147 unique fields: all 132 source fields and all 15 registered derived fields (`log1p_loss` and `cont1_quantile_bin` through `cont14_quantile_bin`). The source inventory exactly matches the dataset header, and the derived fields match the derived-field registry with complete required metadata and consistent quantile-bin definitions. The two-notebook workflow is acceptable: the initial notebook creates the base dictionary, and the update notebook publishes the updated copy.

## Completion

The updated dictionary has been reviewed and approved. The verification checklist is complete, and Issue #15 can be closed.
