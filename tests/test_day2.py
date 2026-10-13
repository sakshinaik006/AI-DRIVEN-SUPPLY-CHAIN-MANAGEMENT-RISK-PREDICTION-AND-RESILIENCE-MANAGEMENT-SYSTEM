"""Unit and integration tests for Member 1 Day 2 deliverables:
- features_v1 and features_v2 integrity, columns, no leakage, split mapping
- graph_scores.parquet schema and coverage
- data_dictionary.md exists and covers four risks
- Frontend React build artifacts exist
"""
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PROC_DIR = ROOT / "data" / "processed"
DOCS_DIR = ROOT / "docs"
FRONTEND_DIST = ROOT / "frontend" / "dist"

RISK_TABLES = ["supplier", "manufacturing", "warehouse", "transport"]


def test_features_v1_and_v2_exist_and_match():
    """Handover 7 & 10 check: features_v1 and features_v2 exist for all four risks."""
    for risk in RISK_TABLES:
        v1_path = PROC_DIR / f"features_{risk}_v1.parquet"
        v2_path = PROC_DIR / f"features_{risk}_v2.parquet"
        assert v1_path.exists(), f"Missing {v1_path}"
        assert v2_path.exists(), f"Missing {v2_path}"

        df1 = pd.read_parquet(v1_path)
        df2 = pd.read_parquet(v2_path)
        assert len(df1) == len(df2), f"Row count mismatch in {risk}"
        assert list(df1.columns) == list(df2.columns), f"Column mismatch in {risk}"


def test_features_leakage_and_splits():
    """Verify leak-free properties: no Late_delivery_risk, split present, label_7d cutoff."""
    forbidden_leakage_cols = {"Late_delivery_risk", "delivery_status", "Days for shipping (real)"}
    expected_splits = {"train", "purge", "val", "test"}

    for risk in RISK_TABLES:
        df = pd.read_parquet(PROC_DIR / f"features_{risk}_v2.parquet")

        # Check keys
        assert {"entity_type", "entity_id", "date", "split", "label_7d"} <= set(df.columns)
        assert not (forbidden_leakage_cols & set(df.columns)), f"Leakage column found in features_{risk}"
        assert set(df["split"]) == expected_splits, f"Splits mismatch in features_{risk}"

        # Check positive rate strictly in range [2.5%, 6.5%]
        valid_labels = df.dropna(subset=["label_7d"])
        pos_rate = valid_labels["label_7d"].mean()
        assert 0.025 <= pos_rate <= 0.065, f"Positive rate {pos_rate:.1%} in {risk} out of target bounds"

        # Check that last 7 days of October have unobserved label_7d (NaN)
        oct_end_rows = df[df["date"] > "2025-10-24"]
        assert oct_end_rows["label_7d"].isna().all(), f"Lookahead leakage in {risk}: Oct 25-31 must be unlabelled NaN"


def test_graph_scores_handover12():
    """Handover 12 check: graph_scores.parquet with dependency_count and route_importance."""
    graph_path = PROC_DIR / "graph_scores.parquet"
    assert graph_path.exists(), "Missing graph_scores.parquet"
    df = pd.read_parquet(graph_path)

    assert set(df.columns) == {"entity_id", "dependency_count", "hgt_score", "route_importance"}
    assert len(df) == 18, f"Expected 18 entities (8 suppliers + 10 routes), got {len(df)}"

    sup_rows = df[df["entity_id"].str.startswith("SUP")]
    assert len(sup_rows) == 8
    assert sup_rows["dependency_count"].notna().all()
    assert sup_rows["hgt_score"].notna().all()

    route_rows = df[df["entity_id"].str.startswith("RT")]
    assert len(route_rows) == 10
    assert route_rows["route_importance"].notna().all()


def test_data_dictionary_and_frontend_build():
    """Verify data_dictionary.md documentation and frontend production build bundle."""
    dd_path = DOCS_DIR / "data_dictionary.md"
    assert dd_path.exists(), "Missing docs/data_dictionary.md"
    content = dd_path.read_text(encoding="utf-8")
    for risk in RISK_TABLES:
        assert f"features_{risk}" in content

    # Check frontend dist build
    index_html = FRONTEND_DIST / "index.html"
    assert index_html.exists(), "Missing frontend/dist/index.html (npm run build artifact)"
