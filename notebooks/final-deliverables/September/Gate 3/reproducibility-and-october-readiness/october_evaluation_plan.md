# October Evaluation Plan

## Split and evaluation

The proposed October starting design is an 80/20 train/validation split with
random seed 42. This is a proposal rather than a completed experiment. Any
approved change to the split design or seed must be recorded before model
fitting.

1. Create the proposed split before fitting any preprocessing.
2. Keep validation data untouched during preprocessing and model selection.
3. Fit all learned preprocessing steps using training data only.
4. Evaluate final validation predictions using MAE in original `loss` units.
5. Do not tune preprocessing or model choices against the final validation results.

## Required constant baselines

The first October comparison will include:

- **Mean-constant baseline:** predict the mean training-set `loss`.
- **Median-constant comparator:** predict the median training-set `loss`.

Both constants will be calculated from the training partition only.

The median comparator is included because the median minimizes absolute error for a constant prediction, while the Challenge Advisor specifically requested the mean-constant baseline.

No MAE calculated from a constant fitted to the complete dataset will be presented as held-out model performance.

## Preprocessing

All preprocessing that learns parameters from data must be fitted on the training partition only.

Examples include:

- category-frequency thresholds;
- categorical encoders;
- imputation rules;
- scaling or transformations;
- feature-selection thresholds; and
- any data-dependent bin boundaries.

## Rare and unseen categorical levels

Rare-level handling will be determined from training data only.

If a categorical encoder groups rare levels, the support threshold and grouping map will be learned from the training partition.

Previously unseen validation categories will be mapped to an explicit unknown/unseen representation supported by the encoder.

Validation category frequencies will not be used to change the training encoding map.

## Model experimentation

The constant baselines establish the initial comparison.

Subsequent models may compare feature-selection and modeling approaches, but the untouched validation partition will remain separate from preprocessing fitting and training.
