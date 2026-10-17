# October Split Design Decision

**Status:** Approved (`OCT-SPLIT-001`)
**Owners:** Ella Zou, Liam Stapley
**Milestone:** Modeling / October - Gate 1, Evaluation and split design
**Modeling-data version:** `OCT-MD-001` (see `modeling_contract.md`)
**Split version:** `OCT-SPLIT-001`

## Decision summary

| Item | Decision |
|---|---|
| Partitions | train 70% / validation 15% / test 15% |
| Eligible rows | all 188,318 rows of `data/allstate_claims_data.csv` |
| Random seed | `42` (inherited from the October evaluation plan drafted in September; fixed before any split was drawn) |
| Stratification | 20 quantile bins of `loss` (5% each) |
| Construction | two steps: draw 15% test; then draw validation as 15/85 of the remainder |
| Cross-validation | 5 folds inside train only, stratified on the same `loss` bins |
| Manifest | `notebooks/final-deliverables/October/Gate 1/partition_manifest.csv` with columns `id, partition, cv_fold` |
| Registration | manifest SHA-256, method, seed, and partition counts recorded in the `split` block of `modeling_run_manifest.json` |

## Change from the September proposal

The October evaluation plan drafted in September
(`notebooks/final-deliverables/September/Gate 3/reproducibility-and-october-readiness/october_evaluation_plan.md`)
proposed an 80/20 train/validation split with seed 42 and asked that any change
be recorded before model fitting. This decision keeps the seed and changes the
design to 70/15/15 with a reserved test partition, recorded here before any
model was fit.

The September plan also said validation stays untouched during model selection
and that choices are not tuned against final validation results. That role now
belongs to the reserved test partition, which October never fits, tunes, or
scores on. Hyperparameter tuning happens only inside train through the 5 CV
folds. Validation becomes a limited comparison set: candidates are compared on
it, every comparison is logged, and the stopping rule below caps how often it
is consulted. This matches the October milestone's guidance to treat validation
"as a limited comparison and selection check, not as training data" and the
modeling contract's rule that validation is excluded from fitting and tuning.

## Why this design

- **A reserved test partition.** November's milestone is final evaluation. A
  test partition that October never fits, tunes, or scores on gives November a
  fresher check than reusing a validation set the team compared models on
  repeatedly. At 15%, test holds about 28,000 claims.
- **Validation separate from tuning.** Hyperparameters are tuned with
  cross-validation inside train, so validation is used for a limited number of
  model comparisons rather than for every tuning step.
- **Stratifying on `loss`.** The target has a long right tail (September F-001).
  Unstratified random splits can give the partitions unequal numbers of
  high-loss claims, which would distort the high-loss error analysis planned
  under OCT-006. Stratification decides only which partition a claim joins;
  `loss` and the bins never become model inputs.
- **Shared folds in the manifest.** Writing fold numbers into the manifest means
  every teammate tunes on the same folds, so cross-validation scores are
  comparable across models.

## Integrity checks (automated, written to `split_checks.csv`)

Each check records pass or fail:

1. Source SHA-256 matches `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03`.
2. `id` is unique in the source.
3. The manifest has 188,318 rows; every source `id` appears exactly once;
   partitions do not overlap or omit eligible claims.
4. Partition counts match 70/15/15 within rounding (plus or minus 1 claim).
5. Every train row has exactly one `cv_fold` in 0-4; fold sizes differ by at
   most 1% of train; validation and test rows have an empty `cv_fold`.
6. Regenerating the split with seed 42 reproduces an identical manifest hash.
7. The rebuilt manifest matches the frozen `OCT-SPLIT-001` hash. On a mismatch
   (for example, a different scikit-learn version) the notebook stops before
   writing any file.

## Pre-comparison checks (train vs. validation only)

Produced before any model is fit:

- `loss` summaries per partition: count, mean, median, p90, p99, max.
- High-loss support: number of claims above the **training** p90 and p99 in
  train and validation.
- Categorical level coverage: for each `cat` field, the number of validation
  levels absent from train and the number of validation claims affected. This
  table is handed to preprocessing work; it is not used to change the split or
  set category rules.

For test, only membership and row count are checked. No test `loss` statistic
or score is computed in October.

## Predeclared rules for changing the split

The split is redrawn only if:

1. an integrity check fails, or
2. a documented source or eligibility change occurs.

**Proposed thresholds (pending review):** if the train and validation `loss`
mean or median differ by more than 2%, or their p99 differs by more than 5%,
record an anomaly and bring it to the team for a decision.

No model score is ever a reason to change the split or seed. Any redraw is saved
as a new version (`OCT-SPLIT-002`, ...) with a recorded decision.

## Partition use rules

| Partition | Allowed October use |
|---|---|
| train | Fit models and all learned preprocessing; tune with the 5 recorded folds |
| validation | Compare candidates, usually after tuning them with cross-validation; never used for fitting, encoding, or feature construction. Every validation MAE is logged in the experiment register, including poor results |
| test | Not used in October. Model code drops `partition == "test"` rows at load time. In November, preregistered candidates and both constant baselines are scored once |

Loading pattern for teammates:

```python
manifest = pd.read_csv("notebooks/final-deliverables/October/Gate 1/partition_manifest.csv")
df = pd.read_csv("data/allstate_claims_data.csv").merge(manifest, on="id", validate="one_to_one")
df = df[df["partition"] != "test"]
train = df[df["partition"] == "train"]
valid = df[df["partition"] == "validation"]
```

## Stopping rule

**Proposed values (pending review):** after the first model comparison, run at
most 3 validation-guided iterations (Gate 3 requires at least 1). Stop earlier
if an iteration improves validation MAE by less than 1% relative to the best
previous result. Record every iteration's result and the stop decision.

## Limitations

- The `loss` bin edges for stratification are computed from all 188,318 rows,
  so test targets take part in assigning claims to partitions. They do not
  enter any feature or score. September EDA had already examined full-file
  `loss`, and that exposure is disclosed in the modeling contract.
- Because September EDA used the full labeled file, the reserved test partition
  is protected from October fitting and tuning but is not a wholly unseen
  sample.
- A random internal split is evidence about this supplied file only. It says
  nothing about future-period stability (OCT-009).

## Review status

- [x] 2% / 5% distribution thresholds reviewed and approved
- [x] 3-iteration cap and 1% stopping criterion reviewed and approved
- [x] Independent manifest and integrity verification completed
- [x] Final split design approved