# Issue #46 Feature Experiments and Review Implementation Plan

> **For agentic workers:** Use `superpowers:executing-plans` and `superpowers:test-driven-development` task by task.

**Goal:** Produce a self-contained, author-verified draft bundle for issue #46 without changing the Gate 1 register or promoting artifacts before independent review.

**Architecture:** One executed notebook reproduces the selected full-feature HGB model, runs the O1 near-constant-field exclusion, and exports row-level evidence and diagnostics. A standalone verifier independently recalculates the frozen-data, prediction, metric, receipt, and pending-review contracts. All new tracked files remain under this directory.

**Tech stack:** Python 3.12, pandas, NumPy, scikit-learn 1.6.1, Jupyter nbformat/nbclient, unittest-style assertions.

**Spec:** GitHub issue #46 plus the user-approved plan in this chat.

## Global Constraints

- Use `OCT-MD-001`, `OCT-SPLIT-001`, seed 42, and the five frozen training folds.
- Never fit, predict, summarize, or score the protected test partition.
- Fit categorical pooling and every learned transformation inside each training fold.
- Select O1 only if both mean CV MAE and validation MAE improve by at least 1% versus the same-run full E02 reproduction.
- Treat predictors as anonymous; do not assign business meaning or causal effects.
- Keep every issue #46 file in this draft directory until review.
- Do not update the Gate 1 register without explicit user approval after Mia Chavez's review.

## Review Focus

- Test IDs must never enter model inputs, predictions, or diagnostics.
- The 31-field exclusion must be learned from training frequencies only.
- Both pipelines must refit preprocessing inside every frozen CV fold.
- Row-level predictions must reproduce every recorded validation MAE and severity support count.
- Approval records must remain pending before real reviewer and team decisions.

---

### Task 1: Independent verifier contract

**Files:**
- Create: `verify_feature_experiments_review.py`

- [ ] Write the verifier first so it fails against the absent evidence files.
- [ ] Confirm the failure names the missing bundle artifacts.
- [ ] Add checks for frozen hashes, feature decisions, predictions, diagnostics, receipt provenance, notebook execution, and pending review status.
- [ ] Keep manifest refresh behind an explicit `--refresh-manifest` option.
- [ ] Commit the verifier and plan.

### Task 2: Executable experiment and evidence exports

**Files:**
- Create: `error_analysis.ipynb`
- Create on execution: CSV and JSON evidence named in the approved plan.

- [ ] Create the notebook with the frozen split and training-only O1 derivation.
- [ ] Run it from top to bottom in the pinned environment.
- [ ] Confirm full E02 and O1 CV/validation metrics, decision rule, prediction coverage, and diagnostics.
- [ ] Refresh the artifact manifest and make the verifier pass on numerical evidence.
- [ ] Commit the executed notebook and generated evidence.

### Task 3: Review and handoff documentation

**Files:**
- Create: `november_handoff.md`
- Create: `model_review.md`
- Create: `review_checklist.md`
- Create: `gate3_approval_record.md`
- Create: `reviewer_reproduction/.gitkeep`

- [ ] Populate the author findings, O1 decision, O2-O4 deferrals, limitations, artifact versions, and reviewer instructions.
- [ ] Leave Mia's review and every team approval pending.
- [ ] Refresh the manifest and verify the complete draft bundle.
- [ ] Commit the documentation.

### Task 4: Author verification checkpoint

- [ ] Execute the notebook once more from a fresh kernel.
- [ ] Run the standalone verifier and the relevant repository test suite.
- [ ] Run `git diff --check` and inspect every created or modified file.
- [ ] Remove caches and temporary files created during this task.
- [ ] Stop before reviewer handoff, Gate 1 register changes, promotion, or issue closeout.
