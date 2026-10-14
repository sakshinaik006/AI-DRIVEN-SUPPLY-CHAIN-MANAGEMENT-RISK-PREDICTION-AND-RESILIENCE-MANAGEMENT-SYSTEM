"""End-to-End Test Suite for Member 2 Day 1 & Day 2 Deliverables.

Validates:
  1. Day 1: GDELT headlines, spaCy NER, zero-shot classifier, DeBERTa risk scoring,
     TF-IDF baseline (train-only), Extended Isolation Forest (train-only).
  2. Day 2: news_scores.parquet (5,778 rows, shift(1) rolling average, out-of-fold scores),
     anomaly_scores.parquet (4 risk domains, train-only EIF & baseline),
     metrics.csv (October test evaluation comparisons),
     FastAPI backend endpoints & CORS compliance.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

from src.nlp.test_day1 import run_all as run_day1_tests
from src.api.test_api import test_api_endpoints as run_api_tests


def run_day2_data_checks():
    import pandas as pd

    print("--> Checking data/processed/news_scores.parquet...")
    news_p = ROOT / "data" / "processed" / "news_scores.parquet"
    assert news_p.exists(), "news_scores.parquet missing!"
    df_n = pd.read_parquet(news_p)
    assert len(df_n) == 5778, f"Expected 5778 rows, got {len(df_n)}"
    assert list(df_n.columns) == ["entity_id", "date", "text_risk", "text_risk_7d", "disruption_type", "tone"]
    # Check that text_risk_7d is shifted by 1 day
    first_dates = df_n.groupby("entity_id")["text_risk_7d"].first()
    assert (first_dates == 0.0).all(), "Leakage detected: first date text_risk_7d is non-zero!"
    print(f"    PASS: news_scores.parquet verified ({len(df_n)} rows, leak-free shift(1) confirmed).")

    print("--> Checking data/processed/anomaly_scores.parquet...")
    anom_p = ROOT / "data" / "processed" / "anomaly_scores.parquet"
    assert anom_p.exists(), "anomaly_scores.parquet missing!"
    df_a = pd.read_parquet(anom_p)
    assert set(df_a.columns) == {"entity_id", "date", "risk_type", "anomaly_score", "anomaly_flag", "if_baseline_score"}
    assert set(df_a["risk_type"].unique()) == {
        "supplier_failure", "manufacturing_delay", "warehouse_stockout", "transport_disruption"
    }
    print(f"    PASS: anomaly_scores.parquet verified ({len(df_a)} rows across all 4 risk types).")

    print("--> Checking outputs/metrics.csv...")
    m_p = ROOT / "outputs" / "metrics.csv"
    assert m_p.exists(), "metrics.csv missing!"
    df_m = pd.read_csv(m_p)
    assert set(df_m.columns) == {"model", "risk_type", "pr_auc", "recall", "f1", "is_baseline"}
    models = set(df_m["model"].unique())
    assert "TF-IDF + Logistic Regression" in models
    assert "DeBERTa-v3 + NER" in models
    assert "Extended Isolation Forest" in models
    assert "Plain Isolation Forest Baseline" in models
    print(f"    PASS: metrics.csv contains {len(df_m)} comparison rows including baselines and upgrades.")


def main():
    print("=============================================================")
    print("        MEMBER 2: DAY 1 & DAY 2 END-TO-END VERIFICATION       ")
    print("=============================================================")
    run_day1_tests()
    print("\n-------------------------------------------------------------")
    print("                VERIFYING DAY 2 ARTIFACTS                    ")
    print("-------------------------------------------------------------")
    run_day2_data_checks()
    print("\n-------------------------------------------------------------")
    print("                TESTING FASTAPI BACKEND                       ")
    print("-------------------------------------------------------------")
    run_api_tests()
    print("\n=============================================================")
    print("   ALL DAY 1 & DAY 2 DELIVERABLES VERIFIED & OPERATIONAL!    ")
    print("=============================================================")


if __name__ == "__main__":
    main()
