# Vehicle-State Feature Summary

## Idle Definition

Idle state was defined as:

- Speed < 1 km/h
- RPM > 500
- Speed-to-RPM timestamp difference <= 30 seconds

Because the telemetry is event-driven, idle ratio was calculated using time-weighted state durations rather than raw row counts.

## Duration Rule

Each observed state duration was capped at 30 seconds to prevent long telemetry gaps from being interpreted as continuously maintained vehicle states.

## Generated Features

- idle_duration_min
- valid_state_duration_min
- idle_ratio
- state_obs_count
- idle_obs_count

## Validation Results

- Total Trips: 15,827
- Unique Trip IDs: 15,827
- Missing idle_ratio: 658 trips (4.2%)
- Idle Ratio Range: 0.0–1.0
- Median Idle Ratio: 0.128
- Mean Idle Ratio: 0.154
- P95 Idle Ratio: 0.377

## Period Coverage

- Before: 95.1%
- After: 96.4%
- Final: 96.0%

## Decision

`idle_ratio` is approved as a core baseline ML feature.

Trips without sufficient state telemetry will be handled during the final cleaning stage.
