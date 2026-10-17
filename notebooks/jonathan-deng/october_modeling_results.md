# October Modeling Results

## Evaluation design

- Modeling-data version: `OCT-MD-001`
- Frozen split: `OCT-SPLIT-001`
- Partition sizes: train `131,822`, validation `28,248`, protected test `28,248`
- Seed: `42`
- Stratification: 20 `loss` quantile bins
- Cross-validation: five folds within training only
- Metric: MAE in original `loss` units
- Workflow Run: `OCT-JD-GATE1-MODELING-002`

## Comparison

| Model | Training/CV MAE | Validation MAE | Validation claims | Improvement vs mean | Improvement vs median | Runtime |
|---|---:|---:|---:|---:|---:|---:|
| Training mean constant | 1,968.12 | 1,962.92 | 28,248 | 0.00% | -8.74% | 0.00 s |
| Training median constant | 1,810.48 | 1,805.09 | 28,248 | 8.04% | 0.00% | 0.00 s |
| Multivariate linear regression | 1,310.31 | 1,290.13 | 28,248 | 34.28% | 28.53% | 54.47 s |
| Ridge with one-hot encoding | 1,307.37 | 1,288.81 | 28,248 | 34.34% | 28.60% | 14.10 s |
| HGB v1, learning rate 0.08 | 1,203.84 | 1,187.53 | 28,248 | 39.50% | 34.21% | 17.37 s |
| HGB v2, learning rate 0.04 | 1,224.38 | 1,209.22 | 28,248 | 38.40% | 33.01% | 18.68 s |
| Random forest | 1,243.54 | 1,223.51 | 28,248 | 37.67% | 32.22% | 24.69 s |

## Interpretation

HGB v1 is the strongest compared approach on overall validation MAE and on the reported p90 and p99 validation-loss tails. Random forest is the next-best nonlinear model at `1,223.51`. Both linear approaches improve substantially over the constant references, with Ridge slightly better than ordinary linear regression.

The evidence-driven iteration changed only HGB `learning_rate` from `0.08` to `0.04`. Validation MAE regressed from `1,187.53` to `1,209.22`, so the negative result is retained and no additional iteration is justified under the current limit.

The multivariate linear and Ridge pipelines use median imputation, one-hot encoding with `handle_unknown='ignore'`, continuous median imputation and standardization, then predict in original `loss` units. HGB and random forest use median/mode imputation, ordinal encoding with unseen categories mapped to `-1`, and tree-based prediction in original `loss` units.

## Tail diagnostics

The validation p90 tail contains `2,826` claims and the p99 tail contains `279` claims. HGB v1 tail MAE is `3,315.61` at p90 and `7,767.74` at p99; random forest tail MAE is `3,429.01` and `8,263.84`. These tail results are diagnostics and were not treated as an undisclosed selection metric.

Four categorical fields contain validation levels unseen in training. The pipelines handle these through their declared unknown-category behavior. The experiment register preserves the baselines, candidate runs, and negative iteration.

The test partition was checked only for membership and row count. No test target summary, prediction, or performance score was used during October modeling or selection.

## Artifacts

Raw outputs are in `notebooks/jonathan-deng/october_modeling_outputs/`:

- `model_comparison.csv`
- `cross_validation_results.csv`
- `experiment_register.csv`
- `validation_tail_error_diagnostics.csv`
- `modeling_run_metadata.json`
- split and category diagnostics
