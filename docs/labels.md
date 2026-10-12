# Labels (v1)

All labels are `label_7d`: a 0/1 value that looks at the next 7 days after `date`
(days t+1 to t+7). The label for day t may use future data; features may not.

| Risk | entity_type | label_7d = 1 if, in t+1..t+7 |
|---|---|---|
| supplier_failure | supplier | a delivery arrives more than **X = 3 days** late, or a disruption event hits the supplier |
| manufacturing_delay | plant | actual production < **85%** of plan on any day, or the plant reports a delay |
| warehouse_stockout | warehouse | stock is below safety stock (or zero) on any day |
| transport_disruption | route | a shipment arrives after its scheduled date |

X = 3 days is the starting value. Adjust the threshold or the generator if the
positive rate falls outside the target.

## Target positive rate

Each label needs **3-5% positives or more** (overall and in train). The positives report is
written to `outputs/label_positives_report.csv` with the data v1 handover. If a label misses the
target, Member 1 adjusts thresholds or the generator and tells Member 3 at once.

## Rules

- Labels are created BEFORE the time split, then split by date.
- Rows in the last 7 days of the window (25-31 Oct) have no full look-ahead and are dropped from labelled tables.
- Leakage columns (`Late_delivery_risk`, delivery status, actual shipping days) never appear in features.
