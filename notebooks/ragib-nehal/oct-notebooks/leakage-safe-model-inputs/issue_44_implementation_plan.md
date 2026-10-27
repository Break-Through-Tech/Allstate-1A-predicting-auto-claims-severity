# Issue #44 Leakage-Safe Model Inputs — Implementation Record

## Status

Implementation is complete on the `ragib-nehal` branch. Gate 2 remains pending independent teammate review.

Issue #44 establishes reusable, leakage-safe training inputs for the approved Ridge and histogram-gradient-boosting model families. Candidate-model tuning, validation comparison, and model selection remain part of Issue #45.

## Frozen contract

- Modeling data: `OCT-MD-001`
- Split: `OCT-SPLIT-001`
- Source SHA-256: `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03`
- Manifest SHA-256: `de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b`
- Inputs: `cat1`-`cat116` followed by `cont1`-`cont14`
- Excluded: `id`, `loss`, derived targets, split fields, target summaries, and validation-derived information
- Target policy: original `loss`, with no target transformation
- Required scikit-learn version: `1.6.1`

Test rows are removed immediately after source and manifest integrity checks and before feature or target construction. Every learned preprocessing operation is fitted on training rows or a recorded fold’s training subset.

## Implemented pipelines

### Ridge

- Constant categorical missing-value guard using `__MISSING__`
- `OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=132, sparse_output=True)`
- Train-median continuous imputation
- Train-fitted `StandardScaler`
- Sparse, finite, aligned train and validation matrices

### Histogram-gradient boosting

- Constant categorical missing-value guard using `__MISSING__`
- Training-only rare-category pooling at `min_frequency=132`
- Pooled ordinal category codes
- Train-median continuous imputation without scaling
- Explicit categorical mask covering the first 116 of 130 columns
- Pooled categorical cardinalities at or below 255

Both public training pipelines reject missing values during fitting while retaining transform-time missing and unseen-value safeguards.

## Delivered artifacts

All primary Issue #44 artifacts are in this directory:

- `preprocessing_pipeline.py` — reusable data boundary, preprocessing factories, pipeline wrapper, and artifact generator
- `leakage_safe_model_inputs.ipynb` — executed notebook with sequential execution counts
- `verify_preprocessing.py` — independent raw-data and artifact verifier
- `preprocessing_validation.md` — evidence, policy, limitations, and Issue #45 handoff
- `preprocessing_checks.csv` — machine-readable contract checks
- `category_handling_summary.csv` — per-field rare and unseen evidence
- `categorical_vocabulary.json` — training-only category vocabularies and counts
- `feature_schema.json` — ordered feature and model-family contracts
- `preprocessing_run_receipt.json` — hashes, versions, Git state, matrix evidence, and baseline reproduction
- `gate2_approval_record.md` — unsigned approval template

Supporting files:

- `tests/test_leakage_safe_model_inputs.py`
- `docs/team/october/Gate 2/issue_44_independent_review.md`

## Verified evidence

- Claims: 131,822 train and 28,248 validation
- Recorded CV folds: 5, preserved through `PredefinedSplit`
- Validation-only category cells: 9 — `cat105` (1), `cat110` (1), `cat113` (1), and `cat116` (6)
- Validation rare-or-unseen cells: 2,560
- Maximum pooled tree cardinality: 105
- Mean baseline validation MAE: `1962.918654312225`
- Median baseline validation MAE: `1805.0863526621356`
- Issue #44 tests: 34 passed
- Independent verifier: 5 of 5 sections passed
- Notebook execution counts: 1 through 6, with no notebook warning outputs

The verifier independently recomputes the source and split checks, category evidence, schema, accepted baselines, saved vocabulary, artifact hashes, and preprocessing code hash. It exits nonzero on any mismatch.

## Review outcome and handoff

A fresh code review identified and resolved three issues before handoff:

- Added the fit-time zero-missing guard to both reusable training pipelines.
- Strengthened the verifier to compare recomputed values with saved baselines, category evidence, vocabularies, and the recorded code hash.
- Removed the committed personal path from notebook output.

The independent teammate should run `verify_preprocessing.py`, review both model-family contracts, resolve any discrepancy, and then complete `gate2_approval_record.md`. Gate 2 must remain pending until that review is signed.

## Known repository-wide test exception

The complete repository suite currently reports 76 passing tests, one failure, and one error. Both non-passing checks are pre-existing Issue #21 checks caused by the absent `notebooks/ragib-nehal/ragib_nehal_task_13.ipynb`, which is also absent from the Issue #44 starting commit and `origin/main`. Issue #44’s 34 tests and independent verifier pass.
