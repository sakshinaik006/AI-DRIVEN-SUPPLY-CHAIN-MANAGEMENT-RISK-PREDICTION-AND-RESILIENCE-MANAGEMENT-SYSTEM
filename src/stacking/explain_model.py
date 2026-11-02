"""Generate SHAP Explainability Outputs from Trained CatBoost Models.

Audited and corrected for Stage 5:
1. Explains the exact deployed CatBoost models (from models/catboost_*.cbm) using identical training features.
2. Computes TreeSHAP feature attributions on all 4 operational risk tiers.
3. Emits verified feature explanations to:
   - outputs/shap_summary.csv (global mean absolute SHAP importance)
   - outputs/shap_values.parquet (row-level SHAP values per entity and date)
   - outputs/reasons.csv (schema-aligned with reason_1/shap_1, reason_2/shap_2, reason_3/shap_3, and top3_reasons)
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import shap
from catboost import CatBoostClassifier

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

TIER_CONFIG = {
    "supplier_failure": {
        "file": "features_supplier_v1.parquet",
        "features": ["supplier_delay_7d_avg", "rain_7d_sum", "news_tone_14d_trend", "single_source_flag"],
        "cat_features": ["single_source_flag"],
    },
    "manufacturing_delay": {
        "file": "features_manufacturing_v1.parquet",
        "features": ["delivery_delay_7d_avg", "production_ratio_7d_avg", "rain_7d_sum", "supplier_failure_prob_oof"],
        "cat_features": [],
    },
    "warehouse_stockout": {
        "file": "features_warehouse_v1.parquet",
        "features": ["demand_7d_avg", "stock_days_cover", "inventory_level", "mfg_delay_prob_oof"],
        "cat_features": [],
    },
    "transport_disruption": {
        "file": "features_transport_v1.parquet",
        "features": ["delivery_delay_7d_avg", "rain_7d_sum", "port_news_tone_14d", "distance_km", "shipping_mode"],
        "cat_features": ["shipping_mode"],
    },
}


def generate_shap_explanations():
    print("=" * 60)
    print("Stage 5: Computing TreeSHAP values on deployed CatBoost models")
    print("=" * 60)

    summary_records = []
    row_shap_records = []
    reasons_records = []

    for risk_type, cfg in TIER_CONFIG.items():
        model_path = MODELS_DIR / f"catboost_{risk_type}.cbm"
        if not model_path.exists():
            raise FileNotFoundError(f"Missing trained model artifact: {model_path}! Run Stage 3 first.")

        data_path = PROC / cfg["file"]
        df = pd.read_parquet(data_path)
        print(f"\n[+] Explaining {risk_type} using {model_path.name}...")

        # Load deployed model
        model = CatBoostClassifier()
        model.load_model(str(model_path))

        # Format input feature matrix exactly as trained
        X = df[cfg["features"]].copy()
        for cat in cfg["cat_features"]:
            if cat in X.columns:
                X[cat] = X[cat].astype(str)

        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X)

        if isinstance(shap_vals, list):
            vals = shap_vals[1]
        elif len(shap_vals.shape) == 3:
            vals = shap_vals[:, :, 1]
        else:
            vals = shap_vals

        # 1. Global Mean Absolute SHAP Importance
        mean_abs_shap = np.abs(vals).mean(axis=0)
        for idx, feat in enumerate(cfg["features"]):
            summary_records.append({
                "target_risk": risk_type,
                "feature_name": feat,
                "mean_shap_importance": round(float(mean_abs_shap[idx]), 4),
            })

        # 2. Row-Level SHAP Attributions & Instance Top-3 Drivers
        for r_idx in range(len(df)):
            e_id = df.iloc[r_idx]["entity_id"]
            d_val = str(df.iloc[r_idx]["date"])[:10]
            instance_shap = []

            for f_idx, feat in enumerate(cfg["features"]):
                sv = round(float(vals[r_idx, f_idx]), 4)
                row_shap_records.append({
                    "entity_id": e_id,
                    "date": d_val,
                    "risk_type": risk_type,
                    "feature": feat,
                    "shap_value": sv,
                })
                instance_shap.append((feat, sv))

            # Sort by absolute SHAP impact descending
            instance_shap_sorted = sorted(instance_shap, key=lambda x: abs(x[1]), reverse=True)
            top3 = instance_shap_sorted[:3]

            r1, s1 = top3[0] if len(top3) > 0 else ("none", 0.0)
            r2, s2 = top3[1] if len(top3) > 1 else ("none", 0.0)
            r3, s3 = top3[2] if len(top3) > 2 else ("none", 0.0)

            top3_str = "; ".join([item[0] for item in top3])

            reasons_records.append({
                "entity_id": e_id,
                "date": d_val,
                "risk_type": risk_type,
                "top3_reasons": top3_str,
                "reason_1": r1,
                "shap_1": s1,
                "reason_2": r2,
                "shap_2": s2,
                "reason_3": r3,
                "shap_3": s3,
            })

    # Save global summary
    df_summary = pd.DataFrame(summary_records).sort_values(
        by=["target_risk", "mean_shap_importance"], ascending=[True, False]
    )
    summary_path = OUT / "shap_summary.csv"
    df_summary.to_csv(summary_path, index=False)
    print(f"\n[+] Global SHAP summary saved to {summary_path}")

    # Save row-level SHAP parquet
    df_row_shap = pd.DataFrame(row_shap_records)
    row_shap_path = OUT / "shap_values.parquet"
    df_row_shap.to_parquet(row_shap_path, index=False)
    print(f"[+] Row-level SHAP attributions saved to {row_shap_path} ({len(df_row_shap)} records)")

    # Save reasons.csv (with schema matching generate_shap_plots.py and API contracts)
    df_reasons = pd.DataFrame(reasons_records)
    reasons_path = OUT / "reasons.csv"
    df_reasons.to_csv(reasons_path, index=False)
    print(f"[+] Top-3 explanations with reason_1..3 and shap_1..3 saved to {reasons_path} ({len(df_reasons)} records)")

    return df_summary, df_row_shap, df_reasons


if __name__ == "__main__":
    generate_shap_explanations()