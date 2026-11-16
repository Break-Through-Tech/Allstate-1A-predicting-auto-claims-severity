# Final Presentation Outline and Initial Ownership

**Milestone:** November Gate 1 — October Handoff and Final Evaluation Plan  
**Issue:** #57 — October handoff and November plan  
**Status:** Initial outline finalized for presentation development  
**Source:** Team presentation hook and outline assignment in Google Docs  
**Source reviewed:** 2026-11-16

## Purpose

This outline lets presentation development begin alongside November Gate 2. It
defines the initial story, slide scope, and section owners. Final test results
remain intentionally absent until the frozen model is evaluated under the
approved November procedure.

The final deck must distinguish among:

- five-fold training cross-validation results;
- October validation results; and
- November protected-test results.

Anonymous predictors may be described only as statistical predictors. They
must not be assigned unsupported business meaning or causal interpretations.

## Presentation Hook

Imagine two auto claims that look similar when they are first reported, but one
ultimately costs several times more than the other. For an insurer, that
difference matters because estimating claim severity accurately can affect
planning, reserving, and how resources are allocated.

Our project asks a simple question: can machine learning use the information
available in a claim to better predict its final loss amount?

Using more than 188,000 historical auto claims, the team compared regression
approaches ranging from constant baselines and linear models to boosted-tree
methods including HistGradientBoosting, XGBoost, and CatBoost. The analysis also
examined which anonymous predictors were statistically useful and how model
performance changed for especially high-loss claims.

**Hook owner:** Liam Stapley  
**Target delivery time:** No more than 90 seconds

## Initial Slide Plan

| Section | Slides | Initial owner(s) | Planned content |
|---|---:|---|---|
| Presentation hook and introduction | 1 | Liam Stapley | Open with similar-looking claims producing different final losses. Connect the problem to severity estimation, introduce the team, and preview the presentation. |
| Project overview | 1–2 | Liam Stapley and Mia Chavez | Explain the continuous claim-loss prediction objective, its potential planning and reserving relevance, and the limits of the evidence. Show the workflow: frozen split → baselines → model comparison → feature experiments → frozen candidate → final evaluation. |
| Data understanding and preparation | 2 | Jonathan Deng | Summarize 188,318 claims, 116 categorical predictors, 14 continuous predictors, `id`, and `loss`. Show the 131,822 / 28,248 / 28,248 train-validation-test split, a useful target-distribution view, and a concise preprocessing diagram. Explain training-only fitting and model-specific preprocessing. |
| Experimental design | 1 | Ragib Nehal and Jonathan Deng | Present the training-mean baseline, training-median comparator, tested model families, MAE in original `loss` units, fixed five-fold training CV, October validation comparison, and protected-test reservation. |
| Model comparison and October selection | 1–2 | Liam Stapley and Ragib Nehal | Use one clear comparison table or chart. Show progression from the mean baseline to HGB and CatBoost. Report the frozen top-75 CatBoost result: five-fold CV MAE 1,153.58 ± 7.19 and October validation MAE 1,136.34. Explain that the decision considered CV stability and validation performance. |
| Feature experiments | 1 | Mia Chavez | Explain the aggregate ranking from model importance, permutation importance, and SHAP. Compare 130, 75, 50, and 30 predictors. State that top 75 retained comparable or slightly stronger performance, while smaller subsets worsened CV MAE. Mention that removing 31 dominant categorical fields from HGB did not improve results. |
| November final evaluation | 1–2 | Liam Stapley and Ragib Nehal | After Gate 2 approval, add protected-test MAE, training-mean and training-median comparisons on the same claims, and a clear CV/validation/test comparison. Until then, retain this section as a labeled placeholder with no test result. |
| Error analysis and limitations | 1 | Ragib Nehal | Show error diagnostics below p90, from p90 to p99, and at or above p99, with support counts. Explain that large-loss claims are harder to predict. Disclose full-file September EDA, validation-informed feature ranking, the small upper-tail sample, anonymous predictors, and the lack of temporal evaluation. Replace validation-only diagnostics with approved final-evaluation diagnostics when Gate 2 is complete. |
| Final model and pipeline | 1 | Jonathan Deng | Present the frozen `CatBoostRegressor`: 75 predictors, MAE loss, depth 8, learning rate 0.08, at most 500 iterations, seed 42, and native categorical handling. Show: frozen inputs → selected features → CatBoost preparation → saved model → predicted `loss`. |
| Final thoughts | 1 | Junaid Pathan and Ella Zou | Summarize technical and collaboration lessons, practical limitations, carefully scoped future work, and acknowledgments to Allstate, Break Through Tech, the Challenge Advisor, and program staff. Prioritize evaluation and communication over renewed broad tuning. |
| Audience Q&A | 1 | Full team | Prepare for questions about CatBoost selection, MAE, high-loss performance, validation exposure, anonymous predictors, and the protected test procedure. |

## Presentation Preview

The presentation will walk through:

1. the problem and data;
2. data preparation and the frozen evaluation design;
3. models and feature experiments;
4. the evidence supporting the frozen CatBoost candidate;
5. the November protected-test evaluation;
6. high-loss error patterns and limitations; and
7. conclusions, future work, and questions.

The intended takeaway is not only which model performed best, but also how the
team built a reproducible evaluation process and what the results can—and
cannot—support about claim-severity prediction.

## Gate 2 Integration Rules

- Do not add protected-test metrics before the frozen final evaluation is run.
- Add only independently verified Gate 2 results to the final deck.
- Report MAE in original `loss` units and compare the final model with both
  training-derived constant predictors on the same test claims.
- Keep claim counts and segment support next to high-loss diagnostics.
- Do not tune the model or select features after viewing test results unless a
  confirmed implementation defect requires a documented rerun.
- Trace every final number and visual to an approved repository artifact.

## Ownership Notes

These are initial section assignments for drafting. Speaker assignments and
transitions may be refined during the Gate 3 team review, but changes should be
recorded in the presentation review evidence.
