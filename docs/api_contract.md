# FastAPI Backend & React Frontend API Contract

**Base URL:** `http://localhost:8000/api`

## Endpoints

### 1. `GET /api/risks`

**Purpose:** Fetch the latest predicted probabilities and discrete risk levels across all entities.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `date` | String (`YYYY-MM-DD`) | No | Defaults to the current simulation date. |
| `risk_type` | String | No | Filter by risk type: `supplier`, `manufacturing`, `warehouse`, or `transport`. |

**Response Format:**

```json
[
  {
    "entity_id": "SUP_001",
    "entity_type": "supplier",
    "date": "2025-10-15",
    "risk_type": "supplier",
    "probability": 0.82,
    "level": "HIGH"
  }
]
```

---

### 2. `GET /api/reasons`

**Purpose:** Retrieve the top TreeSHAP drivers explaining a risk alert.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `entity_id` | String | Yes | Unique identifier of the entity. |
| `risk_type` | String | Yes | Type of risk being explained. |

**Response Format:**

```json
{
  "entity_id": "SUP_001",
  "risk_type": "supplier",
  "top3_reasons": [
    "High 7-day average delivery delay (3.2 days)",
    "Severe weather event flagged at supplier hub",
    "Negative news sentiment score (-0.65)"
  ],
  "shap_breakdown": [
    {
      "feature": "delay_7d_avg",
      "shap_value": 0.35
    },
    {
      "feature": "extreme_weather_flag",
      "shap_value": 0.22
    },
    {
      "feature": "text_risk_7d",
      "shap_value": 0.18
    }
  ]
}
```

---

### 3. `GET /api/network-score`

**Purpose:** Provide a high-level, holistic supply network risk score and component weightings.

**Query Parameters:** None.

**Response Format:**

```json
{
  "date": "2025-10-15",
  "network_risk_score": 0.68,
  "level": "MEDIUM",
  "weights_assumption": {
    "supplier": 0.25,
    "manufacturing": 0.25,
    "stockout": 0.20,
    "transport": 0.20,
    "external": 0.10
  }
}
```

---

### 4. `GET /api/alerts`

**Purpose:** Return recommended mitigation decisions and optional LLM-reformulated alert messages.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `entity_id` | String | Yes | Unique identifier of the entity for which alerts are requested. |

**Response Format:**

```json
{
  "entity_id": "SUP_001",
  "risk_level": "HIGH",
  "recommended_actions": [
    "Switch primary allocation to backup supplier SUP_004",
    "Prioritize high-value customer order fulfillments"
  ],
  "alert_summary": "SUP_001 shows an 82% risk of failure over the next 7 days due to compounding transport delays and localized severe weather."
}
```

---

### 5. `GET /api/metrics`

**Purpose:** Expose October test-set evaluation comparisons between baseline and upgraded pipeline models.

**Query Parameters:** None.

**Response Format:**

```json
[
  {
    "model": "CatBoost Multi-Target",
    "risk_type": "supplier",
    "pr_auc": 0.84,
    "recall": 0.79,
    "f1": 0.81,
    "is_baseline": false
  },
  {
    "model": "Plain CatBoost Baseline",
    "risk_type": "supplier",
    "pr_auc": 0.71,
    "recall": 0.65,
    "f1": 0.68,
    "is_baseline": true
  }
]
```

---

## API Endpoint Summary

| Endpoint | HTTP Method | Primary Function |
|---|---|---|
| `/api/risks` | GET | Retrieve predicted entity risks. |
| `/api/reasons` | GET | Explain risk predictions using TreeSHAP. |
| `/api/network-score` | GET | Retrieve the overall supply network risk score. |
| `/api/alerts` | GET | Retrieve recommended mitigation actions and alert summaries. |
| `/api/metrics` | GET | Compare model evaluation metrics. |

## Implementation Notes

- All endpoints use the base URL `http://localhost:8000/api`.
- All responses use JSON format.
- The `entity_id` and `risk_type` query parameters are required for `/api/reasons`.
- The `entity_id` query parameter is required for `/api/alerts`.
- The `probability`, `network_risk_score`, `pr_auc`, `recall`, `f1`, and `shap_value` fields contain numeric values.
- The `risk_type` field identifies the category of risk being evaluated.
- TreeSHAP values explain individual feature contributions to a model prediction.
- The model evaluation metrics should be calculated from actual test-set results before being reported as validated performance.
- The example dates and response values are illustrative and do not represent confirmed live model outputs.
