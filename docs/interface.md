# Shared Pipeline Interface & Data Contract

## Common Key Standard
- **Primary Composite Keys**: All entity-level parquet files use `entity_type` (supplier / plant / warehouse / route), `entity_id`, and `date`.
- **Date Range**: 1 April 2025 to 31 October 2025.
- **Time Splits**:
  - Train: 1 April 2025 – 31 August 2025 (`split = "train"`)
  - Validation: 1 September 2025 – 30 September 2025 (`split = "val"`)
  - Test: 1 October 2025 – 31 October 2025 (`split = "test"`)

## Shared Data Deliverables Schema

| File Path | Producer | Consumer | Key Columns | Description |
| :--- | :--- | :--- | :--- | :--- |
| `data/raw/weather.parquet` | Member 1 | Member 3 | `entity_id`, `date`, `precipitation_mm`, `max_wind_speed_kmh`, `extreme_weather_flag` | Daily weather pulled from Open-Meteo for supplier, plant, and warehouse locations[cite: 2, 7]. |
| `data/processed/features_supplier.parquet` | Member 1 | Members 2, 3 | `entity_type`, `entity_id`, `date`, `split`, `label_7d`, `delay_7d_avg`, `news_tone_14d_trend` | Cleaned supplier features with 7-day lookahead target[cite: 2, 4, 7]. |
| `data/processed/features_manufacturing.parquet` | Member 1 | Members 2, 3 | `entity_type`, `entity_id`, `date`, `split`, `label_7d`, `production_shortfall_7d` | Manufacturing plant features[cite: 2, 4, 7]. |
| `data/processed/features_warehouse.parquet` | Member 1 | Members 2, 3 | `entity_type`, `entity_id`, `date`, `split`, `label_7d`, `demand_7d_avg`, `stock_level` | Warehouse inventory features[cite: 2, 4, 7]. |
| `data/processed/features_transport.parquet` | Member 1 | Members 2, 3 | `entity_type`, `entity_id`, `date`, `split`, `label_7d`, `delivery_delay_7d_avg`, `rain_7d_avg` | Transport route delay features[cite: 2, 4, 7]. |
| `data/processed/graph_scores.parquet` | Member 1 | Member 3 | `entity_id`, `dependency_count`, `hgt_score`, `route_importance` | Graph network metrics output from NetworkX and PyTorch Geometric HGT[cite: 2, 4, 7]. |
| `data/raw/gdelt_headlines.parquet` | Member 2 | Member 1 | `date`, `title`, `country`, `city`, `theme`, `tone` | Filtered GDELT news articles[cite: 4, 7]. |
| `data/processed/news_scores.parquet` | Member 2 | Members 1, 3 | `entity_id`, `date`, `text_risk`, `text_risk_7d`, `disruption_type`, `tone` | DeBERTa-v3 risk scores and NER linked entity scores[cite: 4, 7]. |
| `data/processed/anomaly_scores.parquet` | Member 2 | Member 3 | `entity_id`, `date`, `risk_type`, `anomaly_score`, `anomaly_flag`, `if_baseline_score` | Extended Isolation Forest and baseline Isolation Forest scores[cite: 4, 7]. |
| `data/processed/forecast_scores.parquet` | Member 3 | Member 3 | `entity_id`, `date`, `forecast_demand`, `forecast_gap`, `demand_surge_flag`, `chronos_forecast`, `patchtst_delay_forecast` | Demand and transit delay zero-shot forecasts (Chronos-2 / PatchTST / ETS)[cite: 4, 7]. |
| `outputs/predictions.csv` | Member 3 | Member 1, 2 | `entity_id`, `date`, `risk_type`, `probability`, `level` | Final multi-target predictions (Low / Medium / High)[cite: 4, 7]. |
| `outputs/shap_values.parquet` | Member 3 | Member 1, 2 | `entity_id`, `date`, `risk_type`, `feature`, `shap_value` | TreeSHAP exact explanation values per sample[cite: 4, 7]. |
| `outputs/reasons.csv` | Member 3 | Member 1, 2 | `entity_id`, `date`, `risk_type`, `top3_reasons` | Generated top 3 explanation drivers in readable text[cite: 4, 7]. |

## Data Leakage Prevention Directives
- **Shift Rule**: All time-series rolling aggregations must strictly use past information (`shift(1)` relative to prediction date `t`)[cite: 2, 4, 7].
- **Exclusion Rule**: Drop `Late_delivery_risk`, actual shipping days, and actual arrival dates from model feature sets[cite: 2, 4, 7].
- **Fitting Boundary**: All imputers, scalers, Isolation Forests, TF-IDF vectorizers, and forecasting models must be fitted exclusively on the `train` split[cite: 4, 7].
