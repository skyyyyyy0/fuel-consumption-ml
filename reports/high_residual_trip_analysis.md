# High Residual Trip Analysis

## 1. Purpose

This analysis investigates trips with the largest prediction errors produced by the final XGBoost fuel-consumption model.

The objective is to understand whether large residuals are associated with operational driving behavior or potential data-quality issues.

Only out-of-sample predictions (Validation and Test) were included in this analysis.

---

## 2. Analysis Scope

- Total out-of-sample trips: **3,970**
- Eligible trips: **3,890**
- Small-fuel trips excluded: **80**
- High-residual threshold (Top 5%): **1.2467 L**
- High-residual trips analyzed: **195**

Residual definition:

```text
Residual = Actual Fuel − Expected Fuel
```

Positive residual:

- Actual fuel consumption was higher than expected.

Negative residual:

- Actual fuel consumption was lower than expected.

---

## 3. High Residual Summary

Among the 195 high-residual trips:

- **112** were high positive residuals.
- **83** were high negative residuals.

Most high-residual trips were concentrated in only a few vehicles.

| Vehicle | High Residual Trips |
| ------- | ------------------: |
| VEH_05  |                  55 |
| VEH_06  |                  53 |
| VEH_11  |                  38 |
| VEH_12  |                  34 |
| Others  |                  15 |

This indicates that prediction errors were not evenly distributed across the fleet.

---

## 4. High Positive Residual Trips

Several trips showed exceptionally large positive residuals.

Examples include:

| Vehicle | Trip       | Residual (L) |
| ------- | ---------- | -----------: |
| VEH_05  | FINAL_0073 |       +56.90 |
| VEH_06  | FINAL_0212 |       +47.45 |
| VEH_05  | FINAL_0003 |       +25.97 |

These trips recorded substantially higher fuel consumption than predicted by the model.

However, several of these values appear unusually large relative to trip distance and duration.

For example:

- A 32 km trip consuming over **66 L**
- A 0.19 km trip consuming over **21 L**

Such observations suggest that operational behavior alone is unlikely to explain these residuals.

---

## 5. High Negative Residual Trips

Several trips also showed unusually large negative residuals.

Examples include:

| Vehicle | Trip       | Residual (L) |
| ------- | ---------- | -----------: |
| VEH_05  | FINAL_0251 |       -26.04 |
| VEH_12  | AFTER_0415 |       -17.11 |
| VEH_06  | FINAL_0461 |        -9.71 |

These trips consumed substantially less fuel than predicted.

Some trips had very short travel distances while the model predicted relatively high fuel consumption, indicating that additional investigation is required.

---

## 6. Operational Characteristics

The high-residual trips did not exhibit a consistent operational pattern.

Observations include:

- Average RPM generally ranged between **950–1,300 RPM**.
- Average speed varied from very low-speed trips to normal driving conditions.
- Idle ratio ranged from approximately **0% to 21%**.
- High RPM ratio was **0** for nearly all high-residual trips.

Based on these observations, high residuals cannot be attributed solely to aggressive driving, excessive idling, or sustained high RPM operation.

---

## 7. Data Quality Findings

Several trips appearing in different analysis periods shared identical operating characteristics.

Examples include:

| Final Period      | After Period      |
| ----------------- | ----------------- |
| VEH_05_FINAL_0003 | VEH_05_AFTER_0350 |
| VEH_06_FINAL_0006 | VEH_06_AFTER_0567 |
| VEH_12_FINAL_0006 | VEH_12_AFTER_0505 |

Each pair contained identical values for:

- Actual fuel
- Expected fuel
- Trip distance
- Trip duration
- Average speed
- Average RPM
- Idle ratio

These duplicated records suggest that overlapping trip extraction or duplicate trip assignment may have occurred across analysis periods.

Therefore, some extreme residuals should be interpreted together with data-quality validation rather than operational behavior alone.

---

## 8. Key Findings

The analysis identified several important observations:

- High residuals were concentrated in a small subset of vehicles.
- High positive residuals slightly outnumbered high negative residuals.
- No clear relationship was observed between high residuals and RPM, speed, or idle behavior.
- Several extreme residuals appeared operationally implausible.
- Duplicate trips were identified across different analysis periods.
- Data-quality issues likely contributed to a portion of the largest residuals.

---

## 9. Limitations

Residual analysis alone cannot determine the exact cause of prediction errors.

Potential contributing factors include:

- Fuel target matching errors
- Duplicate trip records
- Trip boundary definitions
- Sensor measurement uncertainty
- Omitted variables not included in the model
- Genuine operational differences

Further validation of the raw telematics data is recommended before drawing mechanical or operational conclusions.

---

## 10. Conclusion

The High Residual Trip Analysis showed that the largest prediction errors were concentrated in a small number of vehicles and trips.

While some residuals may reflect genuine operational variation, several extreme cases appear to be associated with potential data-quality issues, including duplicated trips and implausible fuel measurements.

Overall, the residual analysis provides a practical framework for identifying trips that require further operational review and data validation before interpreting vehicle efficiency.
