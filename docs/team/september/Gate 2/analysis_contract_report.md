# Issue #9: Plain-Language Analysis Contract

**Status:** Complete

**Author:** Mia Chavez

**Reviewer:** Liam Stapley

**Artifact version:** 1.0

## Scope

Establish the project's objective, unit of analysis, target variable, success metric, data scope, field limitations, and intended non-uses for September EDA.

## Final Artifact

[Plain-Language Analysis Contract](../../../../notebooks/final-deliverables/September/Gate%202/Plain_language_analysis_contract.md)

## Results

The analysis contract establishes the following:

- **Project objective:** Estimate final paid claim amounts early enough to support reserve planning and understand factors associated with higher claim severity.
- **Unit of analysis:** One auto insurance claim per row.
- **Target:** `loss`, representing the final paid claim amount in dollars. Original `loss` units remain the reporting and evaluation scale.
- **Success metric:** Mean Absolute Error (MAE), measuring average absolute prediction error in dollars.
- **Data scope:** Closed claims without payment are excluded according to the project overview. The team verifies that the delivered dataset contains positive `loss` values without inferring individual inclusion reasons.
- **Unknown predictors:** Individual `cat*` and `cont*` field meanings are unknown. Examples in the project overview are not documented field mappings.
- **Intended non-uses:** September EDA does not establish causation, determine individual reserves, prove production readiness, or authorize automated claims decisions.

## Review

Liam reviewed Mia's analysis contract against the requirements in Issue #9.

All required topics are addressed. The contract clearly distinguishes the project's intended use from conclusions that September EDA cannot support.

**Review result:** Approved.

## Anomalies and Limitations

No discrepancies were identified during the contract review.

The meanings of individual anonymous predictors remain undocumented. This limitation is explicitly recorded in the contract and will be preserved in the data dictionary.

The contract defines the project's scope and methods; it does not establish model performance or validate the dataset by itself.

## Completion

All requirements in Issue #9 are addressed in the final analysis contract.

The contract has been reviewed and approved for use in the September EDA workflow.