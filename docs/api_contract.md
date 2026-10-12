# API contract (FastAPI, JSON) v1

Owner: Member 2. Consumer: Member 1 (React). Dev server enables CORS for
`http://localhost:5173` (Vite). Swagger at `/docs`.

Common query params: `entity_id` (optional), `date` (optional, default = latest date).

## GET /api/risks

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

## GET /api/reasons

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

## GET /api/network-score

Computed by `src/decision/network_score.py` (weights are assumptions).

```json
{
  "date": "2025-10-31",
  "network_risk": 0.58,
  "level": "Medium",
  "components": {"supplier": 0.64, "manufacturing": 0.50, "stockout": 0.55, "transport": 0.60, "external": 0.45},
  "weights_are_assumptions": true
}
```

## GET /api/alerts

LLM-written text with a template fallback if the LLM is unavailable.

```json
[
  {
    "entity_id": "SUP001",
    "risk_type": "supplier_failure",
    "level": "High",
    "message": "Supplier risk is HIGH mainly because of high recent delays and negative news.",
    "actions": ["Switch to an alternate supplier"],
    "source": "llm"
  }
]
```

`source` is `llm` or `template`.

## GET /api/metrics

```json
[
  {"model": "catboost_multitarget", "risk_type": "supplier_failure", "pr_auc": 0.71, "recall": 0.68, "f1": 0.66, "is_baseline": false}
]
```

## Fallback

If the API is not ready, React reads static JSON with the same shapes from
`frontend/public/` (`risks.json`, `reasons.json`, `network-score.json`, `alerts.json`, `metrics.json`).
