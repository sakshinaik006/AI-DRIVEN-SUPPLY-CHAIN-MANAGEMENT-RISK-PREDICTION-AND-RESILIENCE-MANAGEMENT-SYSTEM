# Real vs. Synthetic Data Disclosure & Assumptions

**System:** AI-Driven Supply Chain Risk Prediction and Resilience Management Platform  
**Owner:** Member 1 — Data, Graph, and React Dashboard Engineer  
**Date:** 2026-10-13  

---

## 1. Prototype Scope and Evaluation Context

> [!IMPORTANT]
> The performance metrics, risk predictions, and evaluation tables produced in this system demonstrate that the **end-to-end multi-echelon predictive pipeline functions correctly**, rather than certifying real-world operational accuracy of an actual commercial smartphone supply chain.

Because enterprise supply chain operational records (factory downtime, supplier contracts, component breakdowns, warehouse stock levels) are commercially confidential, this prototype utilizes a combination of **real external datasets** and **realistic synthetic simulations**.

---

## 2. Real Data Sources

The following external datasets are real observations:

1. **DataCo Global Supply Chain Dataset (Kaggle):**
   - **Scope:** Filtered exclusively to `Category Name == 'Electronics'` (811 transaction records).
   - **Date Window Adjustment:** Original transaction timestamps from 2015–2018 were systematically calendar-shifted into the prototype window (**2025-04-01 to 2025-10-31**).
   - **Leakage Prevention:** Post-delivery outcome variables (`Late_delivery_risk`, `Delivery Status`, `Days for shipping (real)`) were strictly excluded from model feature sets.

2. **Open-Meteo Historical Weather Reanalysis (API):**
   - **Scope:** Daily meteorological observations pulled across all 27 supply network locations (8 suppliers, 4 assembly plants, 5 distribution warehouses, and 10 transport route lane midpoints).
   - **Variables:** Daily precipitation sum (`precipitation_mm`), maximum 10-meter wind speed (`max_wind_speed_kmh`), and weather severity flags (`extreme_weather_flag`).
   - **Dates:** Complete coverage from 2025-04-01 to 2025-10-31 (5,778 daily records).

3. **Geographic Coordinates and Cities:**
   - Real geographic latitudes, longitudes, countries, and city names (Hsinchu, Seoul, Shenzhen, Dongguan, Pune, Chennai, Noida, Bac Ninh, Rotterdam, Los Angeles, Dubai, Singapore) to ensure authentic spatial modeling and news/weather linking.

---

## 3. Synthetic Data Sources

The following master entities and operational time series are synthetically modeled using a seeded random generator (`seed = 42`):

1. **Master Structure:**
   - Fictional smartphone BOM (Application processor C001, OLED panel C002, Memory C003, Battery C004, Camera module C005, Housing C006).
   - 5 smartphone product tiers (Phone Lite, Core, Core Plus, Pro, Max).
   - Plant assembly capacities and warehouse safety stock units.

2. **Daily Operational Logs & Causal Chains:**
   - **Supplier Deliveries:** Daily dispatches with realistic Poisson delivery delays, defect percentages, and extreme weather-induced disruption events.
   - **Plant Production:** Daily planned vs. actual output units and equipment downtime hours.
   - **Warehouse Inventory:** Dynamic inventory replenishment simulation with sudden demand surges.
   - **Transport Shipments:** Lane transit times, shipping modes (air, sea, road), and route congestion delays.

3. **Label Calibration:**
   - 7-day-ahead binary targets are calibrated to maintain realistic positive label distributions between **3% and 5%** across train, validation, and test partitions, preventing degenerate class-imbalance failure.

---

## 4. Key Modeling Assumptions

1. **Network Risk Weighting:**
   - Composite Network Risk = `0.25 * Supplier + 0.25 * Manufacturing + 0.20 * Stockout + 0.20 * Transport + 0.10 * External`.
   - These weights are designated as **assumptions** reflecting an illustrative balanced executive dashboard, customizable per enterprise SLA.

2. **Leakage Elimination Rule:**
   - All rolling time-series features are computed over past history only (`shift(1)`), preventing observation leakage.
   - Outcomes from October 25–31 are designated `NaN` because their complete 7-day lookahead window exceeds the dataset boundary.
