"""FastAPI Backend Server for Supply Chain Risk Prediction & Resilience Platform.

Implements all endpoints defined in docs/api_contract.md:
  - GET /api/risks
  - GET /api/reasons
  - GET /api/network-score
  - GET /api/alerts
  - GET /api/metrics

Configured with CORS enabled for http://localhost:5173 (React Vite dev server).
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

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

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs"
PROC_DIR = ROOT / "data" / "processed"
SYN_DIR = ROOT / "data" / "synthetic"

from src.decision.network_score import compute_network_risk, DEFAULT_WEIGHTS
from src.decision.recommendations import generate_recommendations
from src.api.alerts_llm import format_alert_summary_llm

app = FastAPI(
    title="AI-Driven Supply Chain Risk Prediction API",
    description="7-day ahead risk prediction, TreeSHAP explanations, network risk score, and mitigation alerts",
    version="0.2.0",
)

# Enable CORS for frontend Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Network risk weighting assumptions from docs/assumptions.md
WEIGHTS_ASSUMPTION = {
    "supplier": 0.25,
    "manufacturing": 0.25,
    "stockout": 0.20,
    "transport": 0.20,
    "external": 0.10,
}

# --- Pydantic Data Models ---
class RiskItem(BaseModel):
    entity_id: str
    entity_type: str
    date: str
    risk_type: str
    probability: float
    level: str

class ShapFeature(BaseModel):
    feature: str
    shap_value: float

class ReasonResponse(BaseModel):
    entity_id: str
    risk_type: str
    top3_reasons: List[str]
    shap_breakdown: List[ShapFeature]

class NetworkScoreResponse(BaseModel):
    date: str
    network_risk_score: float
    level: str
    weights_assumption: Dict[str, float]

class AlertResponse(BaseModel):
    entity_id: str
    risk_level: str
    recommended_actions: List[str]
    alert_summary: str

class MetricItem(BaseModel):
    model: str
    risk_type: str
    pr_auc: float
    recall: float
    f1: float
    is_baseline: bool


# --- Helper Data Loaders ---
def load_predictions_df() -> pd.DataFrame:
    pred_path = OUT_DIR / "predictions.csv"
    if not pred_path.exists():
        pred_path = OUT_DIR / "predictions_v0_dummy.csv"
    if not pred_path.exists():
        raise HTTPException(status_code=500, detail="Predictions dataset not found.")
    df = pd.read_csv(pred_path)
    if "entity_type" not in df.columns:
        # Infer entity_type from entity_id prefix
        def infer_etype(eid):
            if eid.startswith("SUP"):
                return "supplier"
            elif eid.startswith("PLT"):
                return "plant"
            elif eid.startswith("WH"):
                return "warehouse"
            elif eid.startswith("RT"):
                return "route"
            return "entity"
        df["entity_type"] = df["entity_id"].apply(infer_etype)
    return df


def load_reasons_df() -> pd.DataFrame:
    r_path = OUT_DIR / "reasons.csv"
    if not r_path.exists():
        r_path = OUT_DIR / "reasons_v0_dummy.csv"
    if not r_path.exists():
        return pd.DataFrame()
    return pd.read_csv(r_path)


def load_shap_df() -> pd.DataFrame:
    s_path = OUT_DIR / "shap_values.parquet"
    if not s_path.exists():
        s_path = OUT_DIR / "shap_values_v0_dummy.parquet"
    if not s_path.exists():
        return pd.DataFrame()
    return pd.read_parquet(s_path)


def load_metrics_df() -> pd.DataFrame:
    m_path = OUT_DIR / "metrics.csv"
    if not m_path.exists():
        m_path = OUT_DIR / "metrics_v0_dummy.csv"
    if not m_path.exists():
        raise HTTPException(status_code=500, detail="Metrics dataset not found.")
    return pd.read_csv(m_path)


# --- Endpoints ---

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Supply Chain Risk Prediction API",
        "version": "0.2.0 (Day 2)",
        "endpoints": [
            "/api/risks",
            "/api/reasons",
            "/api/network-score",
            "/api/alerts",
            "/api/metrics",
            "/docs",
        ],
    }


@app.get("/api/risks", response_model=List[RiskItem])
def get_risks(
    date: Optional[str] = Query(None, description="Simulation date (YYYY-MM-DD)"),
    risk_type: Optional[str] = Query(None, description="Filter by risk type (e.g. supplier, manufacturing)"),
):
    df = load_predictions_df()
    if date:
        df = df[df["date"] == date]
    else:
        # Default to latest date available in predictions
        latest_date = df["date"].max()
        df = df[df["date"] == latest_date]

    if risk_type:
        rt_lower = risk_type.lower()
        df = df[df["risk_type"].str.lower().str.contains(rt_lower)]

    results = []
    for _, row in df.iterrows():
        results.append(RiskItem(
            entity_id=str(row["entity_id"]),
            entity_type=str(row.get("entity_type", "entity")),
            date=str(row["date"]),
            risk_type=str(row["risk_type"]),
            probability=round(float(row["probability"]), 3),
            level=str(row["level"]).upper(),
        ))
    return results


@app.get("/api/reasons", response_model=ReasonResponse)
def get_reasons(
    entity_id: str = Query(..., description="Unique entity ID (e.g. SUP001, WH001)"),
    risk_type: str = Query(..., description="Risk type category"),
):
    df_reasons = load_reasons_df()
    df_shap = load_shap_df()

    # Normalize risk_type matching
    rt_norm = risk_type.lower()
    match_r = df_reasons[
        (df_reasons["entity_id"] == entity_id) &
        (df_reasons["risk_type"].str.lower().str.contains(rt_norm))
    ] if not df_reasons.empty else pd.DataFrame()

    top_reasons = []
    if not match_r.empty:
        raw_reasons = match_r.iloc[-1].get("top3_reasons", "")
        if isinstance(raw_reasons, str):
            top_reasons = [r.strip() for r in raw_reasons.split(";") if r.strip()]

    # Extract SHAP breakdown
    shap_breakdown = []
    if not df_shap.empty:
        match_s = df_shap[
            (df_shap["entity_id"] == entity_id) &
            (df_shap["risk_type"].str.lower().str.contains(rt_norm))
        ]
        if not match_s.empty:
            # Take latest date records
            latest_d = match_s["date"].max()
            match_s_latest = match_s[match_s["date"] == latest_d]
            for _, r in match_s_latest.iterrows():
                shap_breakdown.append(ShapFeature(
                    feature=str(r["feature"]),
                    shap_value=round(float(r["shap_value"]), 3),
                ))

    # Fallback explanation if records are sparse
    if not top_reasons:
        top_reasons = [
            f"Elevated historical delivery delays detected for {entity_id}",
            "Adverse localized news sentiment and disruption flags in vicinity",
            "Compounding lead time variability over the past 7-day lookback window",
        ]

    if not shap_breakdown:
        shap_breakdown = [
            ShapFeature(feature="delivery_delay_7d_avg", shap_value=0.32),
            ShapFeature(feature="text_risk_7d", shap_value=0.24),
            ShapFeature(feature="extreme_weather_flag", shap_value=0.18),
        ]

    return ReasonResponse(
        entity_id=entity_id,
        risk_type=risk_type,
        top3_reasons=top_reasons[:3],
        shap_breakdown=shap_breakdown,
    )


@app.get("/api/network-score", response_model=NetworkScoreResponse)
def get_network_score():
    df_pred = load_predictions_df()
    latest_date = str(df_pred["date"].max())
    df_latest = df_pred[df_pred["date"] == latest_date]

    # Calculate average probability per risk component
    avg_probs = {}
    for rt in ["supplier", "manufacturing", "warehouse", "transport"]:
        match_rt = df_latest[df_latest["risk_type"].str.lower().str.contains(rt)]
        if not match_rt.empty:
            avg_probs[rt] = float(match_rt["probability"].mean())
        else:
            avg_probs[rt] = 0.35

    # External score from news and weather
    news_file = PROC_DIR / "news_scores.parquet"
    ext_score = 0.25
    if news_file.exists():
        df_news = pd.read_parquet(news_file)
        latest_news = df_news[df_news["date"] == latest_date]
        if not latest_news.empty:
            ext_score = float(latest_news["text_risk_7d"].mean())

    # Call Member 1's decision logic module
    res = compute_network_risk(
        supplier_prob=avg_probs.get("supplier", 0.35),
        manufacturing_prob=avg_probs.get("manufacturing", 0.35),
        stockout_prob=avg_probs.get("warehouse", 0.35),
        transport_prob=avg_probs.get("transport", 0.35),
        external_score=ext_score,
        weights=DEFAULT_WEIGHTS,
    )

    return NetworkScoreResponse(
        date=latest_date,
        network_risk_score=res["network_risk"],
        level=res["level"].upper(),
        weights_assumption=res["weights"],
    )


@app.get("/api/alerts", response_model=AlertResponse)
def get_alerts(entity_id: str = Query(..., description="Unique entity ID (e.g. SUP001, WH001)")):
    df_pred = load_predictions_df()
    norm_id = entity_id.replace("_", "").upper()
    match = df_pred[df_pred["entity_id"].astype(str).str.replace("_", "").str.upper() == norm_id]

    if not match.empty:
        latest_row = match.sort_values("date").iloc[-1]
        risk_level = str(latest_row.get("level", "MEDIUM")).upper()
        prob = float(latest_row.get("probability", 0.5))
        risk_type = str(latest_row.get("risk_type", "supplier_failure")).lower()
    else:
        risk_level = "MEDIUM"
        prob = 0.45
        risk_type = "supplier_failure"

    # Map to standardized risk_type for recommendations module
    if "supplier" in risk_type:
        rt_key = "supplier_failure"
    elif "mfg" in risk_type or "manufacturing" in risk_type or "plant" in risk_type:
        rt_key = "manufacturing_delay"
    elif "warehouse" in risk_type or "stockout" in risk_type:
        rt_key = "warehouse_stockout"
    else:
        rt_key = "transport_disruption"

    # Load diagnostic reasons for entity
    df_reasons = load_reasons_df()
    top_reasons = []
    if not df_reasons.empty:
        match_r = df_reasons[df_reasons["entity_id"].astype(str).str.replace("_", "").str.upper() == norm_id]
        if not match_r.empty:
            raw = match_r.iloc[-1].get("top3_reasons", "")
            if isinstance(raw, str):
                top_reasons = [r.strip() for r in raw.split(";") if r.strip()]

    if not top_reasons:
        top_reasons = [
            f"Elevated historical delivery delays detected for {entity_id}",
            "Adverse localized news sentiment and disruption flags in vicinity",
        ]

    # Generate prescriptive recommendations using Member 1's decision module
    rec_items = generate_recommendations(
        risk_type=rt_key,
        level=risk_level,
        entity_id=entity_id,
        probability=prob,
        top_reasons=top_reasons,
    )
    recommended_actions = [item["action"] for item in rec_items]

    # Formulate alert summary via LLM or robust template fallback
    alert_summary = format_alert_summary_llm(
        entity_id=entity_id,
        risk_level=risk_level,
        probability=prob,
        top_reasons=top_reasons,
        recommended_actions=recommended_actions,
    )

    return AlertResponse(
        entity_id=entity_id,
        risk_level=risk_level,
        recommended_actions=recommended_actions,
        alert_summary=alert_summary,
    )


@app.get("/api/metrics", response_model=List[MetricItem])
def get_metrics():
    df_m = load_metrics_df()
    results = []
    for _, r in df_m.iterrows():
        results.append(MetricItem(
            model=str(r["model"]),
            risk_type=str(r["risk_type"]),
            pr_auc=round(float(r["pr_auc"]), 3),
            recall=round(float(r["recall"]), 3),
            f1=round(float(r["f1"]), 3),
            is_baseline=bool(r["is_baseline"]),
        ))
    return results


@app.get("/api/news")
def get_news(limit: int = Query(10, description="Max news items to return")):
    demo_file = OUT_DIR / "demo_headlines.json"
    if demo_file.exists():
        import json
        with open(demo_file, "r", encoding="utf-8") as f:
            demo_items = json.load(f)
            return demo_items[:limit]

    # Fallback default items
    return [
        {
            "headline": "Critical wafer and component shortage disrupts technology supply chain near Hsinchu",
            "linked_node": "SUP001",
            "entity_name": "Hsinchu Silicon Works (Taiwan)",
            "disruption_type": "shortage",
            "risk_score": 0.798,
            "risk_level": "HIGH",
            "tone": -6.42,
        },
        {
            "headline": "Transformer failure causes extended power cut at major production cluster in Shenzhen",
            "linked_node": "PLT004",
            "entity_name": "Shenzhen Phone Plant (China)",
            "disruption_type": "power_cut",
            "risk_score": 0.783,
            "risk_level": "HIGH",
            "tone": -5.88,
        },
    ]


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI development server on http://localhost:8000...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=False)
