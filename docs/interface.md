# Shared interface (v1)

Agreed by Members 1, 2, 3. Until real files arrive, everyone works on the dummy files
made by `python -m src.data.make_dummy`, which follow exactly this format.
A sender who must change a column tells the receiver BEFORE pushing.

## Keys and window

- Every table has `entity_type` (`supplier` / `plant` / `warehouse` / `route`), `entity_id`, `date`.
- `date` is ISO `YYYY-MM-DD`, one row per entity per day.
- Window: 2025-04-01 to 2025-10-31.
- `split` column on every table: `train` = Apr-Aug, `val` = Sep, `test` = Oct.
- Entity ids: `SUP001..`, `PLT001..`, `WH001..`, `RT001..`.

## Risk types and entity mapping

| risk_type | entity_type |
|---|---|
| supplier_failure | supplier |
| manufacturing_delay | plant |
| warehouse_stockout | warehouse |
| transport_disruption | route |

## Leakage rules

1. Drop `Late_delivery_risk`, delivery status and actual shipping days from DataCo.
2. All rolling features use past days only (shift by 1 day).
3. Every imputer, Isolation Forest, TF-IDF and forecaster is fitted on the train period only.
4. Missing delivery dates (e.g. cancelled orders) stay missing. Do not fill.

## Out-of-fold rule

Any base-model score fed to CatBoost must be out-of-fold for train rows, using
time-ordered folds. Val and test rows use the model fitted on the full train period.

## File table

| File | Made by | Used by | Key columns |
|---|---|---|---|
| `features_supplier / manufacturing / warehouse / transport .parquet` | M1 | M2, M3 | entity_type, entity_id, date, split, label_7d, rolling features |
| `graph_scores.parquet` | M1 | M3 | entity_id, dependency_count, hgt_score, route_importance |
| `gdelt_headlines.parquet` | M2 | M1 | date, title, country, city, theme, tone |
| `news_scores.parquet` | M2 | M1, M3 | entity_id, date, text_risk, text_risk_7d, disruption_type, tone |
| `anomaly_scores.parquet` | M2 | M3 | entity_id, date, risk_type, anomaly_score, anomaly_flag, if_baseline_score |
| `forecast_scores.parquet` | M3 | M3 | entity_id, date, forecast_demand, forecast_gap, demand_surge_flag, chronos_forecast, patchtst_delay_forecast |
| `predictions.csv` | M3 | M2 (API) | entity_id, date, risk_type, probability, level |
| `shap_values.parquet`, `reasons.csv` | M3 | M2 (API) | entity_id, date, risk_type, feature, shap_value, top3_reasons |
| `metrics.csv` | M2, M3 | everyone | model, risk_type, pr_auc, recall, f1, is_baseline |

Location: parquet files in `data/processed/`; predictions, SHAP and metrics in `outputs/`.
Version in the name when handing over, e.g. `features_supplier_v1.parquet`, `_v2`.

## Levels

`level` is one of `Low`, `Medium`, `High`. Starting cut-offs: Low < 0.30, Medium 0.30-0.60,
High >= 0.60. Tuned on the validation set by M3.

## Deadlines

Handovers 7, 8 and 15 are critical. Raise any delay in the group chat straight away.
