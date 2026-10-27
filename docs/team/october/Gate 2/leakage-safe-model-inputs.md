# Issue #44: Leakage-Safe Model Inputs

**Status:** In progress — implementation complete; independent review pending

**Owners:** Mia Chavez and Ragib Nehal

**Independent reviewer:** Pending

**Milestone:** October – Gate 2

## Scope

Implement the approved preprocessing as reproducible, leakage-safe training pipelines for Ridge regression and histogram gradient boosting.

All learned transformations are fit on training rows or training-fold subsets and then applied unchanged to validation rows. The work establishes aligned model inputs, category-handling evidence, and reproducibility checks without tuning, comparing, or selecting candidate models; those activities belong to Issue #45.

## Final artifacts / Artifact inventory

- `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/preprocessing_pipeline.py`
- `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/leakage_safe_model_inputs.ipynb`
- `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/verify_preprocessing.py`
- `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/preprocessing_validation.md`
- `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/preprocessing_checks.csv`
- `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/category_handling_summary.csv`
- `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/categorical_vocabulary.json`
- `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/feature_schema.json`
- `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/preprocessing_run_receipt.json`
- `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/gate2_approval_record.md`
- `tests/test_leakage_safe_model_inputs.py`

## Frozen data and split

- Modeling-data version: `OCT-MD-001`
- Split version: `OCT-SPLIT-001`
- Training claims: 131,822
- Validation claims: 28,248
- Protected test claims: 28,248
- Recorded training folds: 5
- Target: original `loss`, with no transformation
- Primary metric: MAE in original `loss` units

The run receipt records the frozen source and partition-manifest hashes, preprocessing code hash, Git commit, runtime/library versions, matrix evidence, artifact hashes, and reproduced baseline results.

## Implemented pipelines

The model-input contract contains exactly 130 ordered predictors: `cat1`–`cat116`, followed by `cont1`–`cont14`. The identifiers, targets, target-derived fields, split metadata, and validation-derived information are excluded.

| Model family | Categorical handling | Continuous handling | Output |
|---|---|---|---|
| Ridge regression | Constant missing guard and one-hot encoding with `handle_unknown="infrequent_if_exist"` and `min_frequency=132` | Training-median imputation and training-fitted standardization | Sparse, finite 670-column matrix |
| Histogram gradient boosting | Constant missing guard, training-only rare-level pooling, and ordinal codes with an explicit categorical mask | Training-median imputation without scaling | Finite 130-column matrix with 116 categorical columns |

Both model families use the recorded folds through `PredefinedSplit`. The complete preprocessing pipeline must be refit inside every training fold rather than using a pre-fitted encoder or other learned transformation.

## Category-handling results

Nine validation claim-field cells contain categories absent from training:

| Field | Unseen validation cells |
|---|---:|
| `cat105` | 1 |
| `cat110` | 1 |
| `cat113` | 1 |
| `cat116` | 6 |

The training-only frequency rule routes 2,560 validation cells through rare-or-unseen handling. A validation-only category shares a trained rare bucket when one exists; otherwise, Ridge emits an all-zero encoded block and the tree pipeline emits its missing code. The largest pooled tree cardinality is 105, below the 255-category limit.

## Validation protections

- Test rows are removed before feature or target objects are constructed and are never transformed or scored.
- Category vocabularies, rare-level rules, imputers, scalers, encoders, and model parameters are fit on training rows or fold-training rows only.
- Validation `loss` is not used to define category rules or other learned preprocessing state.
- September full-file target relationships remain hypotheses only; any target-informed rule must be recalculated within October training data or training folds.
- `id`, `loss`, `log1p_loss`, target summaries, and validation-only information are absent from model inputs.
- No candidate-model validation MAE or model-family winner is recorded in the Issue #44 artifacts.

## Baseline readiness check

The package independently reproduces the accepted constant-baseline results on the frozen validation partition:

| Model | Fitted constant | Validation MAE |
|---|---:|---:|
| Training mean constant | 3,038.840255 | 1,962.918654 |
| Training median constant | 2,115.39 | 1,805.086353 |

These values are readiness checks only. They do not constitute candidate-model comparison or tuning.

## Automated verification

`preprocessing_checks.csv` records 14 passing checks covering:

- frozen source and split hashes;
- partition counts and protected-test isolation;
- the 130-field feature contract;
- training-only fitting;
- rare and unseen category counts;
- Ridge and tree matrix alignment, shape, sparsity, and finite-value policies;
- recorded cross-validation folds;
- the original-target policy; and
- independent reproduction of both accepted baselines.

From the repository root, use a Python 3.12 environment with the versions in `requirements.txt`, including scikit-learn 1.6.1, and run:

```sh
python notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/verify_preprocessing.py
python -m unittest tests.test_leakage_safe_model_inputs -v
python -m unittest discover -s tests -v
```

Restart the notebook kernel and run `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/leakage_safe_model_inputs.ipynb` from top to bottom. When inputs and code are unchanged, regenerated artifact differences should be limited to explicit run metadata.

## Independent verification

Independent review remains pending. A teammate must rerun the verifier and tests, confirm both model-family pipelines against the frozen contract, resolve any discrepancy, and sign:

`notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/gate2_approval_record.md`

### Expected independent evidence

The verifier should print five passing sections: source/split, category, schema, baseline, and artifact integrity. Its independently calculated counts, category evidence, matrix properties, and baseline results should match the values in this report.

### Reviewer checklist

The reviewer should confirm:

- source and manifest hashes match the frozen contract;
- test rows remain inaccessible to preprocessing and scoring;
- feature order is exactly 116 categorical fields followed by 14 continuous fields;
- all learned preprocessing state is fit on training rows or fold-training rows only;
- rare and unseen handling matches the recorded evidence;
- Ridge and tree matrix properties match the feature contract;
- the full pipeline is refit inside each recorded fold;
- both baseline results reproduce; and
- no Issue #45 result appears in this package.

### Independent decision

Reviewer: ____________________

Review date: ____________________

Verifier result: ____________________

Decision: ____________________

Comments or discrepancies: ____________________

## Limitations

- September full-file EDA informed the approved hypotheses, so future target-informed feature changes must be recalculated inside training folds.
- The rare-level threshold of 132 is the approved starting rule, not a tuned conclusion.
- The accepted baseline receipt used different library versions; this package reproduces its numeric results under Python 3.12.12, scikit-learn 1.6.1, pandas 2.3.3, and NumPy 2.0.2.
- The package proves preprocessing readiness, not candidate-model quality, production suitability, or future-period stability.

## Completion

The Issue #44 implementation artifacts establish reproducible, leakage-safe inputs for both approved model families and provide the required validation evidence and rerun instructions.

Issue #44 remains open until an independent teammate completes the rerun, resolves any discrepancies, signs the Gate 2 approval record, and records the approval decision.
