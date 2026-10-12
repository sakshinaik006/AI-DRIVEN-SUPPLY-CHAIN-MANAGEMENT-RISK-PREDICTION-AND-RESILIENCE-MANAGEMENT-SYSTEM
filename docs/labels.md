# Seven-Day-Ahead Risk Labels

## Purpose

These labels mark whether a supply-chain risk event occurs during the seven
calendar days after a prediction date.

For a feature row dated `t`, predict events during `(t, t + 7 days]`.
Use only information available on or before `t` to construct features.

Labels are binary:

- `1` = the event occurs in the prediction window.
- `0` = the event does not occur in the prediction window.
- `null` = the outcome cannot be determined from available data.

The four label columns are `supplier_failure_7d`, `manufacturing_delay_7d`,
`stockout_7d`, and `transport_delay_7d`.

## Label definitions

### Supplier failure

Set `supplier_failure_7d = 1` if the supplier has a documented failure event
in the seven-day prediction window. A failure event may include a confirmed
supplier shutdown, cancellation, or inability to deliver the required
component.

Set it to `0` if supplier outcome data is available for the full window and
no qualifying event occurred. Use `null` if the supplier has no reliable
outcome record for that window.

Do not treat an ordinary late delivery as supplier failure unless the project
data explicitly records it as a failure event.

### Manufacturing delay

Set `manufacturing_delay_7d = 1` if, within the prediction window, actual
production is less than 85% of planned production:

`actual_production / planned_production < 0.85`

Set it to `0` if production and plan data are available for the full window
and the threshold is not crossed. Use `null` if either value is missing or
planned production is zero.

### Warehouse stockout

Set `stockout_7d = 1` if warehouse inventory falls below its defined
safety-stock level at any point in the prediction window:

`inventory < safety_stock`

Set it to `0` if inventory and safety-stock data cover the full window and
inventory never falls below the threshold. Use `null` if either series or the
safety-stock value is unavailable.

### Transport delay

Set `transport_delay_7d = 1` if a shipment scheduled to arrive in the
prediction window arrives after its scheduled arrival date:

`actual_arrival_date > scheduled_arrival_date`

Set it to `0` if shipment outcome data is available for the full window and
no qualifying late arrival occurred. Use `null` if the shipment has not
resolved or either date is unavailable.

## Implementation and leakage rules

- Generate labels from future outcome records, not from feature values.
- Keep the prediction date and outcome window explicit in the processed data.
- Do not use `Late_delivery_risk`, delivery status, actual shipping days,
  actual arrival dates, or other post-outcome fields as model features.
- A missing outcome is not automatically a negative label; represent it as
  `null` and exclude it from supervised training and evaluation.
- Apply the agreed date split using the prediction date: train April–August
  2025, validation September 2025, and test October 2025.
- For rows whose full seven-day outcome window is not observable, set the
  label to `null` rather than assuming no event occurred.
- Record any synthetic-label generation rules and threshold changes in
  `docs/assumptions.md`.

## Label validation

Before model training, report for each risk:

- Number of positive, negative, and null labels.
- Positive-label rate among non-null labels.
- Date range covered by valid labels.

Check that the positive rate is sufficient for evaluation. If a threshold or
synthetic event rate must be adjusted, document the change and regenerate
labels consistently across all splits.