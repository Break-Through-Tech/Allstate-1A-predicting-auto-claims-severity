# Issue #42: Preprocessing and Experiment Plan

**Status:** In progress — independent review complete; full-team approval pending

**Owner:** Mia Chavez

**Reviewer:** Ragib Nehal

**Artifact version:** `OCT-PLAN-001`; PR #53 working tree reviewed 2026-10-27; final commit pending

## Scope

Define the leakage-safe preprocessing rules and controlled experiment plan for October modeling. The issue covers categorical, rare, unseen, missing, and continuous-value handling; required constant baselines; two distinct model approaches; the experiment register; and the evidence needed for Gate 1 approval.

## Final artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Preprocessing plan | `notebooks/final-deliverables/October/Gate 1/preprocessing_plan.md` | Defines inputs, leakage boundaries, model-specific transformations, rare/unseen handling, and reviewer checks. |
| Experiment plan | `notebooks/final-deliverables/October/Gate 1/experiment_plan.md` | Defines baselines, candidate models, hypotheses, comparisons, stopping rules, and optional experiments. |
| Experiment register | `notebooks/final-deliverables/October/Gate 1/experiment_register.csv` | Records required baselines and planned required/optional experiments with configuration and evidence fields. |
| Gate 1 approval record | `notebooks/final-deliverables/October/Gate 1/gate1_approval_record.md` | Records frozen versions, artifact hashes, independent verification, deviations, team responses, and the final Gate decision. |

## Method

The plan uses modeling-data version `OCT-MD-001` and frozen split `OCT-SPLIT-001`, with 131,822 training claims, 28,248 validation claims, 28,248 protected test claims, seed 42, and five recorded folds inside training. Learned category vocabularies, frequencies, rare-level mappings, imputers, scalers, feature-selection rules, and model parameters are fitted on training data only and refitted inside each cross-validation fold.

The first controlled comparison includes the required training-mean constant, the training-median constant comparator, Ridge regression with one-hot categorical encoding, and histogram gradient boosting with pooled ordinal categorical codes and an explicit categorical mask. Target encoding and CatBoost are deferred; feature inclusion and exclusion experiments remain optional.

The independent review recalculated the source and partition-manifest hashes, checked partition and fold integrity, recomputed both baseline constants and validation MAEs, checked validation prediction coverage, and compared the plan and register fields for consistency.

## Results

- Source SHA-256: `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03`.
- Partition-manifest SHA-256: `de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b`.
- Training-mean constant: 3,038.840255; validation MAE: 1,962.918654.
- Training-median constant: 2,115.39; validation MAE: 1,805.086353.
- The split contains 131,822 training, 28,248 validation, and 28,248 test claims; each training claim has exactly one fold in 0–4.
- The approved artifact contents agree on `OCT-MD-001`, `OCT-SPLIT-001`, seed 42, the 132-claim rare-level threshold, the two required model approaches, and the protected-test boundary.

## Anomalies and limitations

The baseline receipt records a dirty Git working tree and library versions that differ from the split manifest. This is documented as a metadata-only reproducibility deviation because independent recalculation reproduced the constants and validation MAEs exactly from the frozen source and partition manifest.

September EDA used the full labeled dataset before the October split, so the validation partition is protected from model fitting but is not wholly unseen evidence. The internal random split also cannot establish future-period stability.

## Verification

- [x] Notebook rerun is not applicable; Issue #42 contains planning and register artifacts rather than an executable notebook.
- [x] Required outputs were generated and checked.
- [ ] Issue requirements have been completed; full-team approval, the final commit identifier, and owner assignments for E02 and O1-O4 remain outstanding. Ragib Nehal owns E01.
- [x] Calculated outputs match the recorded source and configuration.
- [x] Independent review completed.

**Reviewed by:** Ragib Nehal

**Review date:** 2026-10-27

**Review notes:** The independent review found five consistency issues: artifact location, baseline-deviation disposition, protected-test wording, missing frozen hashes, and incorrect section references. Each finding was corrected and rechecked. No artifact-correctness disagreement remains. The reviewer approves the current artifact contents; full-team approval is still required before Gate 1 passes.

## Completion

The Issue #42 artifact bundle is technically reviewed and approved by the independent reviewer. Ragib Nehal is assigned to E01 (Ridge regression). The issue remains open until the final commit is recorded, the remaining team members approve the plan, owners for E02 and O1-O4 are assigned, and the Gate 1 decision is marked.
