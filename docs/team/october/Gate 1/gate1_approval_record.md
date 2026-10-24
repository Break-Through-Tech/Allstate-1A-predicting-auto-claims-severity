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
| Baseline run | `OCT-BASE-20261021T040859Z-1d82244e` (see open item 1) |
| Plan version | `OCT-PLAN-001` |
| Git commit of approved plan files | [fill in after merge] |

## Approved plan files

| File | Location | SHA-256 |
|---|---|---|
| `preprocessing_plan.md` | `docs/team/october/Gate 1/` | [fill in after merge] |
| `experiment_plan.md` | `docs/team/october/Gate 1/` | [fill in after merge] |
| `experiment_register.csv` | `notebooks/final-deliverables/October/Gate 1/` | [fill in after merge] |

## Independent verification

**Reviewer (not an author of the plan or the metric code):** [name]
**Artifact version / commit reviewed:** [commit]

- [ ] Split manifest: both SHA-256 values match; counts are 131,822 / 28,248 / 28,248; every `id` appears once; each train row has one `cv_fold` in 0-4.
- [ ] Leakage boundaries: every learned item is fitted on training rows only; the pipeline is refit inside each CV fold; test rows are dropped at load; the categorical mask covers all 116 columns.
- [ ] Metric code: validation MAE recomputed independently in original `loss` units and matches the register for B01 (1,962.92) and B02 (1,805.09).
- [ ] Approved plan: `preprocessing_plan.md`, `experiment_plan.md` and `experiment_register.csv` agree on the data version, split, seed, thresholds and model choices.

**Result:** Approved / Changes requested / Pending
**Unresolved feedback:** [notes]

## Open items to resolve before approval

1. The baseline receipt records `git_dirty: true` and library versions (scikit-learn 1.5.1, pandas 2.2.2, numpy 1.26.4) that differ from the split manifest (1.6.1, 2.3.3, 2.0.2). Rerun the baseline notebook from a clean commit on pinned versions, or record this as a documented deviation.
2. Team confirms the rare-level threshold of 132 training claims.
3. Team confirms scikit-learn boosting first, with XGBoost only if `xgboost` is added to `requirements.txt`.
4. Team confirms CatBoost and target encoding are deferred.
5. Owners are assigned to experiment rows E01, E02 and O1-O4.

## Team approval

| Team member | Role | Approve / Object | Date |
|---|---|---|---|
| [name] | Fellow | [ ] | [date] |
| [name] | Fellow | [ ] | [date] |
| [name] | Fellow | [ ] | [date] |
| [name] | Fellow | [ ] | [date] |
| [name] | Fellow | [ ] | [date] |

**Dissent or open disagreements:** [notes]

## Decision

[ ] Gate 1 passes and the modeling approach is approved with the versions above.
[ ] Gate 1 does not pass. Reason: [notes]