# September Retrospective (draft for team discussion)

This is a starting draft, not the recorded team retrospective — Issue #22
calls for the team to record these at the handoff meeting. Bring this to that
meeting rather than treating it as final.

- **One practice to keep:** freezing evidence into versioned CSV/JSON
  artifacts (data dictionary, anomaly register, validation results) with
  recorded SHA-256 hashes made it possible to check exact numbers instead of
  trusting notebook output that could drift.
- **One practice to change:** several method approvals and independent
  reviews (`method_approvals.csv`, `independent_review_register.csv`) sat at
  `pending` well past their originating issues closing. Assign an independent
  reviewer at the same time an artifact is frozen, not afterward.
- **One experiment to try:** in October, compare mean- and median-constant
  baseline MAE against an early tree-based model to see how much the
  high-cardinality categorical fields and the weak marginal continuous
  correlations actually cost in held-out error.
- **One lesson about interpreting anonymous insurance-claim data
  responsibly:** a weak marginal correlation (e.g. `cont2` at 0.142) is not
  evidence a field is unimportant, and a field's anonymity means we should
  describe what the data shows without inventing a real-world meaning for it.
