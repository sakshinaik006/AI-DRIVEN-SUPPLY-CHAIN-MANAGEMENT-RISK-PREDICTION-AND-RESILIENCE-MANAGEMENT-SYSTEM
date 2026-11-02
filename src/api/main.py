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

from src.decision.network_score import DEFAULT_WEIGHTS, compute_network_risk
from src.decision.recommendations import generate_recommendations

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs"
PROC_DIR = ROOT / "data" / "processed"
SYN_DIR = ROOT / "data" / "synthetic"

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
    p_path = OUT_DIR / "predictions.csv"
    if not p_path.exists():
        p_path = OUT_DIR / "predictions_v0_dummy.csv"
    if not p_path.exists():
        raise HTTPException(status_code=500, detail="Predictions dataset not found.")
    return pd.read_csv(p_path)

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
        if "entity_id" in df_shap.columns and "risk_type" in df_shap.columns:
            match_s = df_shap[
                (df_shap["entity_id"] == entity_id) &
                (df_shap["risk_type"].str.lower().str.contains(rt_norm))
            ]
            if not match_s.empty:
                latest_d = match_s["date"].max() if "date" in match_s.columns else None
                match_s_latest = match_s[match_s["date"] == latest_d] if latest_d else match_s
                val_col = "shap_value" if "shap_value" in match_s_latest.columns else "mean_shap_importance"
                feat_col = "feature" if "feature" in match_s_latest.columns else "feature_name"
                match_s_latest = match_s_latest.reindex(
                    match_s_latest[val_col].abs().sort_values(ascending=False).index
                )
                for _, r in match_s_latest.iterrows():
                    shap_breakdown.append(ShapFeature(
                        feature=str(r[feat_col]),
                        shap_value=round(float(r[val_col]), 4),
                    ))
        elif "target_risk" in df_shap.columns and "feature_name" in df_shap.columns:
            match_s = df_shap[df_shap["target_risk"].str.lower().str.contains(rt_norm)]
            if match_s.empty:
                match_s = df_shap
            val_col = "mean_shap_importance" if "mean_shap_importance" in match_s.columns else "shap_value"
            for _, r in match_s.head(5).iterrows():
                shap_breakdown.append(ShapFeature(
                    feature=str(r["feature_name"]),
                    shap_value=round(float(r[val_col]), 4),
                ))

    # Fallback or dynamic reasons from shap_breakdown
    if not top_reasons and shap_breakdown:
        top_reasons = [
            f"Key factor '{item.feature}' contributed {item.shap_value:+.4f} to predicted log-odds"
            for item in shap_breakdown[:3]
        ]

    if not top_reasons:
        top_reasons = [
            f"Elevated historical delivery delays detected for {entity_id}",
            "Adverse localized news sentiment and disruption flags in vicinity",
            "Compounding lead time variability over the past 7-day lookback window",
        ]

    if not shap_breakdown:
        shap_breakdown = [
            ShapFeature(feature="delivery_delay_7d_avg", shap_value=0.032),
            ShapFeature(feature="text_risk_7d", shap_value=0.024),
            ShapFeature(feature="extreme_weather_flag", shap_value=0.018),
        ]

    return ReasonResponse(
        entity_id=entity_id,
        risk_type=risk_type,
        top3_reasons=top_reasons[:3],
        shap_breakdown=shap_breakdown,
    )


@app.get("/api/network-score", response_model=NetworkScoreResponse)
def get_network_score(date: Optional[str] = Query(None, description="Simulation date (YYYY-MM-DD)")):
    df_pred = load_predictions_df()
    latest_date = str(date) if date else str(df_pred["date"].max())
    df_latest = df_pred[df_pred["date"] == latest_date]
    if df_latest.empty:
        df_latest = df_pred[df_pred["date"] == str(df_pred["date"].max())]
        latest_date = str(df_pred["date"].max())

    avg_probs = {}
    for rt, comp in [
        ("supplier", "supplier"),
        ("manufacturing", "manufacturing"),
        ("warehouse", "stockout"),
        ("transport", "transport"),
    ]:
        match_rt = df_latest[df_latest["risk_type"].str.lower().str.contains(rt)]
        if not match_rt.empty:
            avg_probs[comp] = float(match_rt["probability"].mean())
        else:
            avg_probs[comp] = 0.0

    news_file = PROC_DIR / "news_scores.parquet"
    ext_score = 0.0
    if news_file.exists():
        df_news = pd.read_parquet(news_file)
        latest_news = df_news[df_news["date"] == latest_date]
        if not latest_news.empty and "text_risk_7d" in latest_news.columns:
            val = float(latest_news["text_risk_7d"].mean())
            ext_score = max(0.0, min(1.0, val))

    res = compute_network_risk(
        supplier_prob=avg_probs["supplier"],
        manufacturing_prob=avg_probs["manufacturing"],
        stockout_prob=avg_probs["stockout"],
        transport_prob=avg_probs["transport"],
        external_score=ext_score,
    )

    return NetworkScoreResponse(
        date=latest_date,
        network_risk_score=round(float(res["network_risk"]), 3),
        level=res["level"].upper(),
        weights_assumption=DEFAULT_WEIGHTS,
    )


@app.get("/api/alerts", response_model=AlertResponse)
def get_alerts(entity_id: str = Query(..., description="Unique entity ID (e.g. SUP001, WH001)")):
    df_pred = load_predictions_df()
    match = df_pred[df_pred["entity_id"] == entity_id]

    if not match.empty:
        latest_row = match.sort_values("date").iloc[-1]
        risk_level = str(latest_row.get("level", "MEDIUM")).upper()
        prob = float(latest_row.get("probability", 0.5))
        risk_type = str(latest_row.get("risk_type", "supplier_failure")).lower()
    else:
        risk_level = "LOW"
        prob = 0.10
        risk_type = "supplier_failure"

    recs = generate_recommendations(
        risk_type=risk_type,
        level=risk_level,
        entity_id=entity_id,
        probability=prob,
    )
    recommended_actions = [r["action"] for r in recs]

    alert_summary = (
        f"{entity_id} exhibits {prob:.1%} predicted risk ({risk_level}) over the next 7 days. "
        f"Action type: {recs[0]['action_type']}. "
        f"Recommended intervention: {recommended_actions[0]}"
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
        pr_auc_val = float(r.get("pr_auc", r.get("test_pr_auc", 0.0)))
        recall_val = float(r.get("recall", r.get("test_recall", 0.0)))
        f1_val = float(r.get("f1", r.get("test_f1", 0.0)))
        is_base = bool(r.get("is_baseline", False))
        results.append(MetricItem(
            model=str(r["model"]),
            risk_type=str(r["risk_type"]),
            pr_auc=round(pr_auc_val, 3),
            recall=round(recall_val, 3),
            f1=round(f1_val, 3),
            is_baseline=is_base,
        ))
    return results


@app.get("/api/forecast")
def get_forecast():
    f_path = OUT_DIR / "forecast_scores.parquet"
    if not f_path.exists():
        f_path = PROC_DIR / "forecast_scores_v0_dummy.parquet"
    if not f_path.exists():
        return []
    df = pd.read_parquet(f_path)
    records = []
    for _, r in df.iterrows():
        records.append({
            "entity_id": str(r.get("entity_id", "WH001")),
            "date": str(r.get("date"))[:10],
            "forecast_demand": round(float(r.get("forecast_demand", 0)), 1),
            "chronos_forecast": round(float(r.get("chronos_forecast", 0)), 1),
            "patchtst_delay_forecast": round(float(r.get("patchtst_delay_forecast", 0)), 2),
            "demand_surge_flag": int(r.get("demand_surge_flag", 0)),
        })
    return records


@app.get("/api/anomalies")
def get_anomalies():
    a_path = PROC_DIR / "anomaly_scores.parquet"
    if not a_path.exists():
        a_path = PROC_DIR / "anomaly_scores_v0_dummy.parquet"
    if not a_path.exists():
        return []
    df = pd.read_parquet(a_path)
    anom_only = df[df["anomaly_flag"] == 1]
    if anom_only.empty:
        anom_only = df.tail(10)
    else:
        anom_only = anom_only.tail(12)
    records = []
    for _, r in anom_only.iterrows():
        records.append({
            "entity_id": str(r.get("entity_id")),
            "date": str(r.get("date")),
            "risk_type": str(r.get("risk_type")),
            "anomaly_score": round(float(r.get("anomaly_score", 0)), 3),
            "anomaly_flag": int(r.get("anomaly_flag", 0)),
        })
    return records


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI development server on http://localhost:8000...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=False)
