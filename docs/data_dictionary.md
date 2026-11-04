# Data Dictionary (features_v1 & features_v2)

Defines all feature tables generated for all four operational risk domains across the multi-tier supply chain platform.

Time Window: **2025-04-01 to 2025-10-31** (214 days).  
Splits:
- `train`: 2025-04-01 to 2025-08-24 (146 days)
- `purge`: 2025-08-25 to 2025-08-31 and 2025-09-24 to 2025-09-30 (14 days)
- `val`: 2025-09-01 to 2025-09-23 (23 days)
- `test`: 2025-10-01 to 2025-10-31 (31 days; labels valid 2025-10-01 to 2025-10-24)

---

## 1. features_supplier_v1.parquet & features_supplier_v2.parquet

| Column | Type | Range / Values | Description | Leak-Free Rule |
|---|---|---|---|---|
| `entity_type` | string | `supplier` | Entity role | Constant |
| `entity_id` | string | `SUP001` .. `SUP008` | Unique supplier ID | Categorical identifier |
| `date` | string (ISO) | `2025-04-01` .. `2025-10-31` | Observation / prediction date | Chronological index |
| `split` | string | `train`, `purge`, `val`, `test` | Time partition | Derived from `date` |
| `supplier_delay_7d_avg` | float | $\ge 0.0$ | Past 7-day average delivery delay (days) | Shifted by 1 day (`s.shift(1).rolling(7)`) |
| `rain_7d_sum` | float | $\ge 0.0$ mm | Past 7-day total precipitation at supplier location | Shifted by 1 day from Open-Meteo |
| `news_tone_14d_trend` | float | $[-20, 20]$ | 14-day rolling average of GDELT news tone | Shifted by 1 day |
| `single_source_flag` | int | $0, 1$ | 1 if supplier is a sole-source component vendor | Static topology feature |
| `label_7d` | float | $0.0, 1.0, \text{NaN}$ | Target: Disruption occurs within $(t+1, t+7]$ | Future outcome; NaN for $t >$ 2025-10-24 |

---

## 2. features_manufacturing_v1.parquet & features_manufacturing_v2.parquet

| Column | Type | Range / Values | Description | Leak-Free Rule |
|---|---|---|---|---|
| `entity_type` | string | `plant` | Entity role | Constant |
| `entity_id` | string | `PLT001` .. `PLT004` | Unique plant ID | Categorical identifier |
| `date` | string (ISO) | `2025-04-01` .. `2025-10-31` | Observation / prediction date | Chronological index |
| `split` | string | `train`, `purge`, `val`, `test` | Time partition | Derived from `date` |
| `production_shortfall_7d` | float | $[-1.0, 1.0]$ | 7-day rolling shortfall: $(\text{planned} - \text{actual}) / \text{planned}$ | Shifted by 1 day |
| `capacity_util_7d_avg` | float | $[0.0, 1.5]$ | 7-day average capacity utilization ratio | Shifted by 1 day |
| `supplier_failure_prob_oof` | float | $[0.0, 1.0]$ | Out-of-fold predicted risk from upstream suppliers | Generated from leak-free CV |
| `machine_downtime_7d_sum`| float | $\ge 0.0$ hrs | Cumulative unscheduled maintenance downtime | Shifted by 1 day |
| `label_7d` | float | $0.0, 1.0, \text{NaN}$ | Target: Disruption occurs within $(t+1, t+7]$ | Future outcome; NaN for $t >$ 2025-10-24 |

---

## 3. features_warehouse_v1.parquet & features_warehouse_v2.parquet

| Column | Type | Range / Values | Description | Leak-Free Rule |
|---|---|---|---|---|
| `entity_type` | string | `warehouse` | Entity role | Constant |
| `entity_id` | string | `WH001` .. `WH005` | Unique warehouse ID | Categorical identifier |
| `date` | string (ISO) | `2025-04-01` .. `2025-10-31` | Observation / prediction date | Chronological index |
| `split` | string | `train`, `purge`, `val`, `test` | Time partition | Derived from `date` |
| `stock_level` | float | $\ge 0.0$ units | Current physical stock on hand at day $t$ | Logged at end of day $t$ |
| `stock_days_cover` | float | $\ge 0.0$ days | Current inventory divided by past 7-day average daily demand | Shifted by 1 day |
| `inbound_shipment_delay_7d`| float | $\ge 0.0$ days | Average transit delay on inbound routes over past 7 days | Shifted by 1 day |
| `forecast_demand_gap` | float | float | Difference between predicted order surge and current stock | Lagged forecast output |
| `label_7d` | float | $0.0, 1.0, \text{NaN}$ | Target: Inventory falls below safety stock within $(t+1, t+7]$ | Future outcome; NaN for $t >$ 2025-10-24 |

---

## 4. features_transport_v1.parquet & features_transport_v2.parquet

| Column | Type | Range / Values | Description | Leak-Free Rule |
|---|---|---|---|---|
| `entity_type` | string | `route` | Entity role | Constant |
| `entity_id` | string | `RT001` .. `RT010` | Unique transit corridor ID | Categorical identifier |
| `date` | string (ISO) | `2025-04-01` .. `2025-10-31` | Observation / prediction date | Chronological index |
| `split` | string | `train`, `purge`, `val`, `test` | Time partition | Derived from `date` |
| `delivery_delay_7d_avg` | float | $\ge 0.0$ days | Past 7-day average shipment delay on route | Shifted by 1 day |
| `corridor_congestion_score`| float | $[0.0, 1.0]$ | Port / customs delay metric derived from DataCo transit times | Shifted by 1 day |
| `wind_speed_max_7d` | float | $\ge 0.0$ km/h | Maximum wind speed along corridor over past 7 days | Shifted by 1 day |
| `label_7d` | float | $0.0, 1.0, \text{NaN}$ | Actual delivery days $>$ scheduled days in $(t+1, t+7]$ | Future outcome; NaN for $t >$ 2025-10-24 |
