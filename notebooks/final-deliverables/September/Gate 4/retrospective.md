# September Team Retrospective

## Practice to keep

Freeze important evidence into versioned CSV/JSON artifacts and record source/artifact hashes.

This made it possible to verify exact results rather than relying only on notebook outputs that could change between runs.

## Practice to change

Assign an independent reviewer at the same time an artifact is frozen.

Several September approvals and independent reviews remained pending after the underlying analysis was already complete, which made final handoff documentation harder than necessary.

## Experiment to try

In October, compare the training-only mean- and median-constant baselines against early linear and nonlinear regression models using the same modeling-data version and untouched validation split.

Use those comparisons to evaluate whether high-cardinality categorical fields, nonlinear continuous patterns, and correlated features provide measurable held-out value.

## Lesson about interpreting anonymous insurance-claim data responsibly

Observed statistical relationships must not be converted into unsupported real-world explanations.

A weak marginal correlation does not prove a feature is unimportant, a strong correlation does not prove causation, and anonymous predictors should remain anonymous unless their meanings are explicitly documented.

September conclusions should describe what the data shows, what remains uncertain, and what requires validation rather than inventing semantic explanations.