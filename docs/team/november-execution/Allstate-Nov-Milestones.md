# Allstate November Milestones

This guide is meant to be used as a suggestion for the November milestone for the Allstate project.

**November Milestone:**

Final Evaluation and Presentation -> Complete final evaluation, finalize the project story, prepare the presentation, and organize the complete project artifact set for handoff.

## Gate Handoffs

The November milestone has 4 Gates:

1. **Gate 1:** October Handoff and Final Evaluation Plan Approved
2. **Gate 2:** Final Evaluation Complete
3. **Gate 3:** Presentation Draft Reviewed
4. **Gate 4:** Final Project Package Complete

Use the same handoff process as prior milestones:

1. **Evidence owner prepares:** link each completed item to an exact committed artifact.
2. **Independent teammate verifies:** someone other than the primary author checks the critical result.
3. **Team Readiness Review:** review the evidence, limitations, disagreements, and decision.
4. **Board updates:** dependent work becomes ready after the gate decision is recorded.

## November Scope Protections

- Begin from the approved October Gate 4 handoff and provisional candidate.
- Do not reopen broad model tuning unless a blocking issue is discovered.
- Freeze the final model configuration before using the protected test partition.
- Keep MAE in original `loss` units as the primary evaluation metric.
- Preserve the protected test partition for the approved final evaluation.
- Do not describe internal evaluation results as proof of future-period or production performance.
- Keep anonymous predictors anonymous. Statistical importance does not establish business meaning or causation.
- Build the presentation in parallel with final evaluation beginning in Week 2.
- Prioritize final evaluation, communication, documentation, and project organization over additional experimentation.

# Gate 1 - October Handoff and Final Evaluation Plan Approved

## October handoff and November plan

- [ ] Confirm October Gate 4 is approved and the provisional candidate is frozen.
- [ ] Confirm the final feature list, saved model artifact, split manifest, evaluation code, and preprocessing requirements are available.
- [ ] Confirm the protected test partition has not been used during model selection.
- [ ] Carry forward documented limitations, anomalies, deferred experiments, and Challenge Advisor questions.
- [ ] Freeze the final evaluation procedure, metric, baseline comparisons, and planned diagnostics before opening the test partition.
- [ ] Confirm that no model tuning or feature selection will occur after viewing final test results unless a confirmed defect is found.
- [ ] Finalize the presentation outline and assign initial slide sections so presentation development can begin alongside Gate 2.

**Gate 1 passes when:** the October handoff is accepted, the model and final evaluation plan are frozen, and presentation development is ready to begin.

# Gate 2 - Final Evaluation Complete

## Final evaluation and diagnostics

- [ ] Run the frozen final model on the protected test partition using the approved pipeline.
- [ ] Calculate MAE in original `loss` units and compare the final model against the training-mean and training-median constants on the same test claims.
- [ ] Confirm prediction alignment, finite outputs, claim counts, split integrity, and the exact model/configuration used.
- [ ] Evaluate errors across the loss distribution, including the agreed high-loss segments and their support counts.
- [ ] Compare final test performance with October CV and validation evidence and explain any meaningful differences.
- [ ] Record important model limitations, failure patterns, and interpretation constraints.
- [ ] Have someone other than the evaluation author independently reproduce or verify the critical final metrics and confirm that no post-test model changes were made.
- [ ] Resolve any blocking discrepancy before the final evaluation is approved.
- [ ] Add the approved final results and visuals to the developing presentation.

**Gate 2 passes when:** final evaluation is complete, reproducible, independently reviewed, and ready to communicate.

# Gate 3 - Presentation Draft Reviewed

## Presentation development and review

- [ ] Complete a full presentation draft covering the problem, data, methodology, model comparison, final evaluation, limitations, and conclusions.
- [ ] Explain the final model and its output in language appropriate for both technical and non-technical stakeholders.
- [ ] Include only the most useful EDA, model comparison, feature-selection, and error-analysis evidence.
- [ ] Clearly distinguish training CV, October validation, and November final held-out evaluation.
- [ ] Preserve the distinction between anonymous statistical predictors and confirmed business concepts.
- [ ] Confirm that every reported number and visual traces to an approved project artifact.
- [ ] Review the full deck as a team and record requested changes or unresolved questions.
- [ ] Assign speaker ownership and prepare likely Q&A topics.
- [ ] Complete at least one initial presentation walkthrough before Gate 3 approval.

**Gate 3 passes when:** the complete presentation story, results, visuals, and limitations are accurate and approved for final polishing.

# Gate 4 - Final Project Package Complete

## Final presentation and rehearsal

- [ ] Complete all presentation revisions.
- [ ] Confirm final metrics, claims, visuals, terminology, and citations are accurate.
- [ ] Complete at least one timed full-team rehearsal.
- [ ] Refine speaker transitions and Q&A preparation.
- [ ] Preserve the final presentation and presentation outline in the approved project location.

## Final project documentation

Review and update the project documentation so that the repository reflects the final state of the project rather than the state at the end of an earlier milestone.

- [ ] Review every September, October, and November issue report and update completion status, final decisions, limitations, review records, and links where needed.
- [ ] Review milestone handoff documents and confirm that carried-forward work is either completed, explicitly deferred, or still documented as unresolved.
- [ ] Update project-level and relevant folder-level `README.md` files so they describe the final workflow and point to the canonical artifacts.
- [ ] Review model comparison, feature experiment, evaluation, and decision summaries for outdated conclusions.
- [ ] Confirm that references to provisional models, open gates, incomplete reviews, and unused artifacts reflect the final project state.
- [ ] Confirm reproduction instructions remain accurate from a clean committed version.
- [ ] Preserve final review records, decisions, limitations, and unresolved risks.

## Canonical final deliverables

Create one clearly organized final-deliverables area that provides a simple path through the project without requiring reviewers to navigate every working notebook.

At minimum, preserve canonical deliverables for each milestone:

### September - Data Understanding

- [ ] Final reproducible EDA pipeline notebook.
- [ ] Final data dictionary and anomaly record.
- [ ] Final findings / decision register.
- [ ] September handoff or completion report.
- [ ] Reproduction instructions.
- [ ] Monthly artifact bundle index.

### October - Model Development

- [ ] Final reproducible model pipeline notebook.
- [ ] Final model comparison and feature-selection evidence.
- [ ] Final model-selection decision record.
- [ ] Final fitted model and selected feature list.
- [ ] October model-development report.
- [ ] Reproduction instructions.
- [ ] Monthly artifact bundle index.

### November - Evaluation and Presentation

- [ ] Final evaluation notebook or pipeline.
- [ ] Final evaluation results, predictions, and diagnostics.
- [ ] Final evaluation decision record.
- [ ] Final presentation and presentation outline.
- [ ] Final project limitations / conclusions record.
- [ ] Reproduction instructions.
- [ ] Monthly artifact bundle index.

## Artifact Bundle organization

- [ ] Add an `ARTIFACT_BUNDLE.md` or equivalent index to each final milestone folder.
- [ ] Add an artifact bundle index to each Gate folder where the gate produces multiple approved artifacts.
- [ ] Each artifact bundle should identify the exact artifacts used for that gate or milestone, their purpose, status, version or commit, owner, reviewer, and relevant decision record.
- [ ] Artifact bundle files should link to canonical artifacts rather than unnecessarily duplicating files.
- [ ] Confirm that every major reported result can be traced from the final presentation or report to its source artifact and review record.
- [ ] Create one top-level final-deliverables index that links September, October, and November into a single project workflow.

## Repository cleanup and final review

- [ ] Confirm final folders use consistent names and obvious navigation.
- [ ] Remove or clearly label superseded draft artifacts where they could confuse reviewers.
- [ ] Do not delete historical experiments or negative results required for traceability.
- [ ] Confirm all canonical notebooks execute from their documented environment or have a verified reproducible output.
- [ ] Confirm the protected/final evaluation evidence is preserved exactly as approved.
- [ ] Have the full team review the final presentation, documentation structure, and canonical artifact set.
- [ ] Record final approvals, dissent, remaining limitations, and exact committed versions.
- [ ] Update the GitHub Projects board to reflect completed work and any true post-project follow-up.

**Gate 4 passes when:** the final evaluation and presentation are approved, the team has rehearsed, all major documentation reflects the final project state, and the complete project can be understood and reproduced from the organized final-deliverables package.