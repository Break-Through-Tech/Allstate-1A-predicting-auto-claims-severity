# Final Presentation Content (Gate 3 Draft)

Slide-by-slide content for the Google Slides deck. Every number below is copied
from a committed project artifact; the source is listed under each slide.

**Status:** Draft. November Gate 2 (protected test evaluation) has not been run,
so every `[TEST RESULT]` placeholder must be filled from the approved Gate 2
artifacts before Gate 3 approval.

## Evidence labels

Use these labels on every slide that shows a model score, so the audience can
tell the three kinds of evidence apart.

| Label | What it is | Claims | Use it for |
|---|---|---:|---|
| **Training CV** | Mean MAE across 5 fixed folds inside the training partition | 131,822 (≈26,364 per fold) | Model development and stability (± SD) |
| **October validation** | MAE on the shared validation partition | 28,248 | Comparing model families; choosing the candidate |
| **November held-out test** | MAE on the protected test partition, scored once with the frozen model | 28,248 | Final internal evaluation only |

Wording rules (from the November scope protections and the October independent review):

- Validation is **not** fully independent: September EDA used the full labeled file, and the CatBoost permutation/SHAP feature ranking used validation observations.
- Before Gate 2, say the test partition was "not used" for fitting, selection, prediction, or scoring; do not say its rows were "never read".
- Test results are an internal held-out evaluation, not proof of future-period, first-filing, or production performance.
- Predictors are anonymous (`cat1`–`cat116`, `cont1`–`cont14`). Describe them as statistically influential only; never assign business meaning or causation.

## Deck overview (12 slides, about 12–15 minutes)

| # | Section | Suggested owner |
|---|---|---|
| 1 | Hook and introductions | Liam |
| 2 | Problem and project overview | Liam + Mia |
| 3 | Data at a glance | Jonathan |
| 4 | Frozen split and preprocessing | Jonathan |
| 5 | Experimental design | Ragib + Jonathan |
| 6 | Model comparison (CV + validation) | Liam + Ragib |
| 7 | Feature experiments | Mia |
| 8 | Final model and how a prediction is made | Jonathan |
| 9 | November final held-out evaluation | Gate 2 evaluation owner |
| 10 | Error analysis: high-loss claims | Ragib |
| 11 | Limitations and conclusions | Ragib + Junaid |
| 12 | Takeaways, future work, thanks + Q&A | Junaid + Ella |

Owners follow the team outline; the team should confirm them in the Gate 3 review.

---

## Slide 1: Hook and introductions

**On slide**
- Title: *Predicting Auto Claim Severity with Machine Learning*
- Allstate Team 1A: Liam Stapley, Mia Chavez, Ragib Nehal, Junaid Pathan, Ella Zou, Jonathan Deng

**Speaker notes:** Use the recorded hook. Two claims can look similar at first report but end at very different costs. The question: can machine learning use the information in a claim to better predict its final loss? Each member gives college, major, and focus area. Keep it under 90 seconds.

---

## Slide 2: Problem and project overview

**On slide**
- Goal: predict each claim's final `loss` (a continuous dollar-style amount) from 130 anonymous claim attributes.
- Why it matters: better severity estimates can support planning, reserving, and resource allocation. This project did not test any of these operational uses.
- Workflow: **Frozen split → Baselines → Model comparison → Feature experiments → Final candidate → Final held-out test**
- Preview: boosted-tree models performed best; a 75-feature CatBoost model was selected.

**Visual:** a single-row workflow diagram of the six steps.

**Speaker notes:** Keep the business framing cautious: the model estimates loss; we did not test reserving or claim-handling decisions.

---

## Slide 3: Data at a glance

**On slide**
- 188,318 historical claims
- 116 anonymous categorical predictors (`cat1`–`cat116`) and 14 anonymous continuous predictors (`cont1`–`cont14`), plus `id` and the target `loss`
- Loss is heavily right-skewed:
  - median 2,115.57 and mean 3,037.34
  - 90th percentile 6,401.74 and 99th percentile 13,981.20
  - max 121,012.25 (skewness 3.79)

**Visual:** `notebooks/final-deliverables/September/Gate 3/target_distribution_evidence/target_distribution_views.png`

**Speaker notes:** Most claims are moderate, and a small group is very expensive. This long right tail is why we used MAE and why high-loss claims get their own error analysis on slide 10. Because predictors are anonymous, we can say which fields help prediction but not what they represent.

**Sources**
- `notebooks/final-deliverables/September/Gate 3/target_distribution_evidence/target_distribution_summary.csv`
- `notebooks/final-deliverables/October/Gate 4/october_model_development_report.md` (Inputs and Encoding)

---

## Slide 4: Frozen split and preprocessing

**On slide**

| Partition | Claims | Role |
|---|---:|---|
| Train | 131,822 | Model fitting + 5 fixed CV folds |
| Validation | 28,248 | Model comparison and selection |
| Protected test | 28,248 | Final held-out evaluation (November) |

- Split uses seed 42 and is stratified by loss quantile bins, so all three partitions have similar loss distributions:
  - train: median 2,115.39, p99 14,024.14
  - validation: median 2,115.62, p99 13,971.18
- Preprocessing was learned **only from training data** and differed by model family:
  - **Linear/Ridge:** one-hot categories (rare levels pooled for Ridge) and standardized continuous fields
  - **Random Forest/HGB:** ordinal category codes
  - **XGBoost/CatBoost:** native categorical handling
- No target transformation: every model predicts `loss` in original units.

**Visual:** split bar (70% / 15% / 15%) plus a small "fit on train → apply to validation/test" arrow diagram.

**Sources**
- `notebooks/final-deliverables/October/Gate 1/partition_manifest.csv`
- `notebooks/final-deliverables/October/Gate 1/partition_target_summary.csv`
- `notebooks/final-deliverables/October/Gate 4/october_model_development_report.md` (model input table)

---

## Slide 5: Experimental design

**On slide**
- Primary metric: **MAE in original loss units**, the average absolute gap between predicted and actual loss.
- Reference predictors every model must beat:
  - training-mean constant (3,038.84 for every claim), the required baseline
  - training-median constant (2,115.39), the tougher constant under MAE
- Models tested: Linear Regression, Ridge, Random Forest, HistGradientBoosting, XGBoost, CatBoost.
- Development used training CV and October validation. The protected test set was reserved and scored once, at the end, with a frozen model.

**Speaker notes:** MAE is easy to explain ("off by about X on average") and is not dominated by a few huge claims the way squared error would be. The median constant is the best possible single-number guess under MAE, so beating it shows the model learned something real.

**Sources**
- `notebooks/final-deliverables/October/Gate 2/baseline_results.csv`
- `notebooks/final-deliverables/October/Gate 1/experiment_register.csv` (B01, B02)

---

## Slide 6: Model comparison

**On slide** (lower MAE is better)

| Model | Features | Training CV MAE (± SD) | October validation MAE | vs mean baseline |
|---|---:|---:|---:|---:|
| Mean constant (baseline) | 0 | 1,968.12 ± 5.76 | 1,962.92 | — |
| Median constant | 0 | 1,810.48 ± 6.20 | 1,805.09 | 8.0% better |
| Linear Regression | 130 | 1,310.31 | 1,290.13 | 34.3% better |
| Ridge | 130 | 1,308.55 ± 7.82 | 1,290.43 | 34.3% better |
| Random Forest | 130 | 1,243.54 | 1,223.51 | 37.7% better |
| XGBoost | 130 | 1,183.31 ± 6.86 | 1,162.00 | 40.8% better |
| HistGradientBoosting | 130 | 1,172.29 ± 6.29 | 1,151.17 | 41.4% better |
| **CatBoost (final)** | **75** | **1,153.58 ± 7.19** | **1,136.34** | **42.1% better** |

**Visual:** horizontal bar chart of validation MAE, sorted, with CatBoost highlighted and the two constants in grey. Optionally plot CV MAE as a dot next to each bar.

**Key message:** boosted trees clearly beat linear models and Random Forest. CatBoost was best on both CV and validation, and it is 37.0% better than the median constant.

**Speaker notes:** We chose CatBoost on CV performance and stability, not on one validation number. Its CV advantage over HGB (about 19) is larger than the fold-to-fold SD (about 6–7). The gap between the top boosted models is modest. Every model scores about 16–21 lower on validation than on CV. This is consistent across models, so it does not change the ranking.

**Sources**
- `notebooks/final-deliverables/October/Gate 3/final_model_comparison_results/final_model_comparison.csv`
- Linear Regression, Random Forest, and Jonathan's HGB rows record no CV SD, so leave SD blank for them.

---

## Slide 7: Feature experiments

**On slide**
- Three importance views were combined into one ranking: CatBoost model importance, permutation importance, and SHAP.
- Top-ranked predictors: `cat80`, `cat101`, `cat79`, `cat100`, `cont2`. These are statistical signals only; their business meaning is unknown.
- CatBoost feature-subset test (training CV, same settings with about 250 iterations):

| Feature set | Training CV MAE (± SD) |
|---|---:|
| All 130 | 1,160.00 ± 6.89 |
| **Top 75** | **1,159.79 ± 7.59** |
| Top 50 | 1,161.12 ± 6.69 |
| Top 30 | 1,167.15 ± 6.86 |

- Result: **top 75 matched all 130 while dropping 55 predictors**; going down to 30 clearly hurt.
- Separate HGB test (Issue #46): removing 31 near-constant categorical fields (one level above 99% of training claims) did not help:
  - CV MAE 1,171.51 → 1,172.58
  - validation MAE 1,151.24 → 1,152.50

**Visual:** small line chart of CV MAE vs feature count (130 / 75 / 50 / 30) with SD error bars.

**Speaker notes:** The benefit of 75 features is simplicity, not accuracy. The gain of 0.21 is far smaller than the fold SD. The ranking used validation observations, which is one reason the protected test result matters. Do not mix these 250-iteration numbers with the final 500-iteration model's 1,153.58.

**Sources**
- `notebooks/liam-stapley/model_experiment_outputs/aggregate_feature_ranking.csv`
- `notebooks/liam-stapley/model_experiment_outputs/catboost_feature_selection_cv.csv`
- `notebooks/ragib-nehal/oct-notebooks/feature-experiments-review/outputs/feature_experiment_comparison.csv`

---

## Slide 8: Final model and how a prediction is made

**On slide**
- Model: `CatBoostRegressor` with:
  - 75 selected predictors
  - MAE loss
  - depth 8 and learning rate 0.08
  - 500 trees and seed 42
- Trained on all 131,822 training claims and saved as a reusable model file; it predicts without retraining.
- Pipeline: **Claim record → select 75 predictors → CatBoost native categorical handling → saved model → predicted loss**
- Output: one number per claim, the estimated `loss` in the same units as the original target.

**Plain-language explanation:** CatBoost builds hundreds of small decision trees in sequence, each correcting the previous trees' mistakes. It handles categorical fields directly, which suits a dataset with 116 of them.

**Visual:** 5-box pipeline graphic.

**Sources**
- `notebooks/final-deliverables/October/Gate 4/decision_record.md`
- `notebooks/final-deliverables/October/Gate 3/final_model_pipeline_results/final_model_pipeline_receipt.json`
- `notebooks/liam-stapley/model_experiment_outputs/final_catboost_features.csv`

---

## Slide 9: November final held-out evaluation

**Blocked until November Gate 2 is approved.** Fill only from the approved Gate 2 artifacts.

**On slide**

| Evidence | Claims | CatBoost MAE | Mean constant | Median constant |
|---|---:|---:|---:|---:|
| Training CV (5 folds) | 131,822 | 1,153.58 ± 7.19 | 1,968.12 | 1,810.48 |
| October validation | 28,248 | 1,136.34 | 1,962.92 | 1,805.09 |
| **November held-out test** | 28,248 | `[TEST RESULT]` | `[TEST RESULT]` | `[TEST RESULT]` |

- Improvement over the median constant on test: `[TEST RESULT]`%
- One sentence on whether the test result is consistent with CV and validation: `[TEST RESULT]`

**Speaker notes:** The model was frozen before the test set was opened and was not changed afterward. This is our least-exposed estimate, but it is still an internal random split, not future-period performance.

**Sources:** `[November Gate 2 artifact paths]`

---

## Slide 10: Error analysis (high-loss claims)

**On slide**
- Segments are based on training thresholds: p90 = 6,401.74 and p99 = 14,024.14.

| Segment (October validation) | Claims | CatBoost MAE | Mean-constant MAE |
|---|---:|---:|---:|
| Below p90 | 25,422 | 868.05 | 1,446.54 |
| p90 to p99 | 2,547 | 2,976.91 | 5,670.26 |
| p99 and above | 279 | 8,779.90 | 15,170.38 |
| Test-set version | | `[TEST RESULT]` | `[TEST RESULT]` |

- Key message: error on the largest claims is about **10× the error on ordinary claims**.
- CatBoost improved most over HGB in the top group (8,779.90 vs 9,446.5), but the p99 group has only 279 claims, so treat small differences as inconclusive.

**Visual:** grouped bar chart by segment (CatBoost vs mean constant) with the claim counts printed under each group.

**Speaker notes:** In the October error diagnostics, the HGB model under-predicted every claim in the p99 group. The CatBoost tail file records only MAE, so do not claim the same under-prediction rate for CatBoost unless Gate 2 measures it.

**Sources**
- `notebooks/liam-stapley/model_experiment_outputs/final_catboost_tail_diagnostics.csv`
- `notebooks/final-deliverables/October/Gate 3/final_model_comparison_results/final_tail_comparison.csv`
- `notebooks/ragib-nehal/oct-notebooks/feature-experiments-review/outputs/error_diagnostics.csv` (mean-constant rows, HGB under-prediction rate)

---

## Slide 11: Limitations and conclusions

**On slide**

**Limitations**
- **Validation exposure:** September EDA used the full labeled file, and the feature ranking used validation observations. October validation is useful but not fully independent.
- **High-loss claims** remain much harder to predict, and the top segment is small (279 validation claims).
- **Anonymous predictors:** we can identify influential fields but not explain them in business terms or claim causation.
- **One random split:** this does not show stability over time or under future data shifts.

**Conclusions**
- A 75-feature CatBoost model cut validation MAE by about 42% vs the mean baseline and 37% vs the median constant.
- Final held-out result: `[TEST RESULT]`
- The workflow (frozen split, training-only preprocessing, logged experiments, independent reproduction) is itself a key deliverable.

**Sources**
- `notebooks/final-deliverables/October/Gate 4/november_handoff.md` (Outstanding Limitations and Risks)
- `notebooks/final-deliverables/October/Gate 4/independent_review.md`

---

## Slide 12: Takeaways, future work, thanks + Q&A

**On slide**
- **Technical skills:**
  - reproducible splits and cross-validation
  - baseline-first comparison
  - CatBoost and XGBoost
  - feature importance and SHAP
  - error analysis
- **Professional skills:**
  - combining independently built experiments
  - reviewing teammates' evidence
  - communicating model limits honestly
- **Future work:**
  - test on later time periods
  - work with domain experts to interpret the top predictors
  - develop specific approaches for high-loss claims
  - revisit the deferred feature hypotheses (Issue #46 O2–O4)
- **Thanks:** Allstate, Break Through Tech, our Challenge Advisor, and program staff
- Q&A slide: project title and team names

---

## Q&A preparation

| Likely question | Prepared answer | Owner |
|---|---|---|
| Why CatBoost? | It had the best training CV (1,153.58 ± 7.19) and validation MAE (1,136.34). Its CV gain over HGB (about 19) exceeds the fold SD, and it handles 116 categorical fields natively. | Liam |
| Why MAE instead of RMSE? | MAE is in loss units and easy to explain. With a heavily skewed target, squared error would let a few very large claims dominate model choice. | Ragib |
| How does it do on big claims? | Much worse: about 8,780 MAE on the p99+ group vs 868 on ordinary claims. Only 279 validation claims fall in that group. | Ragib |
| What do `cat80` / `cat101` mean? | We don't know; the data is anonymized. We only claim they are statistically useful for prediction. | Mia |
| Is validation leakage a problem? | It is disclosed rather than hidden. Feature ranking used validation, so we kept a protected test set untouched until the model was frozen. | Ragib |
| Why drop 55 features if accuracy didn't change? | A simpler model with the same CV MAE is easier to run and maintain. Cutting to 30 features hurt, so 75 was the floor we tested. | Mia |
| Would this work in production / on new claims? | Not shown. Results are internal held-out evaluations on one random split; time-based testing and first-filing data would be needed. | Junaid |
| Why only a modest gain over HGB/XGBoost? | The boosted models are close; most of the gain comes from moving to boosted trees at all (about 1,290 → about 1,150). | Jonathan |
| How do you know the numbers are right? | Two teammates independently reproduced the final validation MAE from a clean kernel, matching to within 3.6e-12. | Jonathan |

---

## Corrections to the team outline

The pasted outline matches the repo except for these items.

| Outline section | Outline says | Repo says | Change |
|---|---|---|---|
| Results | CatBoost "around the low 1,140s on validation" | Final top-75 CatBoost: **1,136.34**. The 1,142.33 figure is the all-130 CatBoost run. | Use 1,136.34 |
| Results | "Final tuned CatBoost" | The last step only raised the iteration limit from 250 to 500; it was not a tuning search | Say "final CatBoost (500 iterations)" |
| Feature experiments | Top 75 "essentially the same or slightly better" | 1,159.79 vs 1,160.00, a 0.21 difference against a SD of about 7 | Say "essentially the same with 55 fewer predictors" |
| Feature experiments | "reducing to 50 or 30 worsened CV MAE" | Top 50: 1,161.12 (+1.3 vs top 75, within noise). Top 30: 1,167.15 (clearly worse). | "50 was slightly worse, 30 clearly worse" |
| Feature experiments | (implied) final 1,153.58 compared with subsets | Subset runs used about 250 iterations; 1,153.58 is from 500 iterations | Keep the two on separate lines or slides |
| Experimental design | "Protected test remains unused" | True only until Gate 2 runs | Update after Gate 2 to "scored once with the frozen model" |
| Whole outline | No final test evaluation section | Gate 3 requires CV, validation, and November test to be clearly separated | Add slide 9 (held-out evaluation) |
| Q&A | "why the protected test set has not yet been used" | Becomes outdated after Gate 2 | Replace with "how was the test set protected?" |
| Final thoughts | Owner "Junaid / sixth team member" | The roster in the hook lists Ella Zou as the sixth member | Assign Junaid + Ella |

Confirmed correct in the outline:
- 188,318 claims, 116 categorical and 14 continuous predictors
- 131,822 / 28,248 / 28,248 split
- baselines: mean 1,962.92 and median 1,805.09
- HGB validation 1,151.17
- CV 1,153.58 ± 7.19 with 75 predictors
- CatBoost configuration
- HGB 31-field experiment
- 279 claims in the p99 group

## Gate 3 checklist

- [ ] Fill every `[TEST RESULT]` from approved November Gate 2 artifacts
- [ ] Confirm speaker owners in the team review
- [ ] Team deck review; record requested changes and open questions below
- [ ] At least one full walkthrough before Gate 3 approval

### Requested changes / open questions

| Date | Raised by | Item | Resolution |
|---|---|---|---|
| | | | |
