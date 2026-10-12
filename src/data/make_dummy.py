"""Generate dummy files in the agreed interface format (docs/interface.md v1.1).

Run from the repo root:  python -m src.data.make_dummy
Everything is seeded, so the output is reproducible. These are PLACEHOLDERS so
Members 2 and 3 can start work; they are replaced by real data v1 later.

Changes in v1.1: purge split, last 7 days of Oct unlabeled (NaN, rows kept),
outputs/levels.json, split + precision in metrics, entity_type on every
entity-day table, entity ids and cities read from the master tables
(data/synthetic/*.csv) when they exist, probability = sigmoid(raw_score).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
START, END = "2025-04-01", "2025-10-31"
LABEL_END = "2025-10-24"  # labels need t+7 inside the window
ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
SYN = ROOT / "data" / "synthetic"
OUT = ROOT / "outputs"

# entity_type -> (id prefix, master table name, fallback count)
MASTER = {
    "supplier": ("SUP", "suppliers", 8),
    "plant": ("PLT", "plants", 4),
    "warehouse": ("WH", "warehouses", 5),
    "route": ("RT", "routes", 10),
}
RISKS = {
    "supplier_failure": "supplier",
    "manufacturing_delay": "plant",
    "warehouse_stockout": "warehouse",
    "transport_disruption": "route",
}
THEMES = ["shortage", "strike", "flood", "shutdown", "port_congestion"]
FALLBACK_CITIES = [("Shenzhen", "China"), ("Chennai", "India"), ("Seoul", "South Korea")]
LEVELS = {"low_max": 0.30, "high_min": 0.60}  # placeholders, M3 tunes on val
BASE_VALUE = -2.5


def split_of(d: pd.Series) -> np.ndarray:
    """train to 24 Aug | purge 25-31 Aug | val 1-23 Sep | purge 24-30 Sep | test Oct."""
    d = pd.to_datetime(d)
    return np.select(
        [d <= "2025-08-24", d <= "2025-08-31", d <= "2025-09-23", d <= "2025-09-30"],
        ["train", "purge", "val", "purge"],
        default="test",
    )


def ids_for(etype: str) -> list[str]:
    prefix, table, n = MASTER[etype]
    p = SYN / f"{table}.csv"
    if p.exists():
        return list(pd.read_csv(p)["entity_id"])
    return [f"{prefix}{i:03d}" for i in range(1, n + 1)]


def grid(etype: str) -> pd.DataFrame:
    dates = pd.date_range(START, END, freq="D")
    df = pd.MultiIndex.from_product([ids_for(etype), dates], names=["entity_id", "date"]).to_frame(index=False)
    df.insert(0, "entity_type", etype)
    df["split"] = split_of(df["date"])
    return df


def master_cities() -> list[tuple[str, str]]:
    out = []
    for t in ("suppliers", "plants", "warehouses"):
        p = SYN / f"{t}.csv"
        if p.exists():
            m = pd.read_csv(p)
            out += list(zip(m["city"], m["country"]))
    return sorted(set(out)) or FALLBACK_CITIES


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def main():
    rng = np.random.default_rng(SEED)
    PROC.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    # ---- levels.json --------------------------------------------------------
    (OUT / "levels.json").write_text(json.dumps(LEVELS, indent=2))

    # ---- feature tables (4) -------------------------------------------------
    feature_cols = {
        "supplier": ["supplier_delay_7d_avg", "rain_7d_sum", "news_tone_14d_trend", "single_source_flag"],
        "plant": ["delivery_delay_7d_avg", "production_ratio_7d_avg", "rain_7d_sum", "supplier_failure_prob_oof"],
        "warehouse": ["demand_7d_avg", "stock_days_cover", "inventory_level", "mfg_delay_prob_oof"],
        "route": ["delivery_delay_7d_avg", "rain_7d_sum", "port_news_tone_14d", "distance_km", "shipping_mode"],
    }
    file_names = {"supplier": "supplier", "plant": "manufacturing", "warehouse": "warehouse", "route": "transport"}
    for risk, etype in RISKS.items():
        df = grid(etype)
        cols = feature_cols[etype]
        for c in cols:
            if c == "shipping_mode":
                df[c] = rng.choice(["air", "sea", "road"], len(df))
            elif c == "single_source_flag":
                df[c] = rng.integers(0, 2, len(df))
            else:
                df[c] = rng.normal(0, 1, len(df)).round(3)
        p = sigmoid(df[cols[0]].astype(float) * 0.8 - 3.2)
        df["label_7d"] = (rng.random(len(df)) < p).astype(float)
        df.loc[df["date"] > LABEL_END, "label_7d"] = np.nan  # no full look-ahead window
        df.to_parquet(PROC / f"features_{file_names[etype]}_v0_dummy.parquet", index=False)
        ok = df[(df["split"] != "purge") & df["label_7d"].notna()]
        print(f"features_{file_names[etype]}: {len(df)} rows, positives {ok['label_7d'].mean():.1%}")

    # ---- graph_scores (no date; hgt_score null until HGT is done) -----------
    rows = []
    for e in ids_for("supplier") + ids_for("route"):
        is_sup = e.startswith("SUP")
        rows.append({
            "entity_id": e,
            "dependency_count": int(rng.integers(1, 6)) if is_sup else 0,
            "hgt_score": np.nan,
            "route_importance": np.nan if is_sup else round(float(rng.random()), 3),
        })
    pd.DataFrame(rows).to_parquet(PROC / "graph_scores_v0_dummy.parquet", index=False)

    # ---- gdelt_headlines (cities come from the master tables) ---------------
    cities = master_cities()
    heads = []
    for d in pd.date_range(START, END, freq="D"):
        for _ in range(int(rng.integers(0, 4))):
            city, country = cities[int(rng.integers(0, len(cities)))]
            theme = THEMES[int(rng.integers(0, len(THEMES)))]
            heads.append({"date": d, "title": f"{theme.replace('_', ' ').title()} reported near {city}",
                          "country": country, "city": city, "theme": theme,
                          "tone": round(float(rng.normal(-2, 2)), 2)})
    pd.DataFrame(heads).to_parquet(PROC / "gdelt_headlines_v0_dummy.parquet", index=False)

    # ---- news_scores, anomaly_scores, forecast_scores -----------------------
    sup = grid("supplier")
    sup["text_risk"] = rng.random(len(sup)).round(3)
    sup["text_risk_7d"] = sup.groupby("entity_id")["text_risk"].transform(
        lambda s: s.rolling(7, min_periods=1).mean().shift(1)).round(3)
    sup["disruption_type"] = rng.choice(THEMES, len(sup))
    sup["tone"] = rng.normal(-2, 2, len(sup)).round(2)
    sup.to_parquet(PROC / "news_scores_v0_dummy.parquet", index=False)

    an = []
    for risk, etype in RISKS.items():
        g = grid(etype)
        g["risk_type"] = risk
        g["anomaly_score"] = rng.random(len(g)).round(3)
        g["anomaly_flag"] = (g["anomaly_score"] > 0.9).astype(int)
        g["if_baseline_score"] = rng.random(len(g)).round(3)
        an.append(g)
    pd.concat(an, ignore_index=True).to_parquet(PROC / "anomaly_scores_v0_dummy.parquet", index=False)

    wh = grid("warehouse")
    wh["forecast_demand"] = rng.normal(100, 15, len(wh)).round(1)
    wh["forecast_gap"] = rng.normal(0, 10, len(wh)).round(1)
    wh["demand_surge_flag"] = (wh["forecast_gap"] > 15).astype(int)
    wh["chronos_forecast"] = (wh["forecast_demand"] + rng.normal(0, 5, len(wh))).round(1)
    wh["patchtst_delay_forecast"] = rng.random(len(wh)).round(3)
    wh.to_parquet(PROC / "forecast_scores_v0_dummy.parquet", index=False)

    # ---- predictions, SHAP, reasons (consistent: base + sum(shap) = raw) ----
    feats = {"supplier_failure": ["supplier_delay_7d_avg", "news_tone_14d_trend", "single_source_flag"],
             "manufacturing_delay": ["delivery_delay_7d_avg", "production_ratio_7d_avg", "rain_7d_sum"],
             "warehouse_stockout": ["stock_days_cover", "demand_7d_avg", "mfg_delay_prob_oof"],
             "transport_disruption": ["rain_7d_sum", "port_news_tone_14d", "distance_km"]}
    preds, shap_rows, reasons = [], [], []
    for risk, etype in RISKS.items():
        g = grid(etype)
        g = g[g["split"] == "test"][["entity_id", "date"]].reset_index(drop=True)
        vals = rng.normal(0, 1.0, (len(g), 3)).round(3)
        raw = BASE_VALUE + vals.sum(axis=1)
        g["risk_type"] = risk
        g["probability"] = sigmoid(raw).round(3)
        g["level"] = np.where(g["probability"] >= LEVELS["high_min"], "High",
                              np.where(g["probability"] >= LEVELS["low_max"], "Medium", "Low"))
        preds.append(g)
        for i, r in g.iterrows():
            order = np.argsort(-np.abs(vals[i]))
            for f, v in zip(feats[risk], vals[i]):
                shap_rows.append({"entity_id": r.entity_id, "date": r.date, "risk_type": risk,
                                  "feature": f, "shap_value": float(v), "base_value": BASE_VALUE})
            reasons.append({"entity_id": r.entity_id, "date": r.date, "risk_type": risk,
                            "base_value": BASE_VALUE, "raw_score": round(float(raw[i]), 3),
                            "top3_reasons": "; ".join(feats[risk][j] for j in order)})
    pr = pd.concat(preds, ignore_index=True)
    pr.to_csv(OUT / "predictions_v0_dummy.csv", index=False)
    pd.DataFrame(shap_rows).to_parquet(OUT / "shap_values_v0_dummy.parquet", index=False)
    pd.DataFrame(reasons).to_csv(OUT / "reasons_v0_dummy.csv", index=False)

    # ---- metrics (test split, with precision) -------------------------------
    m = []
    for model, base in [("catboost_multitarget", False), ("catboost_plain", True), ("xgboost", True)]:
        for risk in RISKS:
            m.append({"model": model, "risk_type": risk, "split": "test",
                      "pr_auc": round(float(rng.uniform(0.3, 0.8)), 3),
                      "precision": round(float(rng.uniform(0.3, 0.8)), 3),
                      "recall": round(float(rng.uniform(0.3, 0.8)), 3),
                      "f1": round(float(rng.uniform(0.3, 0.8)), 3),
                      "is_baseline": base})
    pd.DataFrame(m).to_csv(OUT / "metrics_v0_dummy.csv", index=False)
    print("High/Medium/Low share:", pr["level"].value_counts(normalize=True).round(3).to_dict())
    print("dummy files written to", PROC, "and", OUT)


if __name__ == "__main__":
    main()
