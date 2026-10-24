# October Preprocessing Plan

This plan builds on `modeling_contract.md` and `split_design_decision.md`. It does not change the split, the seed, the metric, or the field roles.

## 1. Inputs

- Use `cat1`-`cat116` and `cont1`-`cont14` (130 predictors).
- Exclude `id` (identifier) and `loss` (target).
- Load with the pattern in `split_design_decision.md`: merge the manifest on `id`, then drop `partition == "test"` rows at load time.

## 2. Leakage boundary

Everything learned from data is fitted on training rows only. Validation rows are transformed with the fitted objects and never used to fit them.

| Learned item | Fitted on | Applied to |
|---|---|---|
| Category vocabularies and level frequencies | train | train, validation |
| Rare-level pooling threshold and pooled-level list | train | train, validation |
| Imputers (guard only, see section 6) | train | train, validation |
| Scalers (linear models only) | train | train, validation |
| Feature-selection thresholds or rankings (optional experiments) | train, inside CV folds | train, validation |
| Hyperparameters | train, 5 recorded CV folds | validation (one comparison) |

Two rules make this enforceable:

1. All preprocessing and the model sit in one scikit-learn `Pipeline`, so `fit` can only see the rows it is given.
2. During cross-validation the whole pipeline is refit inside each fold's training portion, using the manifest's `cv_fold` column (`PredefinedSplit`). Fitting the vocabulary once on all of train and then cross-validating would leak level information across folds.

The test partition is not loaded in October.

## 3. Nominal categorical fields

All `cat*` fields are nominal. Alphabetical or integer codes never imply order.

Observed on the training partition: 72 fields have 2 levels and 88 have at most 4. The widest are `cat116` (306 train levels), `cat110` (128), `cat113` (60), `cat109` (81), and `cat112` (51).

| Model family | Representation |
|---|---|
| Regularized linear | One-hot of the pooled training vocabulary. `OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=132, sparse_output=True)`. About 670 columns including the 14 continuous fields. |
| Gradient-boosted trees | Ordinal codes from the same pooled vocabulary, passed with an explicit `categorical_features` mask so the model treats them as unordered labels. The mask must cover all 116 categorical columns. |

The mask is a review item. If it is omitted, the integer codes would be read as ordered numbers, which breaks the September nominal rule.

`HistGradientBoostingRegressor` accepts at most 255 levels per categorical field. `cat116` has 306 training levels, so pooling is required before that model can use it.

## 4. Previously unseen levels

- A level absent from the training vocabulary maps to the same bucket as rare levels. Sharing the bucket gives unseen levels a representation that has training support. A separate "unseen" column would be all zeros in train, so its coefficient would be meaningless.
- For a field with no rare training levels there is no pooled bucket. One-hot encodes an unseen level as all zeros. For the tree models the unknown code is treated as missing.
- Evidence under `OCT-SPLIT-001`: 9 validation claim-field cells carry a level absent from train (`cat116`: 6, `cat105`: 1, `cat110`: 1, `cat113`: 1). Under the rare rule, 2,560 of 3,276,768 validation cells (0.08%) land in the rare or unseen bucket. Test coverage is not examined in October, so the handling is implemented regardless.

## 5. Missing values

The source has 0 missing cells (September Gate 1). Pipelines still include guards so a future file cannot fail silently:

- Assert zero missing values in the training rows before fitting.
- Categorical guard: constant `__MISSING__` (it then follows the rare/unseen route).
- Continuous guard: median fitted on train.

Both guards are no-ops on `OCT-MD-001`.

## 6. Continuous fields

- Values are already on a 0-to-1 scale. No clipping and no outlier removal. Large claims stay in the data.
- Tree models: no transformation.
- Linear models: `StandardScaler` fitted on train, so the regularization penalty treats the 14 fields comparably.
- Correlated pairs stay in for the first comparison (`cont11`-`cont12` 0.994, `cont1`-`cont9` 0.930, `cont6`-`cont10` 0.883). Do not interpret individual linear coefficients for these fields, because correlated predictors make them unstable.

## 7. Target handling

- Models are scored on original `loss` units. `log1p(loss)` is not an evaluation scale.
- The default is to fit on original `loss` with an absolute-error-aligned objective. MAE is minimized by a median-type prediction, and the training median constant already beats the training mean constant by 8.0% on validation.
- A model that trains on `log1p(loss)` is an optional variant. Its predictions are converted back with `expm1` before scoring, and the register records which variant was used.

## 8. Target encoding

**Out of scope for the first comparison.**

CatBoost is also deferred for this reason: its default categorical handling uses ordered target statistics, which is a form of target encoding learned inside the model.

If target encoding is proposed later, it needs its own experiment ID and team approval, and it must follow these rules:

- Cross-fit within the 5 recorded training folds. Each training row is encoded using statistics from the other 4 folds only.
- Validation rows are encoded with statistics from the full training partition.
- Rare and unseen levels use a training-only fallback (the training global statistic that matches the encoded statistic).
- Any smoothing strength is chosen inside the training folds.

## 9. Feature inclusion and exclusion (optional if time permits)

All of these use the same split and fit any selection rule on train inside CV folds. Each is informed by September full-file EDA and must be described that way.

- Drop near-constant categorical fields (OCT-002; 31 fields have a level above 99% share).
- Drop one member of a correlated continuous pair, or rely on regularization (OCT-004).
- Data-driven feature selection (OCT-007).

## 10. Checks for the independent reviewer

1. The pipeline's `fit` is called only on training rows (or only on a fold's training portion).
2. No cell reads `partition == "test"` rows.
3. The categorical mask covers all 116 categorical columns for tree models.
4. Vocabularies and pooled-level lists are saved as an artifact and come from train counts.
5. `cv_fold` comes from the manifest, and each fold's pipeline is refit.
6. Manifest SHA-256 and source SHA-256 match the values at the top of this plan before any model runs.
7. No `loss`-derived column (including the stratification bins) enters the features.
8. `scikit-learn` is `1.6.1` and other library versions are recorded in the run receipt.

## 11. Limitations

- September EDA used the full labeled file before the split, so rare-level and feature hypotheses are informed by data that includes validation claims. Validation scores are therefore not wholly unseen evidence.
- The stratification bins use the full-file `loss` distribution (disclosed in `split_design_decision.md`). They never enter features or scores.
- The rare-level threshold of 132 is a starting choice