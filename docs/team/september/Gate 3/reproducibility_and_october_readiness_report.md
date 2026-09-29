# Issue #14: Reproducibility and October-Readiness Evidence

**Status:** Automated reproducibility complete; final team sign-off pending  
**Gate:** 3

## Scope

Verify that the final September workflow can be reproduced from a clean committed project revision and record the exact source, code, runtime, analysis settings, Workflow Run ID, and Artifact Bundle IDs used for Gate 3.

The task also freezes the October evaluation plan before model tuning begins.

## Artifacts

| Artifact | Location |
|---|---|
| Reproducibility notebook | `notebooks/final-deliverables/September/Gate 3/reproducibility-and-october-readiness/reproducibility_and_october_readiness.ipynb` |
| Workflow manifest | `notebooks/final-deliverables/September/Gate 3/reproducibility-and-october-readiness/workflow_run_manifest.json` |
| Artifact manifest | `notebooks/final-deliverables/September/Gate 3/reproducibility-and-october-readiness/artifact_manifest.csv` |
| Reproducibility checks | `notebooks/final-deliverables/September/Gate 3/reproducibility-and-october-readiness/reproducibility_checks.csv` |
| Dependency versions | `notebooks/final-deliverables/September/Gate 3/reproducibility-and-october-readiness/dependency_versions.csv` |
| Random-seed inventory | `notebooks/final-deliverables/September/Gate 3/reproducibility-and-october-readiness/random_seed_inventory.csv` |
| Analysis settings | `notebooks/final-deliverables/September/Gate 3/reproducibility-and-october-readiness/analysis_settings.json` |
| October evaluation plan | `notebooks/final-deliverables/September/Gate 3/reproducibility-and-october-readiness/october_evaluation_plan.md` |
| Gate 3 sign-off | `notebooks/final-deliverables/September/Gate 3/reproducibility-and-october-readiness/gate3_signoff.csv` |

## Reproducibility Result

The workflow was rerun from a clean committed repository state in VS Code/Jupyter.

All automated reproducibility checks passed:

- clean committed start;
- all final workflow notebooks executed successfully;
- all artifact comparisons passed;
- source hash recorded;
- Git revision recorded;
- dependency versions recorded;
- random-seed inventory recorded;
- analysis settings recorded;
- Workflow Run ID recorded;
- Artifact Bundle IDs recorded; and
- October evaluation plan created.

Discrete evidence reproduced exactly, and displayed numerical evidence reproduced within the recorded precision.

## Recorded Reproducibility Metadata

The workflow records:

- source-data SHA-256;
- Git branch and commit;
- Python/runtime information;
- dependency versions;
- random-seed declarations;
- target histogram settings;
- categorical rare-level threshold;
- continuous quantile-bin rule;
- numerical comparison tolerance;
- Workflow Run ID; and
- Gate 1, Gate 2, and Gate 3 Artifact Bundle IDs.

## October Evaluation Plan

October modeling will use a train/validation split created before learned preprocessing.

All learned preprocessing will be fitted using training data only, including:

- categorical encoding;
- rare-level handling;
- scaling or transformations;
- feature-selection thresholds; and
- data-dependent binning.

Validation data will remain untouched during fitting.

Model evaluation will use MAE in original `loss` units.

The first October baseline comparison will include:

- the Challenge Advisor's requested mean-constant baseline; and
- a median-constant comparator.

Both constants will be estimated using the training partition only.

Full-dataset descriptive constant MAE will not be presented as held-out model performance.

Previously unseen validation categories will use an explicit unknown/unseen representation. Validation frequencies will not be used to modify the training encoding map.

## Runtime Note

Issue #14 specifically requests that the clean workflow be rerun in Google Colab.

The complete workflow has instead been reproduced successfully in a clean VS Code/Jupyter environment using the final committed project files.

A Colab rerun may still be completed if required. However, reproducing the full repository environment in Colab would require additional setup that does not change the underlying reproducibility checks already completed locally.

Before closing the issue without a Colab rerun, the team should confirm that the clean VS Code/Jupyter execution is acceptable for this requirement.

This runtime difference should be documented as an approved deviation rather than treated as if a Colab run occurred.

## Human Review Still Required

Two notebook cells remain to be completed:

### Code Cell 10: Team Approval and Final Gate 3 Sign-Off

Update `gate3_signoff.csv` with the actual:

- team approval decision;
- approver(s);
- approval date;
- independent reviewer;
- review date;
- disagreements;
- limitations; and
- review notes.

If the team agrees that the VS Code/Jupyter run is sufficient instead of Colab, record that decision here.

### Code Cell 11: Final Verification

Rerun this cell after the sign-off record is updated.

The expected final result is:

- `Automatic reproducibility checks: PASS`
- `Team sign-off complete: True`

The Colab status should only be marked complete if an actual Colab run occurs. Otherwise, the approved runtime deviation should remain documented in the sign-off record.

## Verification

- [x] Clean committed project revision recorded.
- [x] September workflow rerun successfully in VS Code/Jupyter.
- [x] Discrete evidence reproduced exactly.
- [x] Numerical evidence reproduced within recorded precision.
- [x] Source hash and Git revision recorded.
- [x] Dependency and runtime versions recorded.
- [x] Random-seed declarations recorded.
- [x] Plot, binning, and support settings recorded.
- [x] Workflow Run ID recorded.
- [x] Artifact Bundle IDs recorded.
- [x] October evaluation plan drafted.
- [x] Mean-constant and median-constant training-only baselines specified.
- [x] Full-data descriptive baseline performance explicitly prohibited.
- [x] Rare and unseen categorical handling documented without validation leakage.
- [ ] Team approval and independent review recorded in Code Cell 10.
- [ ] Code Cell 11 rerun after final sign-off.
- [ ] Google Colab rerun completed, or the team explicitly approves and documents the VS Code/Jupyter runtime deviation.

## Completion

All automated reproducibility and October-readiness checks passed.

Issue #14 is ready for final human sign-off. The remaining work is to update Code Cell 10, rerun Code Cell 11, and resolve whether the explicit Google Colab requirement requires a second run or can be satisfied through an approved runtime deviation.