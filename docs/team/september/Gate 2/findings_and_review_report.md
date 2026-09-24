# Issue #11: Findings and Review Method

**Status:** Documentation in progress; Gate 2 approval pending  
**Owner:** Allstate 1A team  
**Documentation coordinator:** Liam Stapley  
**Findings register version:** 1.0.0

## Scope

Maintain one versioned findings register linking September EDA observations to specific evidence, interpretations, limitations, and possible October implications.

Record the team's methodology approvals, independent reviews, disagreements, and exact artifact versions before Gate 3 conclusions are finalized.

## Artifacts

| Artifact | Location |
|---|---|
| Findings and review notebook | `notebooks/final-deliverables/September/Gate 2/findings_and_review.ipynb` |
| Findings register | `notebooks/final-deliverables/September/Gate 2/findings_register.csv` |
| Method approvals | `notebooks/final-deliverables/September/Gate 2/method_approvals.csv` |
| Independent review register | `notebooks/final-deliverables/September/Gate 2/independent_review_register.csv` |
| Findings and review report | `docs/team/september/Gate 2/findings_and_review_report.md` |

## Method

The findings register records a stable ID, concise title, evidence artifact and location, exact artifact hash, observed result, interpretation, evidence status, limitation or alternative explanation, possible October implication, owner, and reviewer.

The evidence-status terms are:

- directly observed
- consistent with a pattern
- hypothesis
- inconclusive

Each finding must be supported by a specific EDA result. Interpretations and October implications are recorded separately from direct observations.

The notebook also maintains methodology approval and independent review registers. Existing records are preserved when the notebook is rerun.

SHA-256 hashes identify the exact file contents used during review. If an artifact changes after approval, its approval or review must be reconfirmed for the new version.

## Initial Finding

The initial register includes a finding on the long upper tail of the raw loss distribution, supported by the target-analysis summary and histogram.

Additional findings from categorical support patterns, continuous target correlations, bin-level target summaries, and predictor-predictor correlations will be added after the team reviews the corresponding final evidence.

The findings register is an evidence log, not a feature-selection decision or a claim of causation.

## Team Method Approvals

The team must explicitly approve the following before Gate 3 conclusions are finalized:

| Method | Status |
|---|---|
| Data dictionary | Pending |
| Target views | Pending final #10 verification |
| Rare-level rule | Pending #16 methodology confirmation |
| Continuous-bin rule | Pending |
| Correlation methods | Pending |
| Findings-register format | Pending |

Each decision must record its approver, date, exact artifact hash, and any disagreement or requested change.

## Independent Review

Liam has reviewed the target-analysis and categorical-analysis notebooks and documented follow-up items in the reports and issue comments for #10 and #16.

Those reviews remain pending final verification of the corrected artifacts.

The data dictionary and continuous-analysis deliverables require review by someone independent of their authors. The findings register also requires a team member to review its evidence links, interpretations, and format.

The independent review register records the author, reviewer, date, decision, artifact hash, disagreements, limitations, and verification notes.

## Limitations

The meanings of anonymous predictors remain unknown. Observed target patterns and marginal correlations do not establish causation or independent feature importance.

Rare categorical levels may have unstable loss summaries, and continuous quantile-bin boundaries depend on the observed source distribution.

Possible October implications are proposed follow-up considerations rather than approved modeling decisions.

## Verification

- [ ] Findings register is committed with stable IDs and exact evidence locations.
- [ ] Each finding contains all required fields and uses an approved evidence-status term.
- [ ] Findings are reviewed by someone independent of their authors.
- [ ] Team approves the data dictionary.
- [ ] Team approves the target views.
- [ ] Team approves the rare-level rule.
- [ ] Team approves the continuous-bin rule.
- [ ] Team approves the correlation methods.
- [ ] Team approves the findings-register format.
- [ ] Independent reviews, disagreements, and limitations are recorded.
- [ ] Exact final artifact versions are recorded for Gate 2.
- [ ] Final documentation is reviewed and merged.

## Completion

The notebook establishes the documentation and validation process for Issue #11.

The issue will remain open until the findings are reviewed, all six methods receive team approval, and the independent review register identifies the final artifact versions used for Gate 2.