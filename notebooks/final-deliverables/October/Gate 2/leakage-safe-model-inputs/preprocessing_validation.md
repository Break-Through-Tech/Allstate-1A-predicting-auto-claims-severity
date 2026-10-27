# Issue #44 Preprocessing Validation

Issue #44 establishes reusable, leakage-safe model inputs for Ridge and histogram-gradient boosting. It does not tune, compare, or select candidate models; that work belongs to Issue #45.

## Observed evidence

- Frozen inputs match `OCT-MD-001` and `OCT-SPLIT-001`: 131,822 training claims and 28,248 validation claims. Test rows are removed before feature or target objects are constructed.
- Model input is exactly 130 fields: `cat1`-`cat116` followed by `cont1`-`cont14`. `id`, `loss`, derived targets, split metadata, and validation-derived information are excluded.
- Nine validation claim-field cells contain categories absent from training: `cat105` (1), `cat110` (1), `cat113` (1), and `cat116` (6).
- Under the training-only frequency rule, 2,560 validation cells are rare or unseen. The widest pooled tree field has 105 codes, below the 255-category limit.
- Ridge train and validation matrices have the same width, are sparse, and contain only finite values. Tree matrices have exactly 130 columns, with the first 116 marked categorical; they contain no infinities or continuous-column NaNs.
- The accepted baseline readiness check reproduced mean MAE `1962.918654312225` and median MAE `1805.0863526621356` on validation in original loss units.

## Configured policy

- Every learned preprocessing operation is fitted inside the scikit-learn pipeline on training rows or a recorded training-fold subset.
- Ridge uses constant categorical missing guards, `OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=132, sparse_output=True)`, train-median continuous imputation, and train-fitted standardization.
- Histogram-gradient boosting uses the same missing and rare threshold, pooled ordinal codes, unscaled continuous fields, and an explicit 116-column categorical mask.
- A validation-only category shares a trained rare bucket when one exists. Otherwise Ridge emits an all-zero block and the tree path emits a missing code.
- The target is original `loss`; Issue #44 applies no target transformation and records no candidate-model validation score.

## Limitations

- September full-file EDA informed the approved hypotheses, so future target-informed feature changes must be recalculated inside training folds.
- The threshold of 132 is the approved starting rule, not a tuned conclusion.
- The baseline receipt used different library versions; this package independently reproduces its numeric results under scikit-learn 1.6.1, pandas 2.3.3, and NumPy 2.0.2.
- Gate 2 was approved by Mia Chavez on October 27, 2026 after the independent verifier and pipeline checks passed with no discrepancies.

## Issue #45 handoff

Issue #45 can import `build_training_pipeline` from `preprocessing_pipeline.py`, inject the approved Ridge or `HistGradientBoostingRegressor` estimator, and use `make_predefined_split` with the recorded folds. The whole pipeline—not a pre-fitted encoder—must be passed into cross-validation. Only Issue #45 may run the controlled candidate-model comparison and record feature-model validation MAE.
