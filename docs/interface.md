# Shared Pipeline Interface & Data Contract

## Common Key Standard
- **Primary Composite Keys**: All entity-level parquet files use `entity_type` (`supplier` / `plant` / `warehouse` / `route`), `entity_id`, and `date`.
- **Date Range**: 1 April 2025 to 31 October 2025 (214 simulation days).
- **Time Splits**:
  - **Train**: 1 April 2025 – 24 August 2025 (`split = "train"`)
  - **Purge Gap 1**: 25 August 2025 – 31 August 2025 (`split = "purge"`)
  - **Validation**: 1 September 2025 – 23 September 2025 (`split = "val"`)
  - **Purge Gap 2**: 24 September 2025 – 30 September 2025 (`split = "purge"`)
  - **Test (Held-out)**: 1 October 2025 – 31 October 2025 (`split = "test"`, labels valid through 24 October)

## Shared Data Deliverables Schema

| File Path | Pipeline Stage | Downstream Consumer | Key Columns | Description |
| :--- | :--- | :--- | :--- | :--- |
| `data/raw/weather.parquet` | Weather Acquisition | Feature Engineering | `entity_id`, `date`, `precipitation_mm`, `max_wind_speed_kmh`, `extreme_weather_flag` | Daily weather pulled from Open-Meteo ERA5 for all 27 entity locations. |
| `data/processed/features_supplier.parquet` | Feature Engineering | Stacking & CatBoost | `entity_type`, `entity_id`, `date`, `split`, `label_7d`, `delay_7d_avg`, `news_tone_14d_trend` | Cleaned supplier features with 7-day lookahead target. |
| `data/processed/features_manufacturing.parquet` | Feature Engineering | Stacking & CatBoost | `entity_type`, `entity_id`, `date`, `split`, `label_7d`, `production_shortfall_7d` | Manufacturing plant features. |
| `data/processed/features_warehouse.parquet` | Feature Engineering | Stacking & CatBoost | `entity_type`, `entity_id`, `date`, `split`, `label_7d`, `demand_7d_avg`, `stock_level` | Warehouse inventory features. |
| `data/processed/features_transport.parquet` | Feature Engineering | Stacking & CatBoost | `entity_type`, `entity_id`, `date`, `split`, `label_7d`, `delivery_delay_7d_avg`, `rain_7d_avg` | Transport route delay features. |
| `data/processed/graph_scores.parquet` | Graph Modeling | Stacking & CatBoost | `entity_id`, `dependency_count`, `hgt_score`, `route_importance` | Network topology centrality metrics output from NetworkX. |
| `data/raw/gdelt_headlines.parquet` | GDELT Ingestion | NLP Pipeline | `date`, `title`, `country`, `city`, `theme`, `tone` | Filtered geopolitical and logistics news headlines. |
| `data/processed/news_scores.parquet` | NLP & Sentiment | Feature Engineering | `entity_id`, `date`, `text_risk`, `text_risk_7d`, `disruption_type`, `tone` | Continuous NLP risk scores and NER entity linking. |
| `data/processed/anomaly_scores.parquet` | Anomaly Detection | Meta-Learner Stacking | `entity_id`, `date`, `risk_type`, `anomaly_score`, `anomaly_flag`, `if_baseline_score` | Extended Isolation Forest and baseline Isolation Forest scores. |
| `data/processed/forecast_scores.parquet` | Demand Forecasting | Inventory Management | `entity_id`, `date`, `forecast_demand`, `forecast_gap`, `demand_surge_flag` | Warehouse demand forecasts and surge indicators. |
| `outputs/predictions.csv` | CatBoost Stacking | API & Dashboard | `entity_id`, `date`, `risk_type`, `probability`, `level` | Multi-target predictions and discrete risk classifications. |
| `outputs/shap_values.parquet` | TreeSHAP Engine | API & Dashboard | `entity_id`, `date`, `risk_type`, `feature`, `shap_value` | Exact TreeSHAP feature attributions per observation. |
| `outputs/reasons.csv` | Explainability Engine | API & Dashboard | `entity_id`, `date`, `risk_type`, `top3_reasons` | Human-readable top-3 root-cause disruption drivers. |

## Data Leakage Prevention Directives
- **Shift Rule**: All time-series rolling aggregations must strictly use past information (`shift(1)` relative to prediction date `t`).
- **Exclusion Rule**: Drop `Late_delivery_risk`, actual shipping days, and actual arrival dates from model feature sets.
- **Fitting Boundary**: All imputers, scalers, Isolation Forests, TF-IDF vectorizers, and forecasting models must be fitted exclusively on the `train` split.
