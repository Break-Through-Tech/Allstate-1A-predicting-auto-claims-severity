# Issue #44 Independent Review Report

Gate 2 status: pending independent review

This package establishes the leakage-safe training inputs for both approved model families. It intentionally stops before Issue #45 model tuning or comparison.

## Rerun commands

From the repository root, activate a Python 3.12 environment containing the versions in `requirements.txt`, especially scikit-learn 1.6.1. Then run:

```sh
python notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/verify_preprocessing.py
python -m unittest tests.test_leakage_safe_model_inputs -v
python -m unittest discover -s tests -v
```

Restart the notebook kernel and run `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/leakage_safe_model_inputs.ipynb` from top to bottom. Confirm that regenerated artifact changes are limited to explicit run metadata when inputs and code are unchanged.

## Expected independent evidence

- The verifier prints five passing sections: source/split, category, schema, baseline, and artifact integrity.
- Frozen counts are 131,822 train, 28,248 validation, and 28,248 protected test rows.
- Validation contains 9 unseen category cells: `cat105=1`, `cat110=1`, `cat113=1`, and `cat116=6`.
- Rare-or-unseen validation cells total 2,560; maximum pooled tree cardinality is 105.
- Mean baseline MAE is `1962.918654312225`; median baseline MAE is `1805.0863526621356`.
- No candidate-model validation MAE or model-family winner is present.

## Artifact inventory

The working package is under `notebooks/ragib-nehal/oct-notebooks/leakage-safe-model-inputs/`:

- `preprocessing_pipeline.py`: reusable frozen-data and model-family pipelines.
- `leakage_safe_model_inputs.ipynb`: executed narrative and artifact runner.
- `verify_preprocessing.py`: raw-input independent verifier.
- `preprocessing_validation.md`: evidence, policy, limitations, and Issue #45 handoff.
- `preprocessing_checks.csv`: 14 machine-readable pass/fail checks.
- `category_handling_summary.csv`: per-field training and validation routing counts.
- `categorical_vocabulary.json`: training-only frequent/rare vocabularies and counts.
- `feature_schema.json`: ordered feature contract and both model-family configurations.
- `preprocessing_run_receipt.json`: hashes, versions, pre-run Git state, evidence, and baselines.
- `gate2_approval_record.md`: pending approval template to sign after review.

## Reviewer checklist

- [ ] Source and manifest hashes match the frozen contract.
- [ ] Test rows are removed before feature/target construction and are never transformed or scored.
- [ ] Feature order is exactly 116 categorical fields followed by 14 continuous fields.
- [ ] Vocabularies, rare levels, imputers, scalers, and encoders are fitted on training rows or fold-training rows only.
- [ ] Ridge unseen handling and sparse/finite matrix behavior match the plan.
- [ ] Tree unseen handling, 116-field mask, 130-column shape, and cardinality limit match the plan.
- [ ] Recorded folds are used through `PredefinedSplit` with the full pipeline refitted inside each fold.
- [ ] Baseline reproduction matches independently and no Issue #45 result is recorded.
- [ ] Any discrepancy is resolved before changing Gate 2 from pending.

## Independent decision

Reviewer: ____________________

Review date: ____________________

Verifier result: ____________________

Decision: ____________________

Comments or discrepancies: ____________________
