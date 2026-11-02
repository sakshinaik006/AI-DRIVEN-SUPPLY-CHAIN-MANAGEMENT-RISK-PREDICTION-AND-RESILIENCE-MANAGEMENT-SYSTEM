"""End-to-End Pipeline Integrity & Correctness Test Suite.

Verifies the audited and rectified machine learning, statistical forecasting,
anomaly detection, TreeSHAP explainability, decision layer, and FastAPI serving pipeline.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs"
PROC_DIR = ROOT / "data" / "processed"


def test_27_entity_prediction_coverage():
    """Verify that predictions.csv covers all 27 physical entities and 4 operational risk tiers."""
    pred_path = OUT_DIR / "predictions.csv"
    assert pred_path.exists(), "outputs/predictions.csv must exist."
    df = pd.read_csv(pred_path)

    expected_entities = (
        [f"SUP00{i}" for i in range(1, 9)]
        + [f"PLT00{i}" for i in range(1, 5)]
        + [f"WH00{i}" for i in range(1, 6)]
        + [f"RT{i:03d}" for i in range(1, 11)]
    )
    assert len(expected_entities) == 27
    actual_entities = set(df["entity_id"].unique())
    for e in expected_entities:
        assert e in actual_entities, f"Missing entity {e} in predictions.csv"

    # Total rows: 27 entities * 214 simulation days = 5,778 rows
    assert len(df) == 5778, f"Expected 5,778 prediction rows, got {len(df)}"

    # Check probability bounds
    assert (df["probability"] >= 0.0).all() and (df["probability"] <= 1.0).all(), (
        "Probabilities out of bounds [0, 1]"
    )

    # Check risk types
    expected_risk_types = {
        "supplier_failure",
        "manufacturing_delay",
        "warehouse_stockout",
        "transport_disruption",
    }
    assert set(df["risk_type"].unique()) == expected_risk_types


def test_leak_free_labels_in_features():
    """Verify that lookahead labels (label_7d) for unobserved period Oct 25-31 are strictly NaN."""
    tier_files = [
        "features_supplier_v1.parquet",
        "features_manufacturing_v1.parquet",
        "features_warehouse_v1.parquet",
        "features_transport_v1.parquet",
    ]
    for tf in tier_files:
        fpath = PROC_DIR / tf
        assert fpath.exists(), f"{tf} missing from data/processed"
        df = pd.read_parquet(fpath)
        unobserved = df[df["date"] >= "2025-10-25"]
        assert len(unobserved) > 0, f"No unobserved rows found in {tf}"
        assert unobserved["label_7d"].isna().all(), (
            f"Leakage detected! unobserved period in {tf} has non-NaN label_7d values"
        )


def test_shap_and_reasons_integrity():
    """Verify SHAP attributions and reasons align with deployed models and feature columns."""
    shap_path = OUT_DIR / "shap_values.parquet"
    reasons_path = OUT_DIR / "reasons.csv"
    assert shap_path.exists(), "shap_values.parquet missing"
    assert reasons_path.exists(), "reasons.csv missing"

    df_shap = pd.read_parquet(shap_path)
    df_reasons = pd.read_csv(reasons_path)

    assert len(df_shap) == 25252, f"Expected 25,252 SHAP attribution rows, got {len(df_shap)}"
    assert len(df_reasons) == 5778, f"Expected 5,778 top3 reason records, got {len(df_reasons)}"

    # Ensure no NaN shap values
    assert not df_shap["shap_value"].isna().any(), "NaN found in shap_value"
    # Ensure all top3_reasons are non-empty strings
    assert not df_reasons["top3_reasons"].isna().any(), "NaN found in top3_reasons"


def test_network_score_weight_and_bound_validation():
    """Verify compute_network_risk validates weights and input domains."""
    from src.decision.network_score import compute_network_risk

    # Normal valid execution
    res = compute_network_risk(
        supplier_prob=0.45,
        manufacturing_prob=0.30,
        stockout_prob=0.20,
        transport_prob=0.25,
        external_score=0.15,
    )
    assert 0.0 <= res["network_risk"] <= 1.0
    assert res["level"] in ("Low", "Medium", "High")

    # Invalid weights sum
    with pytest.raises(ValueError, match="Weights must sum to 1.0"):
        compute_network_risk(
            0.5, 0.5, 0.5, 0.5, 0.5,
            weights={"supplier": 0.5, "manufacturing": 0.5, "stockout": 0.5, "transport": 0.5, "external": 0.5}
        )

    # Invalid probability range (> 1.0)
    with pytest.raises(ValueError, match="out of valid range"):
        compute_network_risk(1.5, 0.2, 0.2, 0.2, 0.1)


def test_recommendations_suppression_and_prescriptions():
    """Verify prescriptive resilience recommendations logic."""
    from src.decision.recommendations import generate_recommendations

    # Low risk / safe operating node must be suppressed
    low_recs = generate_recommendations(
        risk_type="supplier_failure",
        level="Low",
        entity_id="SUP008",
        probability=0.08,
    )
    assert len(low_recs) == 1
    assert low_recs[0]["action_type"] == "Operational Notice"
    assert low_recs[0]["priority"] == "Normal"

    # High risk node must receive prescriptive action
    high_recs = generate_recommendations(
        risk_type="supplier_failure",
        level="High",
        entity_id="SUP001",
        probability=0.82,
    )
    assert len(high_recs) >= 2
    assert all(r["action_type"] == "Prescriptive Mitigation" for r in high_recs)
    assert high_recs[0]["priority"] == "Critical"
    assert "switch purchase allocation" in high_recs[0]["action"]


def test_fastapi_full_endpoints():
    """Verify FastAPI backend endpoints return contract-compliant status and schemas."""
    from src.api.main import app
    client = TestClient(app)

    # 1. /api/risks
    r = client.get("/api/risks")
    assert r.status_code == 200
    risks = r.json()
    assert len(risks) == 27
    assert all(0.0 <= item["probability"] <= 1.0 for item in risks)

    # 2. /api/reasons
    r = client.get("/api/reasons?entity_id=SUP001&risk_type=supplier")
    assert r.status_code == 200
    reasons = r.json()
    assert len(reasons["top3_reasons"]) > 0
    assert len(reasons["shap_breakdown"]) > 0

    # 3. /api/network-score
    r = client.get("/api/network-score")
    assert r.status_code == 200
    net = r.json()
    assert 0.0 <= net["network_risk_score"] <= 1.0
    assert net["level"] in ("LOW", "MEDIUM", "HIGH")

    # 4. /api/alerts
    r = client.get("/api/alerts?entity_id=SUP001")
    assert r.status_code == 200
    alert = r.json()
    assert len(alert["recommended_actions"]) > 0

    # 5. /api/metrics
    r = client.get("/api/metrics")
    assert r.status_code == 200
    metrics = r.json()
    assert len(metrics) == 22
    for m in metrics:
        assert "model" in m and "risk_type" in m and "pr_auc" in m
