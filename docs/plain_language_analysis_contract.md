# Plain-Language Analysis Contract

This project aims to estimate a claim's final paid amount early enough to 
support reserve planning and to build a better understanding of what factors
are related with higher claim severity.

## Unit of analysis

One row represents an insurance claim. 

## Target variable

`loss` is the regression target. All model evaluation happens in the original
`loss` units (dollars).

## Success metric

Mean Absolute Error (MAE) is the project's success metric. MAE measures on
average how far off a prediction is from the actual claim cost, regardless of
whether the model over or under estimated.

## Data scope

Closed claims without any payment are excluded from this dataset. We are only
verifying that the delivered file contains positive `loss` values.

## Unknown field meanings

The meaning of individual `cat*` and `cont*` fields is not known. The examples
given in the project overview (airbag deployment, point of impact, time 
of day) are possibilities for what these fields might represent.

## Intended non-uses

This September EDA phase does not:

- establish causation between any field and claim severity
- determine or influence any individual claim's reserve amount
- prove the model is production ready
- authorize any automated claims decision making