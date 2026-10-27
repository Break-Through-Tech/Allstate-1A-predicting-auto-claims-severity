# Issue #44 Leakage-Safe Model Inputs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate reusable, leakage-safe training pipelines for the approved Ridge and histogram-gradient-boosting model families, without running the controlled model comparison from Issue #45.

**Architecture:** A reusable Python module will own frozen-data loading, partition protection, category auditing, preprocessing factories, and artifact generation. One executed notebook will call that module to create the review evidence. A separate verification script and behavior-focused tests will independently check the saved artifacts and pipeline boundaries.

**Tech Stack:** Python, pandas, NumPy, scikit-learn 1.6.1, nbformat/nbclient, unittest.

**Spec:** `notebooks/final-deliverables/October/Gate 1/preprocessing_plan.md`

## Global Constraints

- Keep all Issue #44 notebooks and deliverables under `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/`; reusable-module tests belong in `tests/test_leakage_safe_model_inputs.py` per repository guidelines.
- Work on the current `ragib-nehal` branch; do not create a worktree.
- Use frozen modeling data `OCT-MD-001` and split `OCT-SPLIT-001` with source SHA-256 `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03` and manifest SHA-256 `de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b`.
- Immediately remove test rows after source/manifest integrity checks and before feature or target extraction; do not inspect, transform, predict, or score test rows.
- Model inputs are exactly `cat1`-`cat116` and `cont1`-`cont14`; exclude `id`, `loss`, `log1p_loss`, split/stratification fields, summaries, and validation-derived information.
- Fit every vocabulary, frequency rule, imputer, scaler, encoder, and optional learned operation on training rows or on the training portion of a recorded CV fold only.
- Pool categorical levels below `min_frequency=132`; missing categorical values use `__MISSING__`; unseen behavior must follow the approved family-specific rules and be measured without validation `loss`.
- Ridge inputs use pooled one-hot categoricals and train-fitted standardized continuous features; histogram-gradient-boosting inputs use pooled ordinal categorical codes, unscaled continuous features, and an explicit 116-column categorical mask.
- Fit on original `loss`; no target transformation is used in Issue #44. Do not calculate feature-model validation MAE or choose a winning model.
- Reproduce the accepted mean and median baselines as a pipeline-readiness check without duplicating their saved prediction artifact.
- Record the code commit, pre-run Git state, source/config hashes, and actual library versions. A Gate 2 approval record remains `pending` until a teammate independently reruns and signs it.

## Review Focus

- A validation-only category must never enter a fitted vocabulary or frequency count; tests must prove the configured unseen fallback for each model family.
- A field with no training-rare bucket must still transform unseen validation values safely: all-zero one-hot for Ridge and missing code for histogram boosting.
- Missing-value guards must be train-fitted and must not silently change the current zero-missing source behavior.
- Reordered, missing, duplicate, or extra source/manifest IDs or feature columns must fail before fitting rather than silently misaligning claims.
- Tree output must preserve exactly 116 categorical positions, keep every categorical cardinality at or below 255 after pooling, and restrict non-finite output to documented missing/unknown categorical codes.

---

### Task 1: Frozen data boundary and feature contract

**Files:**
- Create: `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/preprocessing_pipeline.py`
- Create: `tests/test_leakage_safe_model_inputs.py`

**Interfaces:**
- Produces: `PartitionedModelingData`, `sha256_file(path)`, `load_frozen_partitions(repo_root)`, `make_predefined_split(cv_folds)`, and constants for the 116 categorical, 14 continuous, 130 feature, source-hash, and manifest-hash contracts.
- `PartitionedModelingData` exposes only train and validation IDs/features/targets plus training `cv_fold`; it must not expose test features or targets.

- [ ] **Step 1: Write failing contract tests**

  Add tests using controlled temporary CSV fixtures and the real frozen files to prove exact ID coverage, one-to-one source/manifest alignment, frozen hashes/counts, test removal before feature/target construction, exact ordered feature columns, and complete training fold assignments. Add negative tests for duplicate IDs, missing IDs, unexpected partitions, and missing/extra model fields.

- [ ] **Step 2: Verify the tests fail for the missing module**

  Run: `.venv/bin/python -m unittest tests.test_leakage_safe_model_inputs.FrozenDataBoundaryTests -v`

  Expected: failure because `preprocessing_pipeline` or its public interfaces do not exist.

- [ ] **Step 3: Implement the minimum frozen-data interfaces**

  Load only after verifying both hashes and schema; merge source and manifest one-to-one; validate partition counts; filter to train/validation; then construct the approved feature and target objects. Build `PredefinedSplit` directly from recorded `cv_fold` values.

- [ ] **Step 4: Verify Task 1 passes**

  Run: `.venv/bin/python -m unittest tests.test_leakage_safe_model_inputs.FrozenDataBoundaryTests -v`

  Expected: all Task 1 tests pass.

- [ ] **Step 5: Commit Task 1**

  Commit message: `notebooks: add leakage-safe data boundary`

### Task 2: Both reusable preprocessing families

**Files:**
- Modify: `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/preprocessing_pipeline.py`
- Modify: `tests/test_leakage_safe_model_inputs.py`

**Interfaces:**
- Consumes: `PartitionedModelingData` and approved feature constants from Task 1.
- Produces: `RareCategoryGrouper`, `build_ridge_preprocessor()`, `build_tree_preprocessor()`, `build_training_pipeline(model_family, estimator)`, `tree_categorical_mask()`, and `summarize_category_handling(X_train, X_validation)`.

- [ ] **Step 1: Write failing rare/unseen/missing behavior tests**

  Use small literal DataFrames to prove: frequencies come only from training; values below 132 pool; Ridge uses `OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=132, sparse_output=True)` after the missing guard; an unseen value maps to the infrequent bucket when one exists and all-zero when none exists; tree preprocessing maps rare/unseen values to the pooled code when supported and otherwise to the documented missing code; continuous medians/scalers are train-fitted; and validation values cannot alter learned statistics.

- [ ] **Step 2: Verify the category tests fail for missing behavior**

  Run: `.venv/bin/python -m unittest tests.test_leakage_safe_model_inputs.CategoryHandlingTests -v`

  Expected: failure because the preprocessing factories and grouper do not exist.

- [ ] **Step 3: Implement category handling and both preprocessors**

  Implement an sklearn-compatible rare-category grouper for the tree path. Use `SimpleImputer(strategy="constant", fill_value="__MISSING__")` for categoricals, train-median imputation for continuous fields, `StandardScaler` only for Ridge, and deterministic categorical-first output ordering for the tree mask.

- [ ] **Step 4: Verify the category tests pass**

  Run: `.venv/bin/python -m unittest tests.test_leakage_safe_model_inputs.CategoryHandlingTests -v`

  Expected: all category behavior tests pass.

- [ ] **Step 5: Write failing full-pipeline alignment tests**

  Prove both `build_training_pipeline` variants clone and fit inside each recorded fold, Ridge train/validation transformed widths match, tree output has exactly 130 columns with the first 116 marked categorical, pooled tree cardinalities do not exceed 255, Ridge outputs are finite, and tree outputs contain no infinities with NaNs limited to documented missing/unknown categorical cells.

- [ ] **Step 6: Verify the alignment tests fail before the pipeline wrapper exists**

  Run: `.venv/bin/python -m unittest tests.test_leakage_safe_model_inputs.ModelFamilyPipelineTests -v`

  Expected: failure for the unimplemented pipeline/mask contract.

- [ ] **Step 7: Implement the generic training-pipeline wrapper and mask**

  Require the caller to supply the estimator so Issue #44 establishes preprocessing without choosing Issue #45 model configurations. Reject unknown family names.

- [ ] **Step 8: Verify Task 2 and the pre-existing split/baseline tests pass**

  Run: `.venv/bin/python -m unittest tests.test_leakage_safe_model_inputs tests.test_october_split_artifacts tests.test_october_baseline_artifacts -v`

  Expected: all selected tests pass.

- [ ] **Step 9: Commit Task 2**

  Commit message: `notebooks: add approved preprocessing pipelines`

### Task 3: Reproducible evidence and saved artifacts

**Files:**
- Modify: `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/preprocessing_pipeline.py`
- Modify: `tests/test_leakage_safe_model_inputs.py`
- Create through the validated artifact runner:
  - `preprocessing_checks.csv`
  - `category_handling_summary.csv`
  - `categorical_vocabulary.json`
  - `feature_schema.json`
  - `preprocessing_run_receipt.json`

**Interfaces:**
- Consumes: frozen partitions, category audit, and both preprocessors from Tasks 1-2.
- Produces: `generate_preprocessing_artifacts(repo_root, output_dir)` returning the receipt dictionary after atomically writing all five evidence artifacts.

- [ ] **Step 1: Write failing artifact-contract tests**

  Require check rows for frozen hashes/counts, protected test handling, exact excluded fields, train-only fitted state, category counts, Ridge alignment/finiteness, tree alignment/mask/cardinality/non-finite policy, CV folds, original-target policy, and independent reproduction of both accepted baseline constants/MAEs. Require the known unseen evidence: 9 validation claim-field cells across `cat105` (1), `cat110` (1), `cat113` (1), and `cat116` (6), plus 2,560 rare-or-unseen validation cells.

- [ ] **Step 2: Verify artifact tests fail before generation exists**

  Run: `.venv/bin/python -m unittest tests.test_leakage_safe_model_inputs.SavedArtifactTests -v`

  Expected: failure because the artifact generator/files do not exist.

- [ ] **Step 3: Implement deterministic evidence generation**

  Fit both preprocessors on the entire training partition, transform validation without fitting it, save only compact metadata/evidence rather than transformed matrices, and record `git_dirty_before_run` before outputs are written. Record no feature-model MAE. Make JSON/CSV ordering deterministic apart from the explicit run ID/time.

- [ ] **Step 4: Generate artifacts and verify Task 3**

  Run: `.venv/bin/python -c "from pathlib import Path; import sys; p=Path('notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs'); sys.path.insert(0,str(p)); from preprocessing_pipeline import generate_preprocessing_artifacts; generate_preprocessing_artifacts(Path.cwd(),p)"`

  Run: `.venv/bin/python -m unittest tests.test_leakage_safe_model_inputs.SavedArtifactTests -v`

  Expected: all saved-artifact tests pass and every recorded check status is `pass`.

- [ ] **Step 5: Commit Task 3**

  Commit message: `notebooks: record preprocessing validation evidence`

### Task 4: Executed notebook, reviewer rerun, and pending Gate 2 record

**Files:**
- Create: `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/leakage_safe_model_inputs.ipynb`
- Create: `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/verify_preprocessing.py`
- Create: `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/preprocessing_validation.md`
- Create: `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/gate2_approval_record.md`
- Create: `docs/team/october/Gate 2/issue_44_independent_review.md`
- Modify: `tests/test_leakage_safe_model_inputs.py`

**Interfaces:**
- Consumes: all Task 3 public interfaces and saved artifacts.
- Produces: a top-to-bottom executed notebook, a standalone independent verification command, a plain-language validation report, an explicitly pending approval template, and a teammate-facing independent-review report in the shared team documentation area.

- [ ] **Step 1: Write failing notebook and review-package tests**

  Require sequential notebook execution counts, a Colab/local root override, calls into the reusable module instead of copied preprocessing logic, displayed summaries for both model families and category handling, and no test-partition or feature-model score output. Require the verifier to recompute hashes/counts/category evidence/baselines independently of saved check statuses. Require the approval record to name every frozen version/hash/artifact, leave reviewer/date/decision unsigned, and state `Gate 2 status: pending independent review`.

- [ ] **Step 2: Verify the documentation-package tests fail**

  Run: `.venv/bin/python -m unittest tests.test_leakage_safe_model_inputs.NotebookAndReviewPackageTests -v`

  Expected: failure because the notebook, verifier, report, and approval record do not exist.

- [ ] **Step 3: Create and execute the notebook**

  Keep narrative beside code, regenerate the compact artifacts through the module, display the check table and category/model-family summaries, then execute from top to bottom with nbclient using the project `.venv` kernel.

- [ ] **Step 4: Create the independent verifier and human-facing records**

  The verifier must exit nonzero on any mismatch and print a concise pass summary on success. The validation report must distinguish observed evidence, configured policy, limitations, and Issue #45 handoff. The approval record must remain pending and must not imply that the author performed independent review. The team report must give a reviewer the exact rerun commands, expected evidence, artifact inventory, review checklist, and unsigned decision fields.

- [ ] **Step 5: Run the independent verification and Task 4 tests**

  Run: `.venv/bin/python notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/verify_preprocessing.py`

  Expected: exit 0 with source/split, category, schema, baseline, and artifact checks reported as passed.

  Run: `.venv/bin/python -m unittest tests.test_leakage_safe_model_inputs.NotebookAndReviewPackageTests -v`

  Expected: all documentation-package tests pass.

- [ ] **Step 6: Commit Task 4**

  Commit message: `docs: add Issue 44 Gate 2 review package`

### Task 5: Whole-repository verification and handoff

**Files:**
- Modify only if verification finds an Issue #44 defect, following a new failing test first.

**Interfaces:**
- Consumes: complete Issue #44 implementation and all repository tests.
- Produces: fresh verification evidence and a clean handoff for independent teammate review; it does not mark Gate 2 approved or close the issue.

- [ ] **Step 1: Run the notebook from a restarted kernel**

  Run with nbclient and confirm every code cell completes sequentially without warnings or hidden state.

- [ ] **Step 2: Run the complete test suite**

  Run: `.venv/bin/python -m unittest discover -s tests -v`

  Expected: zero failures and zero errors.

- [ ] **Step 3: Rerun the independent verifier**

  Run: `.venv/bin/python notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/verify_preprocessing.py`

  Expected: exit 0 and the same evidence values as the saved artifacts.

- [ ] **Step 4: Inspect version-control evidence**

  Confirm only planned files changed, the receipt points to the correct code commit/pre-run state, no transformed matrices or personal paths were saved, and `gate2_approval_record.md` still says pending.

- [ ] **Step 5: Commit any verification-only notebook output refresh**

  Commit message, only if needed: `notebooks: finalize Issue 44 evidence`

- [ ] **Step 6: Request independent teammate review**

  Hand the teammate `verify_preprocessing.py`, `preprocessing_validation.md`, and `gate2_approval_record.md`. Do not mark Issue #44 complete until the teammate records the rerun result and Gate 2 decision.

## Self-Review Result

- **Spec coverage:** Every Issue #44 checklist item maps to Tasks 1-4; Task 5 preserves the independent-review requirement.
- **Scope boundary:** Model estimators may be injected to prove pipeline compatibility, but no candidate model is tuned, scored on validation, compared, or selected.
- **Interface consistency:** Task 1 data objects feed Task 2 factories; Task 2 outputs feed Task 3 evidence; Task 3 outputs feed Task 4 notebook/reviewer artifacts.
- **Review-focus coverage:** Each of the five listed failure modes has a behavior test in Tasks 1 or 2 and a saved-evidence assertion in Task 3.
- **Approval safety:** The planned Gate 2 record is a pending template and cannot be interpreted as an independent approval.
