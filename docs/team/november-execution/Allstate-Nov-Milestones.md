# Allstate November Milestones

This guide is meant to be used as a suggestion for the November milestone for the Allstate project.

**November Milestone:**

Final Evaluation and Presentation -> Complete the approved final evaluation, finalize results and interpretation, build the presentation, and prepare for delivery.

## Gate Handoffs

The November milestone has 4 Gates:

1. **Gate 1:** October Handoff and Final Evaluation Plan Approved
2. **Gate 2:** Final Evaluation Reviewed
3. **Gate 3:** Presentation Draft Reviewed
4. **Gate 4:** November Complete

Use the same handoff process as prior milestones:

1. **Evidence owner prepares:** link each completed item to the exact committed artifact or approved result.
2. **Independent teammate verifies:** someone other than the primary author checks the critical result.
3. **Team Readiness Review:** review the evidence, limitations, disagreements, and next steps.
4. **Board updates:** dependent work becomes ready after the gate decision is recorded.

## November Scope Protections

- Begin from the approved October Gate 4 handoff and provisional candidate.
- Do not reopen broad model tuning unless a blocking issue is discovered.
- Freeze the final model configuration before using the protected test partition.
- Keep MAE in original `loss` units as the primary evaluation metric.
- Preserve the protected test partition for the approved final evaluation.
- Do not describe internal evaluation results as proof of future-period or production performance.
- Keep anonymous predictors anonymous. Importance does not establish business meaning or causation.
- Continue presentation work in parallel with final evaluation once the project story is stable.

# Gate 1 - October Handoff and Final Evaluation Plan Approved

## October handoff

- [ ] Confirm October Gate 4 is approved.
- [ ] Confirm the provisional final model and exact configuration.
- [ ] Confirm the final feature list, saved model artifact, split manifest, and evaluation code are available.
- [ ] Confirm the protected test partition has not been used during model selection.
- [ ] Carry forward documented limitations, anomalies, and deferred experiments.

## Final evaluation plan

- [ ] Freeze the model and preprocessing configuration before test evaluation.
- [ ] Record the final evaluation metric, test partition, and evaluation procedure.
- [ ] Record the baseline comparisons that will be reported.
- [ ] Record the error diagnostics that will be included.
- [ ] Confirm that no tuning or feature selection will occur after viewing final test results unless a confirmed defect is found.

## Presentation kickoff

- [ ] Confirm the final presentation outline and overall story.
- [ ] Assign initial presentation sections or slide groups.
- [ ] Begin drafting presentation content that does not depend on final test results.

**Gate 1 passes when:** the October handoff is accepted, the final evaluation plan is frozen, and presentation development can begin.

# Gate 2 - Final Evaluation Reviewed

## Final evaluation

- [ ] Run the frozen final model on the protected test partition.
- [ ] Calculate overall MAE in original `loss` units.
- [ ] Compare the final model against the mean and median constant predictors on the same test claims.
- [ ] Confirm prediction alignment, finite outputs, and test claim count.
- [ ] Record the exact model, split, code, configuration, and dependency versions used.

## Error analysis

- [ ] Evaluate errors across the claim-severity distribution, including high-loss claims.
- [ ] Record support counts for each reported segment.
- [ ] Document important failure patterns or limitations.
- [ ] Compare final test performance with October CV and validation evidence.

## Independent review

- [ ] Have a teammate independently verify the final evaluation results.
- [ ] Resolve any blocking discrepancy before Gate 2 approval.
- [ ] Record the final evaluation decision and limitations.

## Presentation development

- [ ] Update the presentation with final evaluation results.
- [ ] Build the main model-comparison and error-analysis visuals.
- [ ] Continue drafting speaker content.

**Gate 2 passes when:** final evaluation is reproducible, independently reviewed, and ready to communicate.

# Gate 3 - Presentation Draft Reviewed

## Presentation content

- [ ] Complete a full first draft of the presentation.
- [ ] Explain the project problem, data, methodology, model comparison, final model, evaluation results, and limitations.
- [ ] Explain the final model output in plain language.
- [ ] Clearly distinguish validation evidence from final held-out evaluation.
- [ ] Preserve the distinction between anonymous statistical predictors and confirmed business concepts.

## Visuals and interpretation

- [ ] Include the key model-comparison result.
- [ ] Include the final evaluation result.
- [ ] Include at least one useful error or high-loss diagnostic.
- [ ] Include only the most relevant data and feature findings.
- [ ] Confirm that all reported numbers trace to approved artifacts.

## Team review

- [ ] Review the full deck as a team.
- [ ] Record requested changes, disagreements, and unresolved questions.
- [ ] Confirm speaker ownership for each section.
- [ ] Prepare likely audience Q&A topics.

**Gate 3 passes when:** the complete presentation story is accurate, understandable, and approved for final polishing.

# Gate 4 - November Complete

## Final presentation

- [ ] Complete all presentation revisions.
- [ ] Confirm all metrics, visuals, and claims are accurate.
- [ ] Confirm slide formatting and terminology are consistent.
- [ ] Complete at least one timed full-team rehearsal.
- [ ] Refine speaker transitions and Q&A preparation.

## Final project artifacts

- [ ] Preserve the final evaluation results and predictions.
- [ ] Preserve the final model artifact and feature list.
- [ ] Preserve the final comparison and error-analysis outputs.
- [ ] Preserve reproduction instructions and review records.
- [ ] Preserve the final presentation and supporting documentation.

## Final review

- [ ] Have the full team review the final presentation and evidence.
- [ ] Record approvals, dissent, remaining limitations, and final artifact versions.
- [ ] Update the GitHub Projects board with completed November work and any remaining follow-up.

**Gate 4 passes when:** the final evaluation is approved, the presentation is ready to deliver, required artifacts are preserved, and the team has completed its final review.