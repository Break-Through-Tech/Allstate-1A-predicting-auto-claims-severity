# October Modeling Handoff

No winning model is selected here. This draft identifies the inputs October
work should start from, per Issue #22.

- **Frozen source and field-role versions:** `data/allstate_claims_data.csv`
  (188,318 rows, 132 columns, SHA-256 recorded in
  `Gate 3/data_quality_evidence/validation_results.csv`); 1 identifier, 116
  categorical predictors, 14 continuous predictors, 1 target, per
  `data_dictionary.csv`.
- **Target and metric:** `loss` in original dollar units; MAE on held-out
  data is the project success metric. `log1p(loss)` remains a visualization
  field only.
- **Proposed split/cross-validation design and seed:** not yet fixed by the
  team. Recommend a fixed random seed recorded alongside whichever
  train/validation split or k-fold scheme is chosen, so results reproduce.
- **Baseline plan:** fit a mean-constant baseline (per the Challenge
  Advisor's request) and a median-constant baseline (proposed here because
  the median minimizes absolute error for a constant prediction), both fitted
  on the training partition only.
- **Leakage-safe categorical encoding and preprocessing boundaries:** any
  encoder, scaler, or rare-level pooling must be fit on training folds only
  and applied unchanged to validation/test folds.
- **High-cardinality and unseen-level handling questions:** `cat116` (326
  levels), `cat110` (131 levels), and `cat109` (84 levels) need an explicit
  encoding strategy plus a defined fallback for levels not seen during
  training.
- **Correlated-feature interpretation concerns:** `cont11`-`cont12` (r=0.994),
  `cont1`-`cont9` (r=0.930), and `cont6`-`cont10` (r=0.883) should be
  considered before trusting individual linear-model coefficients.
- **Candidate model families:** drawn from the project overview; specific
  families are not selected here — that decision belongs to October.
- **Required validation evidence:** held-out MAE in original loss units for
  every baseline and candidate model, computed only after preprocessing is
  fit on training data.
- **Unresolved questions for the Challenge Advisor:** none beyond those
  already logged in the September findings register; the Challenge Advisor
  should be asked to confirm the rare-level threshold (188 rows) and the
  proposed median-constant baseline before October experiments begin.
