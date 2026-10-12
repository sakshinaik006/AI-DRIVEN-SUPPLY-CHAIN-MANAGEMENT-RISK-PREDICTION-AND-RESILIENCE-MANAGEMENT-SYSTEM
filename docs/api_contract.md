# FastAPI Backend & React Frontend API Contract

Base URL: `http://localhost:8000/api`[cite: 2, 4, 7]

## Endpoints

### 1. `GET /api/risks`
- **Purpose**: Fetch latest predicted probabilities and discrete risk levels across all entities[cite: 2, 4, 7].
- **Query Parameters**:
  - `date` (optional, string: `YYYY-MM-DD`): Defaults to current simulation date.
  - `risk_type` (optional, string): `supplier` | `manufacturing` | `warehouse` | `transport`[cite: 2, 7].
- **Response Format**:
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
