"""Unit and integration tests for Member 1 Day 3 decision logic & disclosure:
- network_score.py formula and weights assumption
- recommendations.py prescriptive resilience logic
- disclosure.md existence and required sections
"""
from pathlib import Path
import pytest
from src.decision.network_score import compute_network_risk
from src.decision.recommendations import generate_recommendations

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"


def test_network_score_computation_and_assumptions():
    """Verify formula: 0.25*Sup + 0.25*Mfg + 0.20*Stock + 0.20*Trans + 0.10*Ext."""
    result = compute_network_risk(
        supplier_prob=0.8,
        manufacturing_prob=0.4,
        stockout_prob=0.5,
        transport_prob=0.6,
        external_score=0.2,
    )
    # Expected: 0.25*0.8 + 0.25*0.4 + 0.20*0.5 + 0.20*0.6 + 0.10*0.2
    # = 0.20 + 0.10 + 0.10 + 0.12 + 0.02 = 0.54
    assert result["network_risk"] == 0.54
    assert result["level"] == "Medium"
    assert result["weights_are_assumptions"] is True
    assert result["weights"]["supplier"] == 0.25
    assert result["weights"]["manufacturing"] == 0.25
    assert result["weights"]["stockout"] == 0.20
    assert result["weights"]["transport"] == 0.20
    assert result["weights"]["external"] == 0.10


def test_network_score_high_threshold():
    """Verify high risk threshold triggers when score >= 0.60."""
    result = compute_network_risk(
        supplier_prob=0.9,
        manufacturing_prob=0.8,
        stockout_prob=0.7,
        transport_prob=0.8,
        external_score=0.5,
    )
    # Expected: 0.25*0.9 + 0.25*0.8 + 0.20*0.7 + 0.20*0.8 + 0.10*0.5
    # = 0.225 + 0.20 + 0.14 + 0.16 + 0.05 = 0.775
    assert result["network_risk"] == 0.775
    assert result["level"] == "High"


def test_recommendations_rules():
    """Verify prescriptive recommendations for each risk type."""
    # 1. Supplier High -> switch supplier
    sup_actions = generate_recommendations("supplier_failure", "High", "SUP001")
    assert any("switch" in a["action"].lower() for a in sup_actions)

    # 2. Stockout High -> raise safety stock
    wh_actions = generate_recommendations("warehouse_stockout", "High", "WH001")
    assert any("safety stock" in a["action"].lower() for a in wh_actions)

    # 3. Transport High -> reroute / divert
    trans_actions = generate_recommendations("transport_disruption", "High", "RT004")
    assert any("divert" in a["action"].lower() or "reroute" in a["action"].lower() for a in trans_actions)

    # 4. Manufacturing High -> prioritize orders
    mfg_actions = generate_recommendations("manufacturing_delay", "High", "PLT002")
    assert any("prioritize" in a["action"].lower() for a in mfg_actions)


def test_disclosure_file_contents():
    """Verify disclosure.md clearly states real vs synthetic data and assumptions."""
    disc_path = DOCS_DIR / "disclosure.md"
    assert disc_path.exists(), "Missing docs/disclosure.md"
    content = disc_path.read_text(encoding="utf-8")
    assert "DataCo" in content
    assert "Open-Meteo" in content
    assert "Synthetic" in content
    assert "Assumptions" in content
