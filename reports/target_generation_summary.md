# Fuel Target Generation Summary

## Dataset

- Total GPS trips: 15,827
- Total Trip Fuel Used events: 13,947
- Trips with matched fuel target: 12,863

## Match Confidence

- High: 12,231
- Review: 632
- Unmatched: 2,964

## Matching Rule

Trip Fuel Used events were matched to GPS trip stop timestamps
within a maximum tolerance of 60 seconds.

A one-to-one assignment constraint was applied so that each fuel
event could be assigned to at most one trip.

## Confidence Rule

- High: <= 30 seconds
- Review: > 30 and <= 60 seconds
- Unmatched: > 60 seconds or no available fuel event

## Target Validation

- Duplicate fuel assignments: 0
- Zero/negative matched fuel targets: 0
- Unique trip IDs: 15,827

## Modeling Decision

The primary modeling dataset will use High-confidence target matches.

Review and Unmatched observations are retained in the processed
dataset for traceability but will not be included in the initial
baseline model.

## Known Coverage Issue

Target coverage varies across vehicles.

VEH_05, VEH_06, and VEH_12 show lower target coverage than the
fleet average. This pattern was also observed during the Week 1
data-quality audit and will be documented rather than corrected
through imputation.
