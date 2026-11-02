"""FastAPI Verification & API Contract Test Suite.

Tests all 5 endpoints:
  - GET /api/risks
  - GET /api/reasons
  - GET /api/network-score
  - GET /api/alerts
  - GET /api/metrics

Verifies status codes, JSON schema compliance, and CORS configuration.
"""
import os
import sys
from pathlib import Path
from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.api.main import app


def test_api_endpoints():
    client = TestClient(app)

    print("--> Testing GET / ...")
    r = client.get("/")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert r.json().get("status") == "online"
    print("    PASS: Root endpoint responded.")

    print("--> Testing GET /api/risks ...")
    r = client.get("/api/risks")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), "Expected list of risks"
    assert len(data) > 0, "Empty risks response"
    item = data[0]
    for key in ("entity_id", "entity_type", "date", "risk_type", "probability", "level"):
        assert key in item, f"Missing key {key} in risk item"
    print(f"    PASS: /api/risks returned {len(data)} items. Sample: {item['entity_id']} -> {item['level']}")

    print("--> Testing GET /api/reasons ...")
    r = client.get("/api/reasons?entity_id=SUP001&risk_type=supplier")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    reason_data = r.json()
    for key in ("entity_id", "risk_type", "top3_reasons", "shap_breakdown"):
        assert key in reason_data, f"Missing key {key} in reason response"
    assert len(reason_data["top3_reasons"]) > 0, "No top reasons found"
    assert len(reason_data["shap_breakdown"]) > 0, "No shap breakdown found"
    print(f"    PASS: /api/reasons returned top reasons: {reason_data['top3_reasons'][:2]}")

    print("--> Testing GET /api/network-score ...")
    r = client.get("/api/network-score")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    net_data = r.json()
    for key in ("date", "network_risk_score", "level", "weights_assumption"):
        assert key in net_data, f"Missing key {key} in network score"
    assert 0.0 <= net_data["network_risk_score"] <= 1.0, "Network score out of range"
    print(f"    PASS: /api/network-score returned score {net_data['network_risk_score']} ({net_data['level']})")

    print("--> Testing GET /api/alerts ...")
    r = client.get("/api/alerts?entity_id=SUP001")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    alert_data = r.json()
    for key in ("entity_id", "risk_level", "recommended_actions", "alert_summary"):
        assert key in alert_data, f"Missing key {key} in alert response"
    assert len(alert_data["recommended_actions"]) > 0, "No recommended actions"
    print(f"    PASS: /api/alerts returned {len(alert_data['recommended_actions'])} actions. Summary: {alert_data['alert_summary'][:60]}...")

    print("--> Testing GET /api/metrics ...")
    r = client.get("/api/metrics")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    metric_data = r.json()
    assert isinstance(metric_data, list), "Expected list of metrics"
    assert len(metric_data) > 0, "Empty metrics response"
    for m in metric_data:
        for k in ("model", "risk_type", "pr_auc", "recall", "f1", "is_baseline"):
            assert k in m, f"Missing key {k} in metric item"
    print(f"    PASS: /api/metrics returned {len(metric_data)} comparison rows.")

    print("--> Testing GET /api/forecast ...")
    r = client.get("/api/forecast")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    forecast_data = r.json()
    assert len(forecast_data) > 0, "Empty forecast response"
    for k in ("entity_id", "date", "forecast_demand", "demand_surge_flag"):
        assert k in forecast_data[0], f"Missing key {k} in forecast item"
    print(f"    PASS: /api/forecast returned {len(forecast_data)} predictions.")

    print("--> Testing GET /api/anomalies ...")
    r = client.get("/api/anomalies")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    anom_data = r.json()
    assert len(anom_data) > 0, "Empty anomaly response"
    for k in ("entity_id", "date", "risk_type", "anomaly_score", "anomaly_flag"):
        assert k in anom_data[0], f"Missing key {k} in anomaly item"
    print(f"    PASS: /api/anomalies returned {len(anom_data)} anomaly records.")

    print("--> Testing GET /api/demos ...")
    r = client.get("/api/demos")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    demo_dict = r.json()
    assert "case_1_high_supplier_risk" in demo_dict
    assert "case_2_stockout" in demo_dict
    assert "case_3_low_risk" in demo_dict
    print(f"    PASS: /api/demos returned verified demo cases dictionary.")

    print("--> Testing 404 on non-existent entity for /api/alerts ...")
    r = client.get("/api/alerts?entity_id=NON_EXISTENT_ENTITY")
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"
    print("    PASS: /api/alerts correctly returns 404 for unknown entity.")

    print("--> Testing CORS Headers for http://localhost:5173 ...")
    cors_resp = client.options(
        "/api/risks",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    # Status can be 200 or have access-control-allow-origin
    get_resp = client.get("/api/risks", headers={"Origin": "http://localhost:5173"})
    assert get_resp.headers.get("access-control-allow-origin") in ("*", "http://localhost:5173"), "CORS origin header missing"
    print("    PASS: CORS header 'access-control-allow-origin' confirmed for http://localhost:5173.")

    print("\n=== ALL FASTAPI CONTRACT TESTS PASSED! ===")


if __name__ == "__main__":
    test_api_endpoints()
