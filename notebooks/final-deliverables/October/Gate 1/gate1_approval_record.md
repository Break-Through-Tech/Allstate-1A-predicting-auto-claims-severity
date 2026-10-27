# October Gate 1 Approval Record

Do not mark this record approved until the independent review and the team approval below are complete. Fields in brackets are left blank on purpose.

## Versions that must pass Gate 1

| Item | Version or identifier |
|---|---|
| Modeling-data version | `OCT-MD-001` |
| Split version | `OCT-SPLIT-001` |
| Partition manifest SHA-256 | `de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b` |
| Source SHA-256 | `74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03` |
| Split seed | 42 |
| Frozen split artifact | `notebooks/final-deliverables/October/Gate 1/modeling_run_manifest.json` |
| September workflow run | `G3-20260929T042604Z-5ece32b7` |
| September bundles | `GATE1-3c893f22f14ced97`, `GATE2-8e529ab389c94c3d`, `GATE3-c4860456366d67d3` |
| Baseline run | `OCT-BASE-20261021T040859Z-1d82244e` (accepted metadata deviation documented below) |
| Plan version | `OCT-PLAN-001` |
| Git commit of approved plan files | Pending; the independently reviewed corrections are not yet committed |

## Approved plan files

| File | Location | SHA-256 |
|---|---|---|
| `preprocessing_plan.md` | `notebooks/final-deliverables/October/Gate 1/` | `b958135cc581711c150fcecabfc94a11418284e17653eaf784d7b3c646a0971a` |
| `experiment_plan.md` | `notebooks/final-deliverables/October/Gate 1/` | `4b19023f68a66a2f993278fd9cfbf15b703ff33f5d28e84a13b4b604db859d31` |
| `experiment_register.csv` | `notebooks/final-deliverables/October/Gate 1/` | `de93ca22e0bb94fbdc9c92900c794f5d8036f0b6fd72f5b71cfa9c9241f17b3b` |

## Independent verification

**Reviewer (not an author of the original plan or the metric code):** Ragib Nehal  
**Artifact version / commit reviewed:** PR #53 working tree on `42-preprocessing-and-experiment-plan`, reviewed 2026-10-27; final commit pending

- [x] Split manifest: both SHA-256 values match; counts are 131,822 / 28,248 / 28,248; every `id` appears once; each train row has one `cv_fold` in 0-4.
- [x] Leakage boundaries: the plan requires training-only fitting and per-fold pipeline refitting; after the source-manifest merge and integrity checks, test rows are filtered before feature or target extraction; the categorical mask covers all 116 columns.
- [x] Metric code: validation MAE recomputed independently in original `loss` units and matches the register for B01 (1,962.92) and B02 (1,805.09).
- [x] Approved plan: `preprocessing_plan.md`, `experiment_plan.md` and `experiment_register.csv` agree on the data version, split, seed, thresholds and model choices.

**Result:** Approved by the independent reviewer; full-team Gate approval pending  
**Unresolved feedback:** No remaining artifact-correctness findings. Record the final commit, obtain the remaining team approvals, and assign owners for E02 and O1-O4 before Gate 1 closes. Ragib Nehal owns E01.

## Documented deviation

The baseline receipt records `git_dirty: true` and library versions (scikit-learn 1.5.1, pandas 2.2.2, numpy 1.26.4) that differ from the split manifest (1.6.1, 2.3.3, 2.0.2). This is accepted as a metadata-only reproducibility deviation: it limits the receipt's ability to identify a clean, environment-matched execution, but it does not change the accepted baseline values. Independent verification reproduced both fitted constants and validation MAEs exactly from the frozen source and partition manifest.

## Open items to resolve before approval

1. Team confirms the rare-level threshold of 132 training claims.
2. Team confirms scikit-learn boosting first, with XGBoost only if `xgboost` is added to `requirements.txt`.
3. Team confirms CatBoost and target encoding are deferred.
4. Owners are assigned to experiment rows E02 and O1-O4; Ragib Nehal is assigned to E01.

## Team approval

| Team member | Role | Approve / Object | Date |
|---|---|---|---|
| Ragib Nehal | Fellow / independent reviewer | Approve | 2026-10-27 |
| [name] | Fellow | [ ] | [date] |
| [name] | Fellow | [ ] | [date] |
| [name] | Fellow | [ ] | [date] |

**Dissent or open disagreements:** None recorded by the independent reviewer; remaining team responses are pending.

## Decision

[ ] Gate 1 passes and the modeling approach is approved with the versions above.
[ ] Gate 1 does not pass. Reason: [notes]
