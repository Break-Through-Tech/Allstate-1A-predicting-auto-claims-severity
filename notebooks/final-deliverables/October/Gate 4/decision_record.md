# Gate 4 Model Selection Decision

## Provisional November Candidate

The provisional November candidate is the top-75-feature `CatBoostRegressor`.

Configuration:

- MAE loss
- depth 8
- learning rate 0.08
- maximum 500 iterations
- seed 42
- 75 selected predictors

Five-fold training CV MAE: 1,153.58  
CV SD: 7.19

Validation MAE: [FINAL VALIDATION MAE]

Mean baseline validation MAE: 1,962.92  
Median comparator validation MAE: 1,805.09

The candidate outperforms both constant predictors on the same validation claims.

## Limitations

- September EDA used the full labeled dataset.
- Later feature ranking used validation observations for permutation and SHAP importance.
- The validation partition therefore is not fully independent of the broader modeling process.
- The protected test partition remains unused and is reserved for later evaluation.
- The p99 loss segment contains only 279 validation claims.
- Anonymous predictors limit semantic interpretation.

## Gate 4 Decision

The October artifact bundle is complete and reproducible, no blocking modeling defect remains, and the top-75 CatBoost model is approved as the provisional November candidate pending full-team Gate 4 approval.