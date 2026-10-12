# Shared interface (v1.1)

Agreed by Members 1, 2 and 3. Until real files arrive, everyone works on the dummy files
made by `python -m src.data.make_dummy`, which follow exactly this format.
Check any file with `python -m src.data.validate`.

**Change rule:** a sender who must change a column, a key or a value set tells the receiver
BEFORE pushing. Version every handed-over file in its name, e.g. `features_supplier_v1.parquet`, `_v2`.

## 1. Keys and window

- Every **entity-day table** has `entity_type`, `entity_id`, `date`, `split`.
  One row per entity per day (per `risk_type` where the table has that column).
- Exceptions (no entity-day shape):
  - `graph_scores.parquet`: one row per supplier and route, no date.
  - `gdelt_headlines.parquet`: one row per headline.
  - `metrics.csv`: one row per model, risk type and split.
- `entity_type` is one of `supplier`, `plant`, `warehouse`, `route`.
- Entity ids: `SUP001..`, `PLT001..`, `WH001..`, `RT001..` (three or more digits, zero padded).
- `date` is ISO `YYYY-MM-DD`.
- Window: **2025-04-01 to 2025-10-31** (214 days).

## 2. Splits

| `split` | Dates | Use |
|---|---|---|
| `train` | 2025-04-01 to 2025-08-24 | fit models |
| `purge` | 2025-08-25 to 2025-08-31 and 2025-09-24 to 2025-09-30 | excluded from fitting and scoring |
| `val` | 2025-09-01 to 2025-09-23 | tuning, level cut-offs, early stopping |
| `test` | 2025-10-01 to 2025-10-31 | final metrics only |

Why `purge`: a 7-day-ahead label on 28 Aug looks into September (and 28 Sep into October),
so those rows would leak validation/test outcomes into training/validation.

- `purge` rows are still kept in the files. Rolling features may use them as history.
  Never train, tune or score on them.
- In every table the `split` column follows these dates exactly.

## 3. Risk types and entity mapping

| risk_type | entity_type | Table |
|---|---|---|
| `supplier_failure` | supplier | `features_supplier` |
| `manufacturing_delay` | plant | `features_manufacturing` |
| `warehouse_stockout` | warehouse | `features_warehouse` |
| `transport_disruption` | route | `features_transport` |

`entity_type` is not stored in `predictions.csv`; the API derives it from `risk_type`.

## 4. Labels

`label_7d` = 1 if the event happens on **any day from t+1 to t+7**, else 0 (t = the row date).
Definitions (details in `docs/labels.md`):

| risk_type | Event |
|---|---|
| `supplier_failure` | supplier failure |
| `manufacturing_delay` | production below 85% of plan |
| `warehouse_stockout` | stock below safety stock |
| `transport_disruption` | shipment arrives after its scheduled date |

- Target: 3-5% positives per label, checked per split by `validate.py`.
- **2025-10-25 to 2025-10-31 have no label** (`label_7d` is NaN). Keep the rows, but exclude
  them from test metrics.
- No feature may be built from a label column or from events after day t.

## 5. Leakage rules

1. Drop `Late_delivery_risk`, delivery status and actual shipping days from DataCo.
2. All rolling features use past days only: shift by 1 day.
3. Every imputer, Isolation Forest, TF-IDF and forecaster is fitted on `train` only.
4. Missing delivery dates (e.g. cancelled orders) stay missing. Do not fill them.
5. Same-day observed weather at day t may be used as a raw feature; its rolling
   features follow rule 2.
6. Rows with `split = purge` are never used for fitting, tuning or scoring.

## 6. Out-of-fold rule

Any base-model score fed to CatBoost must be out-of-fold for `train` rows, using time-ordered
folds. `val` and `test` rows use the model fitted on the full train period.

## 7. File table

Location: parquet files in `data/processed/` (raw pulls in `data/raw/`); predictions, SHAP,
metrics and levels in `outputs/`.

| File | Made by | Used by | Key columns |
|---|---|---|---|
| `suppliers / plants / warehouses / products / components / routes` (master tables) | M1 | all | entity_id, country, city, lat, lon (+ table specific) |
| `weather.parquet` (raw) | M1 | M3 | entity_type, entity_id, date, precipitation_sum, wind_speed_10m_max, weather_code, extreme_weather_flag, split |
| `agmarknet.parquet` (raw) | M1 | M3 | date, commodity, market, price, split |
| `features_supplier / manufacturing / warehouse / transport .parquet` | M1 | M2, M3 | entity_type, entity_id, date, split, label_7d, rolling features |
| `graph_scores.parquet` | M1 | M3 | entity_id, dependency_count, hgt_score (null until HGT is done), route_importance |
| `gdelt_headlines.parquet` | M2 | M1 | date, title, country, city, theme, tone |
| `news_scores.parquet` | M2 | M1, M3 | entity_id, date, text_risk, text_risk_7d, disruption_type, tone |
| `anomaly_scores.parquet` | M2 | M3 | entity_id, date, risk_type, anomaly_score, anomaly_flag, if_baseline_score |
| `forecast_scores.parquet` | M3 | M3 | entity_id, date, forecast_demand, forecast_gap, demand_surge_flag, chronos_forecast, patchtst_delay_forecast |
| `predictions.csv` | M3 | M2 (API) | entity_id, date, risk_type, probability, level |
| `shap_values.parquet`, `reasons.csv` | M3 | M2 (API) | entity_id, date, risk_type, feature, shap_value, top3_reasons |
| `metrics.csv` | M2, M3 | everyone | model, risk_type, split, pr_auc, precision, recall, f1, is_baseline |
| `levels.json` | M3 | M2 (API), M1 (UI) | low_max, high_min |

Rules for `news_scores` and `anomaly_scores`: `train` rows are out-of-fold (news) or fitted on train only (anomaly).

## 8. Levels

`level` is one of `Low`, `Medium`, `High`.

- Cut-offs live in `outputs/levels.json`, e.g. `{"low_max": 0.30, "high_min": 0.60}`.
  Low if `probability < low_max`, High if `probability >= high_min`, otherwise Medium.
- The values 0.30 and 0.60 are placeholders. M3 tunes them on `val` and publishes the final
  file. The API and the dashboard read this file; nobody hard-codes cut-offs.
- Because positives are only 3-5%, tuned cut-offs will be lower than the placeholders.
  Probabilities are not assumed to be calibrated unless M3 says so in `metrics.csv` notes.

## 9. Reproducibility

- Fixed seeds everywhere (`42` unless stated), relative paths only.
- The pipeline must run from `README.md` on a fresh clone.

## 10. Deadlines

Handovers 7, 8 and 15 are critical. Raise any delay in the group chat straight away.
If a file will be late, push what exists with a note on what is missing.
