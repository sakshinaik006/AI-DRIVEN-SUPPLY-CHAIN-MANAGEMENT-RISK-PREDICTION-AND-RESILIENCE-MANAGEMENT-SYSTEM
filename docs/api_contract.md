# API contract (FastAPI, JSON) v1.1

Owner: Member 2. Consumer: Member 1 (React).
Dev server enables CORS for `http://localhost:5173` and `http://127.0.0.1:5173` (Vite).
Swagger at `/docs`. All responses are JSON. Dates are ISO `YYYY-MM-DD`.
Probabilities are floats between 0 and 1. `level` is `Low`, `Medium` or `High`
(cut-offs from `outputs/levels.json`).

## Common query params

| Param | Meaning |
|---|---|
| `entity_id` | optional, e.g. `SUP001` |
| `risk_type` | optional: `supplier_failure`, `manufacturing_delay`, `warehouse_stockout`, `transport_disruption` |
| `date` | optional, default = latest date (2025-10-31) |

## Errors

Unknown `entity_id`, `risk_type` or a date outside the window returns HTTP 404 with
`{"detail": "message"}`. An empty result for valid params returns `[]`.

## GET /api/health

```json
{"status": "ok", "data_source": "real", "latest_date": "2025-10-31"}
```

`data_source` is `dummy` until the final API is connected to real data.

## GET /api/entities

List of all entities for the map and filters.

```json
[
  {
    "entity_type": "supplier",
    "entity_id": "SUP001",
    "name": "Supplier 1",
    "country": "India",
    "city": "Pune",
    "lat": 18.52,
    "lon": 73.86
  }
]
```

## GET /api/risks

Supports `entity_id`, `risk_type`, `date`.

```json
[
  {
    "entity_type": "supplier",
    "entity_id": "SUP001",
    "date": "2025-10-31",
    "risk_type": "supplier_failure",
    "probability": 0.64,
    "level": "High"
  }
]
```

`entity_type` is derived from `risk_type`.

## GET /api/history

Time series for trend charts. Requires `entity_id` and `risk_type`.
Optional `from` and `to` dates. Rows with `split = purge` are included.

```json
[
  {"date": "2025-10-29", "probability": 0.41, "level": "Medium"},
  {"date": "2025-10-30", "probability": 0.55, "level": "Medium"},
  {"date": "2025-10-31", "probability": 0.64, "level": "High"}
]
```

## GET /api/reasons

Top 3 reasons per prediction.

```json
[
  {
    "entity_id": "SUP001",
    "date": "2025-10-31",
    "risk_type": "supplier_failure",
    "base_value": -2.94,
    "raw_score": 0.56,
    "reasons": [
      {"feature": "supplier_delay_7d_avg", "shap_value": 1.80},
      {"feature": "news_tone_14d_trend", "shap_value": 1.10},
      {"feature": "single_source_flag", "shap_value": 0.60}
    ]
  }
]
```

- `raw_score` is the log-odds. `probability = 1 / (1 + exp(-raw_score))`.
- `base_value` plus the sum of ALL SHAP values equals `raw_score`. `reasons` lists only the
  top 3; the full set is in `outputs/shap_values.parquet`. The example above is illustrative.

## GET /api/network-score

Computed by `src/decision/network_score.py` (weights are assumptions).

```json
{
  "date": "2025-10-31",
  "network_risk": 0.58,
  "level": "Medium",
  "components": {
    "supplier": 0.64,
    "manufacturing": 0.50,
    "stockout": 0.55,
    "transport": 0.60,
    "external": 0.45
  },
  "weights_are_assumptions": true
}
```

`external` = mean of the extreme-weather flag rate and the news-tone risk over the last
7 days (Member 1 assumption; labeled as such in the report).

## GET /api/alerts

LLM-written text with a template fallback if the LLM is unavailable.
Supports `entity_id`, `risk_type`, `level`, `date`.

```json
[
  {
    "entity_type": "supplier",
    "entity_id": "SUP001",
    "date": "2025-10-31",
    "risk_type": "supplier_failure",
    "level": "High",
    "probability": 0.64,
    "message": "Supplier risk is HIGH mainly because of high recent delays and negative news.",
    "actions": ["Switch to an alternate supplier"],
    "source": "llm"
  }
]
```

`source` is `llm` or `template`. The LLM key stays on the server in `.env`; React never sees it.

## GET /api/metrics

Final numbers; must match `outputs/metrics.csv` and the report.

```json
[
  {
    "model": "catboost_multitarget",
    "risk_type": "supplier_failure",
    "split": "test",
    "pr_auc": 0.71,
    "precision": 0.64,
    "recall": 0.68,
    "f1": 0.66,
    "is_baseline": false
  }
]
```

Baseline rows have `"is_baseline": true`.

## Fallback

If the API is not ready, React reads static JSON with the same shapes from
`frontend/public/`: `risks.json`, `reasons.json`, `network-score.json`, `alerts.json`,
`metrics.json`, `entities.json`, `history.json`.

## Checks

- Handover 14: the React app reads `/api/risks` from the dev server with no CORS errors.
- Handover 19: every dashboard panel shows real values, and `/api/health` reports
  `"data_source": "real"`.
