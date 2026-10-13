# Gate 1: Evaluation and Split Design

**Status:** Ready for review

**Owner(s):** Ella Zou, Liam Stapley

**Reviewer:** pending

**Artifact version:** `31a93b8` (branch `ella-zou`)

## Scope

Freeze the claim-level partition used for every October model comparison, verify
its integrity, and record train-versus-validation comparability before any model
is fit. The design, its reasons, and the partition-use and stopping rules are in
`split_design_decision.md`.

## Final artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Split design decision | `docs/team/october/Gate 1/split_design_decision.md` | Design, reasons, change rules, partition-use rules, stopping rule |
| Split notebook | `notebooks/final-deliverables/October/Gate 1/split_design.ipynb` | Builds the manifest and all evidence below |
| Partition manifest | `notebooks/final-deliverables/October/Gate 1/partition_manifest.csv` | `id, partition, cv_fold` for all 188,318 claims |
| Split checks | `notebooks/final-deliverables/October/Gate 1/split_checks.csv` | Integrity checks I1-I6 and distribution checks D1-D3 |
| Target summary | `notebooks/final-deliverables/October/Gate 1/partition_target_summary.csv` | `loss` summary for train and validation |
| High-loss support | `notebooks/final-deliverables/October/Gate 1/high_loss_support.csv` | Claims above training p90 and p99 |
| Categorical coverage | `notebooks/final-deliverables/October/Gate 1/categorical_level_coverage.csv` | Validation levels unseen in train, per `cat` field |
| Run manifest | `notebooks/final-deliverables/October/Gate 1/modeling_run_manifest.json` | `split` block now frozen with the manifest hash |
| Artifact tests | `tests/test_october_split_artifacts.py` | Automated checks of the artifacts above |

## Method

- Source `data/allstate_claims_data.csv` (SHA-256 `74037cb2...ae03`), all 188,318 rows eligible (`OCT-MD-001`).
- Stratified random split on 20 quantile bins of `loss`, seed 42: 15% test drawn
  first, then 15/85 of the remainder as validation. 5-fold `StratifiedKFold`
  inside train on the same bins and seed.
- scikit-learn 1.6.1, pandas 2.3.3, numpy 2.0.2 (recorded in the run manifest;
  a different scikit-learn version may draw a different split from the same seed).

## Results

**Partitions** (manifest SHA-256 `de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b`):

| Partition | Claims | CV folds |
|---|---|---|
| train | 131,822 | 0-4 (26,364-26,365 claims each) |
| validation | 28,248 | - |
| test | 28,248 | - |

**Integrity checks:** I1-I6 all pass. The source hash matches, ids are unique,
every claim is in exactly one partition, counts match 70/15/15 within 1 claim,
folds cover train only, and regenerating with seed 42 reproduces an identical
manifest.

**Train vs. validation `loss`:**

| Partition | Mean | Median | p90 | p99 | Max |
|---|---|---|---|---|---|
| train | 3,038.84 | 2,115.39 | 6,401.74 | 14,024.14 | 121,012.25 |
| validation | 3,033.03 | 2,115.62 | 6,403.81 | 13,971.18 | 49,549.85 |

Distribution checks against the proposed thresholds all pass: mean differs by
0.19% (D1), median by 0.01% (D2), p99 by 0.38% (D3).

**High-loss support** (thresholds from train): above the training p90 (6,401.74)
are 13,183 train and 2,826 validation claims (10.0% each); above the training
p99 (14,024.14) are 1,319 train and 279 validation claims (1.0% each).

**Categorical coverage:** 4 of 116 fields have validation levels never seen in
train: `cat116` (6 levels), `cat105`, `cat110`, `cat113` (1 each). Each unseen
level appears on exactly 1 validation claim: 9 field occurrences across 7
distinct validation claims (some claims carry an unseen level in more than one
field). Gate 2 preprocessing must map these to an explicit unseen
representation.

## Anomalies and limitations

- The largest `loss` (121,012.25) fell in train; validation's maximum is
  49,549.85. Stratification balances quantile bins, not individual extremes, so
  the single largest claims land wherever the random draw puts them. This is
  not a split defect and does not trigger the change rules; it matters only for
  reading tail diagnostics.
- The `loss` bin edges use all 188,318 rows, so test targets take part in
  assigning partition membership. They enter no feature or score.
- September EDA used the full labeled file, so the reserved test partition is
  protected from October fitting and tuning but is not a wholly unseen sample.
- A random internal split is evidence about this supplied file only, not about
  future-period stability.

## Verification

- [x] Final notebook runs from a fresh kernel (executed headlessly with nbclient).
- [x] Required outputs were generated and checked (`tests/test_october_split_artifacts.py`, 12 tests pass).
- [ ] Issue requirements have been completed (pending team approval of proposed thresholds and stopping rule).
- [x] Calculated outputs match the recorded source and configuration.
- [ ] Independent review completed, if required.

**Reviewed by:** pending

**Review date:** pending

**Review notes:** Liam/team to confirm the 2% / 5% distribution thresholds and
the 3-iteration / 1% stopping rule. An independent teammate should recheck the
manifest and checks with their own code.

## Completion

The manifest and evidence are generated and pass their automated checks.
Outstanding: team review of the proposed values and independent verification.
