# Reproducing October Results

## Environment

Use the committed repository version and the dependency versions recorded in the final run receipts.

## Frozen inputs

- Modeling data: `OCT-MD-001`
- Split: `OCT-SPLIT-001`
- Seed: 42
- Train: 131,822
- Validation: 28,248
- Test: 28,248, reserved and unused

## Reproduce baselines

Run the baseline notebook or verifier that produces:

- Mean baseline validation MAE: 1,962.92
- Median comparator validation MAE: 1,805.09

## Reproduce provisional candidate

Run:

`notebooks/final-deliverables/October/Gate 3/final_model_pipeline.ipynb`

This pipeline:

- verifies the frozen source and split;
- loads the saved top-75 feature list;
- loads the final CatBoost `.cbm` model;
- reproduces validation predictions;
- calculates validation MAE in original `loss` units;
- confirms finite predictions;
- does not access the protected test partition.

## Expected candidate configuration

- Model: `CatBoostRegressor`
- Features: 75
- Loss: MAE
- Depth: 8
- Learning rate: 0.08
- Maximum iterations: 500
- Seed: 42
- 5-fold CV MAE: 1,153.58
- CV SD: 7.19

## Required checks

Confirm:

- 28,248 unique validation IDs;
- no overlap between training and validation IDs;
- no test IDs in predictions;
- predictions align one-to-one with validation rows;
- MAE is computed in original `loss` units;
- source and split hashes match the approved bundle.