---

* ** `docs/labels.md`**:

```markdown
# Seven-Day-Ahead Supply Chain Risk Labels

## Overview
- Predicts risk events occurring within the window `(t, t + 7 days]` using only past information available on or before prediction date `t`.
- Labels are binary (`1` = event occurs, `0` = event does not occur, `null` = incomplete outcome window).

## Label Definitions

### 1. Supplier Failure (`supplier_failure_7d`)
- `1`: Confirmed shutdown, cancellation, or complete inability to deliver required components within 7 days.
- `0`: Outcome data is complete for the 7-day window and no failure event occurred.
- `null`: Missing or unobservable outcome history.

### 2. Manufacturing Delay (`manufacturing_delay_7d`)
- `1`: Actual production falls below 85% of planned production in the 7-day window:
  `actual_production / planned_production < 0.85`
- `0`: Outcome data complete and production remains at or above 85% of plan.
- `null`: Missing production data or planned production is zero.

### 3. Warehouse Stockout (`stockout_7d`)
- `1`: Physical inventory falls below the safety stock threshold at any point during the 7-day window:
  `inventory < safety_stock`
- `0`: Outcome data complete and inventory remains above safety stock throughout the window.
- `null`: Unavailable inventory or safety stock records.

### 4. Transport Delay (`transport_delay_7d`)
- `1`: Shipment scheduled to arrive in the window arrives after the scheduled arrival date:
  `actual_arrival_date > scheduled_arrival_date`
- `0`: Outcome data complete and shipment arrives on or before the scheduled date.
- `null`: Shipment unfulfilled or missing date values.

## Leakage Prevention Rules
- Features are restricted strictly to data collected on or before date `t`.
- Exclude post-outcome columns (`Late_delivery_risk`, delivery status, actual transit days) from feature sets.
- Any missing outcome is designated as `null` and removed from supervised fitting and metrics calculation.
