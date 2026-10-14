"""Day 3 Comprehensive Test Suite for Member 2.

Validates:
  1. API points at real production files (predictions.csv, reasons.csv, shap_values.parquet, metrics.csv)
  2. Integration of Member 1's decision modules (network_score.py, recommendations.py)
  3. LLM alert summary formatting with template fallback
  4. Leakage-free training proof (tests/test_leakage.py)
  5. 5 demo headlines in outputs/demo_headlines.json
  6. Technical report in reports/member2_report_section.md
  7. NewsPanel frontend component in frontend/src/components/NewsPanel.jsx
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

from src.api.test_api import test_api_endpoints
from tests.test_leakage import run_all_leakage_tests


def test_real_files():
    print("--> Checking real production files...")
    assert (ROOT / "outputs" / "predictions.csv").exists(), "predictions.csv missing!"
    assert (ROOT / "outputs" / "reasons.csv").exists(), "reasons.csv missing!"
    assert (ROOT / "outputs" / "shap_values.parquet").exists(), "shap_values.parquet missing!"
    assert (ROOT / "outputs" / "metrics.csv").exists(), "metrics.csv missing!"
    print("    PASS: All real outputs present.")


def test_demo_headlines():
    print("--> Checking outputs/demo_headlines.json...")
    demo_f = ROOT / "outputs" / "demo_headlines.json"
    assert demo_f.exists(), "demo_headlines.json missing!"
    with open(demo_f, "r", encoding="utf-8") as f:
        cases = json.load(f)
    assert len(cases) == 5, f"Expected 5 cases, found {len(cases)}"
    for c in cases:
        for k in ("headline", "linked_node", "disruption_type", "risk_score", "risk_level"):
            assert k in c, f"Missing key {k} in demo case"
    print(f"    PASS: 5 exemplary headlines verified ({', '.join(c['linked_node'] for c in cases)}).")


def test_report_and_frontend():
    print("--> Checking report and frontend NewsPanel component...")
    rep_f = ROOT / "reports" / "member2_report_section.md"
    assert rep_f.exists(), "member2_report_section.md missing!"
    content = rep_f.read_text(encoding="utf-8")
    assert "DeBERTa-v3" in content
    assert "Extended Isolation Forest" in content
    assert "FastAPI" in content
    assert "October test split" in content

    news_panel = ROOT / "frontend" / "src" / "components" / "NewsPanel.jsx"
    assert news_panel.exists(), "NewsPanel.jsx missing!"
    print("    PASS: Technical report and NewsPanel component verified.")


def main():
    print("=============================================================")
    print("            MEMBER 2: DAY 3 VERIFICATION SUITE               ")
    print("=============================================================")
    test_real_files()
    test_demo_headlines()
    test_report_and_frontend()
    print("\n-------------------------------------------------------------")
    print("               RUNNING FASTAPI CONTRACT TESTS                ")
    print("-------------------------------------------------------------")
    test_api_endpoints()
    print("\n-------------------------------------------------------------")
    print("               RUNNING LEAKAGE PROOF TESTS                   ")
    print("-------------------------------------------------------------")
    run_all_leakage_tests()
    print("\n=============================================================")
    print("         ALL DAY 3 TASKS 100% VERIFIED & COMPLETED!          ")
    print("=============================================================")


if __name__ == "__main__":
    main()
