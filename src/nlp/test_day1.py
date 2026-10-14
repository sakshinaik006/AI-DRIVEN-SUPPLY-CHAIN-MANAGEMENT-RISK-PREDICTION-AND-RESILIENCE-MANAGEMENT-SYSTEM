"""Day 1 Comprehensive Test & Verification Suite for Member 2.

Tests all Day 1 deliverables:
  - GDELT news schema and validity
  - spaCy NER location extraction & master entity linking
  - Zero-shot disruption classification
  - DeBERTa-v3 continuous risk scoring
  - TF-IDF + Logistic Regression train-only fitting and OOF predictions
  - Extended Isolation Forest & Plain Isolation Forest anomaly detection on Member 1's dummy files
"""
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

_dll_cookie = None
if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    torch_lib = os.path.join(sys.prefix, "Lib", "site-packages", "torch", "lib")
    if os.path.exists(torch_lib):
        try:
            _dll_cookie = os.add_dll_directory(torch_lib)
        except Exception:
            pass

try:
    import torch
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]

from src.nlp.ner_linking import SupplyChainNERLinker
from src.nlp.zero_shot import DisruptionZeroShotClassifier
from src.nlp.risk_scoring import DeBERTaRiskScorer
from src.nlp.baseline_tfidf import TfidfLogisticBaseline
from src.anomaly.isolation_forest import run_anomaly_pipeline, ExtendedIsolationForest, PlainIsolationForestBaseline


def test_gdelt_raw_file():
    print("--> Testing data/raw/gdelt_headlines.parquet...")
    raw_path = ROOT / "data" / "raw" / "gdelt_headlines.parquet"
    assert raw_path.exists(), f"File {raw_path} does not exist!"
    df = pd.read_parquet(raw_path)
    expected_cols = ["date", "title", "country", "city", "theme", "tone"]
    for c in expected_cols:
        assert c in df.columns, f"Missing required column: {c}"
    assert len(df) >= 100, f"Expected at least 100 headlines, found {len(df)}"
    assert (df["tone"] >= -20).all() and (df["tone"] <= 20).all(), "Tone values outside expected range"
    print(f"    PASS: {len(df)} headlines loaded with columns {list(df.columns)}")


def test_ner_and_linking():
    print("--> Testing spaCy NER and Entity Linking...")
    linker = SupplyChainNERLinker()
    # Test city linking
    matches_sz = linker.link_entities(
        "Severe container backlog causes gridlock at ports near Shenzhen",
        city="Shenzhen", country="China", theme="port_congestion"
    )
    assert len(matches_sz) > 0, "Failed to link Shenzhen headline"
    entities = [m["entity_id"] for m in matches_sz]
    assert any("PLT" in e or "SUP" in e or "RT" in e for e in entities), f"Unexpected entity types: {entities}"
    print(f"    PASS: Linked Shenzhen headline to {len(matches_sz)} entities: {entities[:4]}...")


def test_zero_shot_classification():
    print("--> Testing Zero-Shot Disruption Classification...")
    classifier = DisruptionZeroShotClassifier()
    assert classifier.predict("Labour union strikes close factory in Dongguan") == "strike"
    assert classifier.predict("Extreme monsoon flood inundates industrial park") == "flood"
    assert classifier.predict("Critical microchip and wafer shortage halts production") == "shortage"
    assert classifier.predict("Blackout and electrical power cut stops assembly line") == "power_cut"
    print("    PASS: Disruption classification correctly identified test labels.")


def test_risk_scoring():
    print("--> Testing DeBERTa-v3 Continuous Risk Scoring...")
    scorer = DeBERTaRiskScorer()
    high_score = scorer.score_text("Catastrophic flood and regulatory shutdown halt production", tone=-7.5, theme="shutdown")
    low_score = scorer.score_text("Stable logistics operations report increased seasonal throughput", tone=2.1, theme="general_business")
    assert 0.0 <= high_score <= 1.0, f"Score out of bounds: {high_score}"
    assert 0.0 <= low_score <= 1.0, f"Score out of bounds: {low_score}"
    assert high_score > low_score, f"High risk headline ({high_score}) should exceed low risk headline ({low_score})"
    print(f"    PASS: High risk={high_score:.3f}, Low risk={low_score:.3f}")


def test_tfidf_baseline():
    print("--> Testing TF-IDF + Logistic Regression Baseline on train period only...")
    raw_path = ROOT / "data" / "raw" / "gdelt_headlines.parquet"
    df_news = pd.read_parquet(raw_path)
    d = pd.to_datetime(df_news["date"])
    df_news["split"] = np.select(
        [d <= "2025-08-24", d <= "2025-08-31", d <= "2025-09-23", d <= "2025-09-30"],
        ["train", "purge", "val", "purge"],
        default="test",
    )
    baseline = TfidfLogisticBaseline()
    oof_scores = baseline.fit_predict_oof(df_news)
    assert len(oof_scores) == len(df_news), "OOF predictions length mismatch"
    assert not oof_scores.isna().any(), "Found NaN in OOF predictions"
    assert baseline.is_fitted, "Baseline model failed to fit"
    metrics = baseline.evaluate_test_split(df_news.assign(tfidf_lr_risk=oof_scores))
    print(f"    PASS: Baseline fitted leak-free on train only. Test PR-AUC: {metrics['pr_auc']:.3f}, F1: {metrics['f1']:.3f}")


def test_anomaly_on_dummy_files():
    print("--> Testing Extended Isolation Forest & Baseline on Member 1's dummy files...")
    dummy_sup = ROOT / "data" / "processed" / "features_supplier_v0_dummy.parquet"
    assert dummy_sup.exists(), f"{dummy_sup} missing!"
    df_sup = pd.read_parquet(dummy_sup)
    feature_cols = ["supplier_delay_7d_avg", "rain_7d_sum", "news_tone_14d_trend"]

    res = run_anomaly_pipeline(df_sup, feature_cols, risk_type="supplier_failure")
    assert len(res) == len(df_sup), "Output row count mismatch"
    assert set(res.columns) == {"entity_id", "date", "risk_type", "anomaly_score", "anomaly_flag", "if_baseline_score"}
    assert (res["anomaly_score"] >= 0).all() and (res["anomaly_score"] <= 1.0).all(), "Anomaly score out of [0, 1]"
    assert (res["if_baseline_score"] >= 0).all() and (res["if_baseline_score"] <= 1.0).all(), "IF baseline score out of [0, 1]"
    assert set(res["anomaly_flag"].unique()).issubset({0, 1}), "Anomaly flag not binary"
    print(f"    PASS: Processed {len(res)} supplier rows. Anomaly flag rate: {res['anomaly_flag'].mean():.1%}")


def run_all():
    print("=== STARTING DAY 1 VERIFICATION SUITE ===")
    test_gdelt_raw_file()
    test_ner_and_linking()
    test_zero_shot_classification()
    test_risk_scoring()
    test_tfidf_baseline()
    test_anomaly_on_dummy_files()
    print("=== ALL DAY 1 TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    run_all()
