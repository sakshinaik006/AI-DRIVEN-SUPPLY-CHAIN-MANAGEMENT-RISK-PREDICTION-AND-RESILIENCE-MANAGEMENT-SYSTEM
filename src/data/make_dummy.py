"""Generate dummy files in the agreed interface format (docs/interface.md).

Run from the repo root:  python -m src.data.make_dummy
Everything is seeded, so the output is reproducible. These are PLACEHOLDERS so
Members 2 and 3 can start work; they are replaced by real data v1 later.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
START, END = "2025-04-01", "2025-10-31"
ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
OUT = ROOT / "outputs"

N_SUP, N_PLT, N_WH, N_RT = 8, 4, 5, 10
RISKS = {
    "supplier_failure": ("supplier", "SUP", N_SUP),
    "manufacturing_delay": ("plant", "PLT", N_PLT),
    "warehouse_stockout": ("warehouse", "WH", N_WH),
    "transport_disruption": ("route", "RT", N_RT),
}
THEMES = ["shortage", "strike", "flood", "shutdown", "port_congestion"]
CITIES = [("Shenzhen", "China"), ("Chennai", "India"), ("Taipei", "Taiwan"),
          ("Hanoi", "Vietnam"), ("Seoul", "South Korea"), ("Bengaluru", "India")]


def split_of(d: pd.Series) -> pd.Series:
    d = pd.to_datetime(d)
    return np.where(d < "2025-09-01", "train", np.where(d < "2025-10-01", "val", "test"))


def ids(prefix: str, n: int):
    return [f"{prefix}{i:03d}" for i in range(1, n + 1)]


def grid(entity_type: str, prefix: str, n: int) -> pd.DataFrame:
    dates = pd.date_range(START, END, freq="D")
    eids = ids(prefix, n)
    df = pd.MultiIndex.from_product([eids, dates], names=["entity_id", "date"]).to_frame(index=False)
    df.insert(0, "entity_type", entity_type)
    df["split"] = split_of(df["date"])
    return df


def main():
    rng = np.random.default_rng(SEED)
    PROC.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    # ---- feature tables (4) -------------------------------------------------
    feature_cols = {
        "supplier": ["supplier_delay_7d_avg", "rain_7d_sum", "news_tone_14d_trend", "single_source_flag"],
        "plant": ["delivery_delay_7d_avg", "production_ratio_7d_avg", "rain_7d_sum", "supplier_failure_prob_oof"],
        "warehouse": ["demand_7d_avg", "stock_days_cover", "inventory_level", "mfg_delay_prob_oof"],
        "transport": ["delivery_delay_7d_avg", "rain_7d_sum", "port_news_tone_14d", "distance_km", "shipping_mode"],
    }
    file_names = {"supplier": "supplier", "plant": "manufacturing", "warehouse": "warehouse", "route": "transport"}
    for risk, (etype, prefix, n) in RISKS.items():
        df = grid(etype, prefix, n)
        # drop the last 7 days: no full look-ahead window for the label
        df = df[df["date"] <= pd.Timestamp(END) - pd.Timedelta(days=7)].copy()
        key = "transport" if etype == "route" else etype
        for c in feature_cols[key]:
            if c == "shipping_mode":
                df[c] = rng.choice(["air", "sea", "road"], len(df))
            elif c == "single_source_flag":
                df[c] = rng.integers(0, 2, len(df))
            else:
                df[c] = rng.normal(0, 1, len(df)).round(3)
        score = df[feature_cols[key][0]].astype(float) if feature_cols[key][0] != "shipping_mode" else 0
        p = 1 / (1 + np.exp(-(score * 0.8 - 3.2)))
        df["label_7d"] = (rng.random(len(df)) < p).astype(int)
        df.to_parquet(PROC / f"features_{file_names[etype]}_v0_dummy.parquet", index=False)
        print(f"features_{file_names[etype]}: {len(df)} rows, positives {df['label_7d'].mean():.1%}")

    # ---- graph_scores -------------------------------------------------------
    rows = []
    for e in ids("SUP", N_SUP) + ids("RT", N_RT):
        rows.append({
            "entity_id": e,
            "dependency_count": int(rng.integers(1, 6)) if e.startswith("SUP") else 0,
            "hgt_score": round(float(rng.random()), 3) if e.startswith("SUP") else 0.0,
            "route_importance": round(float(rng.random()), 3) if e.startswith("RT") else 0.0,
        })
    pd.DataFrame(rows).to_parquet(PROC / "graph_scores_v0_dummy.parquet", index=False)

    # ---- gdelt_headlines ----------------------------------------------------
    dates = pd.date_range(START, END, freq="D")
    heads = []
    for d in dates:
        for _ in range(int(rng.integers(0, 4))):
            city, country = CITIES[int(rng.integers(0, len(CITIES)))]
            theme = THEMES[int(rng.integers(0, len(THEMES)))]
            heads.append({"date": d, "title": f"{theme.replace('_', ' ').title()} reported near {city}",
                          "country": country, "city": city, "theme": theme,
                          "tone": round(float(rng.normal(-2, 2)), 2)})
    pd.DataFrame(heads).to_parquet(PROC / "gdelt_headlines_v0_dummy.parquet", index=False)

    # ---- news_scores, anomaly_scores, forecast_scores -----------------------
    sup = grid("supplier", "SUP", N_SUP)
    sup["text_risk"] = rng.random(len(sup)).round(3)
    sup["text_risk_7d"] = sup.groupby("entity_id")["text_risk"].transform(lambda s: s.rolling(7, min_periods=1).mean().shift(1)).round(3)
    sup["disruption_type"] = rng.choice(THEMES, len(sup))
    sup["tone"] = rng.normal(-2, 2, len(sup)).round(2)
    sup[["entity_id", "date", "split", "text_risk", "text_risk_7d", "disruption_type", "tone"]].to_parquet(
        PROC / "news_scores_v0_dummy.parquet", index=False)

    an = []
    for risk, (etype, prefix, n) in RISKS.items():
        g = grid(etype, prefix, n)[["entity_id", "date", "split"]]
        g["risk_type"] = risk
        g["anomaly_score"] = rng.random(len(g)).round(3)
        g["anomaly_flag"] = (g["anomaly_score"] > 0.9).astype(int)
        g["if_baseline_score"] = rng.random(len(g)).round(3)
        an.append(g)
    pd.concat(an).to_parquet(PROC / "anomaly_scores_v0_dummy.parquet", index=False)

    wh = grid("warehouse", "WH", N_WH)[["entity_id", "date", "split"]]
    wh["forecast_demand"] = rng.normal(100, 15, len(wh)).round(1)
    wh["forecast_gap"] = rng.normal(0, 10, len(wh)).round(1)
    wh["demand_surge_flag"] = (wh["forecast_gap"] > 15).astype(int)
    wh["chronos_forecast"] = (wh["forecast_demand"] + rng.normal(0, 5, len(wh))).round(1)
    wh["patchtst_delay_forecast"] = rng.random(len(wh)).round(3)
    wh.to_parquet(PROC / "forecast_scores_v0_dummy.parquet", index=False)

    # ---- predictions.csv, shap, reasons, metrics ----------------------------
    preds, shap_rows, reasons = [], [], []
    for risk, (etype, prefix, n) in RISKS.items():
        g = grid(etype, prefix, n)
        g = g[g["split"] == "test"][["entity_id", "date"]].copy()
        g["risk_type"] = risk
        g["probability"] = rng.beta(1.2, 3, len(g)).round(3)
        g["level"] = np.where(g["probability"] >= 0.6, "High", np.where(g["probability"] >= 0.3, "Medium", "Low"))
        preds.append(g)
    pr = pd.concat(preds, ignore_index=True)
    pr.to_csv(OUT / "predictions_v0_dummy.csv", index=False)

    feats = {"supplier_failure": ["supplier_delay_7d_avg", "news_tone_14d_trend", "single_source_flag"],
             "manufacturing_delay": ["delivery_delay_7d_avg", "production_ratio_7d_avg", "rain_7d_sum"],
             "warehouse_stockout": ["stock_days_cover", "demand_7d_avg", "mfg_delay_prob_oof"],
             "transport_disruption": ["rain_7d_sum", "port_news_tone_14d", "distance_km"]}
    sample = pr.sample(min(len(pr), 400), random_state=SEED)
    for _, r in sample.iterrows():
        vals = rng.normal(0, 0.8, 3).round(3)
        order = np.argsort(-np.abs(vals))
        for f, v in zip(feats[r.risk_type], vals):
            shap_rows.append({"entity_id": r.entity_id, "date": r.date, "risk_type": r.risk_type,
                              "feature": f, "shap_value": float(v)})
        top3 = "; ".join(feats[r.risk_type][i] for i in order)
        reasons.append({"entity_id": r.entity_id, "date": r.date, "risk_type": r.risk_type, "top3_reasons": top3})
    pd.DataFrame(shap_rows).to_parquet(OUT / "shap_values_v0_dummy.parquet", index=False)
    pd.DataFrame(reasons).to_csv(OUT / "reasons_v0_dummy.csv", index=False)

    m = []
    for model, base in [("catboost_multitarget", False), ("catboost_plain", True), ("xgboost", True)]:
        for risk in RISKS:
            m.append({"model": model, "risk_type": risk, "pr_auc": round(float(rng.uniform(0.3, 0.8)), 3),
                      "recall": round(float(rng.uniform(0.3, 0.8)), 3), "f1": round(float(rng.uniform(0.3, 0.8)), 3),
                      "is_baseline": base})
    pd.DataFrame(m).to_csv(OUT / "metrics_v0_dummy.csv", index=False)
    print("dummy files written to", PROC, "and", OUT)


if __name__ == "__main__":
    main()
