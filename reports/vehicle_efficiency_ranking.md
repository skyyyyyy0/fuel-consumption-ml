# Vehicle Efficiency Analysis

## 1. Purpose

This analysis compares each vehicle’s actual fuel consumption with the fuel consumption expected by the final XGBoost model.

The goal is to identify vehicles that consumed more or less fuel than expected under their observed trip conditions.

The results are intended for operational screening. A positive fuel deviation does not by itself prove mechanical inefficiency because residuals may also reflect model error, measurement error, omitted variables, route differences, payload, or other operating conditions.

---

## 2. Analysis Scope

- Total Expected vs. Actual records: **9,923**
- Out-of-sample records used: **3,970**
- Records eligible for percentage analysis: **3,890**
- Small-fuel trips excluded from percentage analysis: **80**
- Vehicles evaluated: **12**

Only Validation and Test predictions were used for the vehicle ranking.

Train-set predictions were excluded because they are in-sample predictions.

Trips with Expected Fuel less than or equal to `0.05 L` were excluded from percentage-based calculations because very small denominators can create unstable percentage differences.

---

## 3. Primary Ranking Metric

The primary vehicle-ranking metric is:

```text
Fuel Deviation (%)
= (Total Actual Fuel - Total Expected Fuel)
  / Total Expected Fuel × 100
```

Interpretation:

- Positive value: actual fuel consumption was higher than expected.
- Negative value: actual fuel consumption was lower than expected.
- Value near zero: actual fuel consumption was close to model expectation.

The ranking uses aggregate fuel totals rather than the average of trip-level percentages. This prevents short trips with very small expected fuel values from disproportionately affecting the results.

---

## 4. Operational Classification

The following screening thresholds were used:

- **Higher Fuel Use Than Expected:** Fuel Deviation ≥ **+5%**
- **Within Expected Range:** Fuel Deviation between **-5%** and **+5%**
- **Lower Fuel Use Than Expected:** Fuel Deviation ≤ **-5%**

These thresholds are intended for operational screening and should not be interpreted as proof of mechanical inefficiency.

---

## 5. Vehicle Efficiency Ranking

Rank 1 represents the vehicle with the lowest actual fuel consumption relative to the model expectation.

| Rank | Vehicle | Fuel Deviation | Mean Residual (L) | Median Residual (L) | MAE (L) | Eligible Trips | Status                        |
| ---: | ------- | -------------: | ----------------: | ------------------: | ------: | -------------: | ----------------------------- |
|    1 | VEH_01  |         -9.88% |            -0.040 |              -0.039 |   0.103 |            592 | Lower Fuel Use Than Expected  |
|    2 | VEH_09  |         -9.44% |            -0.032 |              -0.036 |   0.094 |            775 | Lower Fuel Use Than Expected  |
|    3 | VEH_10  |         -9.01% |            -0.044 |              -0.052 |   0.086 |            512 | Lower Fuel Use Than Expected  |
|    4 | VEH_08  |         -8.37% |            -0.071 |              -0.049 |   0.113 |            257 | Lower Fuel Use Than Expected  |
|    5 | VEH_12  |         +0.41% |            +0.039 |              +0.051 |   0.831 |            251 | Within Expected Range         |
|    6 | VEH_06  |         +1.99% |            +0.186 |              -0.178 |   1.317 |            220 | Within Expected Range         |
|    7 | VEH_11  |         +4.71% |            +0.698 |              +0.119 |   1.338 |            136 | Within Expected Range         |
|    8 | VEH_05  |         +4.94% |            +0.560 |              -0.059 |   2.022 |            161 | Within Expected Range         |
|    9 | VEH_03  |         +5.68% |            +0.066 |              +0.004 |   0.126 |            230 | Higher Fuel Use Than Expected |
|   10 | VEH_04  |         +7.88% |            +0.081 |              -0.010 |   0.168 |            256 | Higher Fuel Use Than Expected |
|   11 | VEH_02  |        +12.14% |            +0.071 |              +0.033 |   0.122 |            321 | Higher Fuel Use Than Expected |
|   12 | VEH_07  |        +16.03% |            +0.120 |              -0.015 |   0.251 |            179 | Higher Fuel Use Than Expected |

---

## 6. Vehicles Using More Fuel Than Expected

The following vehicles exceeded the **+5%** screening threshold:

- **VEH_07:** 16.03% more fuel than expected
- **VEH_02:** 12.14% more fuel than expected
- **VEH_04:** 7.88% more fuel than expected
- **VEH_03:** 5.68% more fuel than expected

Among these vehicles, **VEH_07** showed the largest positive fuel deviation and should receive the highest priority for further investigation.

Recommended follow-up analyses include:

- Review idling behavior
- Examine high-RPM operation
- Compare driver behavior
- Evaluate route and traffic conditions
- Check payload differences
- Review maintenance records
- Assess fuel measurement quality
- Analyze trip composition

These results identify vehicles for further investigation rather than proving mechanical inefficiency.

---

## 7. Vehicles Using Less Fuel Than Expected

The following vehicles were below the **-5%** screening threshold:

- **VEH_01:** 9.88% less fuel than expected
- **VEH_09:** 9.44% less fuel than expected
- **VEH_10:** 9.01% less fuel than expected
- **VEH_08:** 8.37% less fuel than expected

These vehicles may provide useful operational benchmarks.

Their driving patterns, route conditions, idling behavior, RPM profiles, and trip characteristics can be compared with vehicles showing positive fuel deviations.

However, lower-than-expected fuel use should still be interpreted alongside vehicle type, route mix, trip distance, payload, and data quality.

---

## 8. Vehicles Within the Expected Range

The following vehicles remained within the **±5%** screening range:

- **VEH_12:** +0.41%
- **VEH_06:** +1.99%
- **VEH_11:** +4.71%
- **VEH_05:** +4.94%

Their aggregate fuel consumption was broadly consistent with model expectations.

However, aggregate deviation alone does not fully describe prediction stability.

---

## 9. Vehicles Requiring Residual Review

Several vehicles had relatively high MAE despite remaining near the expected aggregate range:

- **VEH_05:** MAE 2.0215 L
- **VEH_11:** MAE 1.3381 L
- **VEH_06:** MAE 1.3167 L
- **VEH_12:** MAE 0.8310 L

This suggests that large positive and negative trip-level residuals may be partially canceling each other in the aggregate totals.

A vehicle can therefore have a small Fuel Deviation percentage while still producing large prediction errors on individual trips.

These vehicles should be prioritized in the High Residual Trip Analysis.

---

## 10. Interpretation of Metrics

### Fuel Deviation %

The primary business-ranking metric.

It measures whether total actual fuel consumption was higher or lower than total expected fuel consumption.

### Mean Residual

The average directional difference per trip.

```text
Residual = Actual Fuel - Expected Fuel
```

A positive value indicates higher actual fuel use on average.

### Median Residual

A robust measure of the typical directional difference.

It is less sensitive to extreme residuals than the mean.

### MAE

The average absolute prediction error.

MAE measures error magnitude regardless of whether the model overpredicted or underpredicted.

### Residual Standard Deviation

Measures the variability of trip-level residuals.

A high value may indicate inconsistent operating conditions or the presence of extreme-error trips.

---

## 11. Key Findings

The vehicle-level analysis identified several meaningful patterns across the fleet.

- Four vehicles consumed more than **5%** above the model expectation.
- Four vehicles consumed more than **5%** below the model expectation.
- Four vehicles remained within the expected operating range.
- **VEH_07** showed the largest positive fuel deviation (**+16.03%**) and should be considered the highest-priority candidate for further investigation.
- **VEH_01** showed the largest negative fuel deviation (**-9.88%**) and may serve as a useful operational benchmark.
- **VEH_05**, **VEH_11**, and **VEH_06** exhibited relatively high MAE despite moderate aggregate fuel deviations, indicating that trip-level residuals should be investigated separately.

Overall, aggregate fuel deviation and prediction error should be interpreted together rather than independently.

---

## 12. Limitations

The prediction model does not include every factor that can influence fuel consumption.

Potential omitted variables include:

- Engine load
- Vehicle payload
- Road grade
- Traffic congestion
- Weather conditions
- Tire condition
- Maintenance history
- Detailed driver behavior
- Fuel-sensor measurement uncertainty

Consequently, residual-based vehicle rankings should be interpreted as an operational screening tool rather than definitive evidence of vehicle inefficiency.

---

## 13. Conclusion

This analysis compared actual fuel consumption with model-estimated expected fuel consumption using only out-of-sample predictions.

The vehicle-level ranking identified several vehicles with consistently higher or lower fuel consumption relative to model expectations.

Vehicles with positive aggregate fuel deviations should be prioritized for further operational review, while vehicles with negative deviations may provide useful efficiency benchmarks.

The next step is to perform **High Residual Trip Analysis**, which will investigate whether the largest prediction errors are associated with specific trips, operating conditions, or data-quality issues.
