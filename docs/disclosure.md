# Real vs. Synthetic Data Disclosure & Assumptions

**System:** AI-Driven Supply Chain Risk Prediction and Resilience Management Platform  
**Owner:** Senior ML & Backend Engineering Auditor  
**Date:** 2026-11-02  
**Status:** Fully Audited, Rectified & Verified  

---

## 1. Prototype Scope and Evaluation Context

> [!IMPORTANT]
> The performance metrics, risk predictions, and evaluation tables produced in this system demonstrate that the **end-to-end multi-echelon predictive pipeline functions correctly**, rather than certifying real-world operational accuracy of an actual commercial smartphone supply chain.
>
> All dates, historical records, and synthetic simulations are strictly scoped to the benchmark simulation period (**2025-04-01 to 2025-10-31**). Historical records date-shifted into this window are explicitly marked as prototype benchmark data and must NOT be described as genuine 2025 operational observations.

Because enterprise supply chain operational records (factory downtime, supplier contracts, component breakdowns, warehouse stock levels) are commercially confidential, this system utilizes a combination of **real external datasets** and **realistic synthetic simulations**.

---

## 2. Real External Data Sources

The following external datasets are real observations:

1. **DataCo Global Supply Chain Dataset (Kaggle):**
   - **Scope:** Filtered exclusively to `Category Name == 'Electronics'` (811 transaction records).
   - **Date Window Adjustment:** Original transaction timestamps from 2015–2018 were systematically calendar-shifted into the benchmark prototype window (**2025-04-01 to 2025-10-31**).
   - **Clarification:** These are historical 2015–2018 records shifted for prototype benchmarking; they are NOT real 2025 operational data.
   - **Leakage Prevention:** Post-delivery outcome variables (`Late_delivery_risk`, `Delivery Status`, `Days for shipping (real)`) were strictly excluded from model feature sets.

2. **Open-Meteo Historical Weather Reanalysis (API):**
   - **Scope:** Daily meteorological observations pulled across all 27 supply network locations (8 suppliers, 4 assembly plants, 5 distribution warehouses, and 10 transport route lane midpoints).
   - **Variables:** Daily precipitation sum (`precipitation_mm`), maximum 10-meter wind speed (`max_wind_speed_kmh`), and weather severity flags (`extreme_weather_flag`).
   - **Dates:** Complete coverage from 2025-04-01 to 2025-10-31 (5,778 daily records).

3. **Geographic Coordinates and Cities:**
   - Real geographic latitudes, longitudes, countries, and city names (Hsinchu, Seoul, Shenzhen, Dongguan, Pune, Chennai, Noida, Bac Ninh, Rotterdam, Los Angeles, Dubai, Singapore) to ensure authentic spatial modeling and news/weather linking.

---

## 3. Synthetic Data Sources & Modeling

The following master entities and operational time series are synthetically modeled using a seeded random generator (`seed = 42`):

1. **Master Structure:**
   - Smartphone BOM (Application processor C001, OLED panel C002, Memory C003, Battery C004, Camera module C005, Housing C006).
   - 5 smartphone product tiers (Phone Lite, Core, Core Plus, Pro, Max).
   - Plant assembly capacities and warehouse safety stock units.

2. **Daily Operational Logs & Causal Chains:**
   - **Supplier Deliveries:** Daily dispatches with realistic delivery delays, defect percentages, and weather-correlated disruptions.
   - **Plant Production:** Daily planned vs. actual output units and equipment downtime hours.
   - **Warehouse Inventory:** Dynamic inventory replenishment simulation with sudden demand surges.
   - **Transport Shipments:** Lane transit times, shipping modes (air, sea, road), and route congestion delays.

3. **Label Calibration & Lookahead:**
   - 7-day forward-looking binary targets ($t+1$ to $t+7$) calibrated between **3% and 5%** positive rates across train, validation, and test partitions.
   - Purge gaps enforced between splits:
     - Train: 2025-04-01 to 2025-08-24
     - Purge Gap 1: 2025-08-25 to 2025-08-31
     - Validation: 2025-09-01 to 2025-09-23
     - Purge Gap 2: 2025-09-24 to 2025-09-30
     - Test (Held-out): 2025-10-01 to 2025-10-24
     - Unobserved: 2025-10-25 to 2025-10-31 (strictly `NaN` lookahead labels, 189 rows).

---

## 4. Key Modeling & Architectural Assumptions

1. **Network Risk Weighting:**
   - Default Composite Network Risk = `0.25 * Supplier + 0.25 * Manufacturing + 0.20 * Stockout + 0.20 * Transport + 0.10 * External`.
   - Labeled as **heuristic prototype assumptions** reflecting an illustrative balanced executive dashboard.
   - If external news/weather data is unavailable for a given timestamp, operational weights are re-normalized across the observed components (`w_i / 0.90`) rather than falsely deflating the score by assuming 0.0 risk.

2. **Temporal Leakage Elimination:**
   - All rolling feature indicators are strictly shifted by 1 day (`shift(1)`).
   - OOF stacking features (`supplier_failure_prob_oof`, `mfg_delay_prob_oof`) are generated via expanding-window chronological splits with 7-day purge gaps. Static placeholders (`0.05`) have been completely eliminated.

3. **Foundation Forecasting Models (Chronos-2 / PatchTST):**
   - Transformer foundation forecasters (Chronos-2, PatchTST) require specialized GPU infrastructure and external pretrained weights not hosted locally in this repository.
   - In accordance with audit standards, their outputs are documented as **uncomputed / unavailable** (`NaN`) rather than simulated with random-noise proxies.
   - The primary demand forecasting pipeline uses validated Holt-Winters Seasonal Exponential Smoothing and CatBoost time-series regressors trained strictly on the training partition and evaluated out-of-sample on the held-out October split.

4. **Prescriptive Resilience Playbooks:**
   - Prescriptive interventions (e.g. vendor failover, lane rerouting, +15% and +20% buffer threshold adjustments) are **rule-based operational policy heuristics**, NOT empirically validated mathematical optimizations.
   - Recovery times and cost savings are unvalidated estimates and are labeled as such (`is_rule_based_assumption: True`).
   - Low-risk and nominal operating nodes are suppressed from receiving emergency mitigation alerts.
