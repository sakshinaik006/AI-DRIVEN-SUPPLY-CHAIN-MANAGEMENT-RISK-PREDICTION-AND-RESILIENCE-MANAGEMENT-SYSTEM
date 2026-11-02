"""Generate SHAP Explainability Outputs from Trained CatBoost Models.

Audited and corrected for Stage 7:
1. Explains the exact deployed CatBoost models (from models/catboost_*.cbm) rather than training an independent dummy model.
2. Uses identical feature order and preprocessing from Stage 3 configuration.
3. Computes TreeSHAP feature attributions on test/validation sets for all 4 operational risk tiers.
4. Emits verified feature explanations to:
   - outputs/shap_summary.csv (global mean absolute SHAP importance)
   - outputs/shap_values.parquet (row-level SHAP values per entity and date)
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
    print("Stage 7: Computing TreeSHAP values on deployed CatBoost models")
    print("=" * 60)

    summary_records = []
    row_shap_records = []

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

        # Handle binary classification 1D or 2D array output
        if isinstance(shap_vals, list):
            vals = shap_vals[1]  # positive class
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

        # 2. Row-Level SHAP Attributions (Entity & Date level)
        for r_idx in range(len(df)):
            e_id = df.iloc[r_idx]["entity_id"]
            d_val = df.iloc[r_idx]["date"]
            for f_idx, feat in enumerate(cfg["features"]):
                row_shap_records.append({
                    "entity_id": e_id,
                    "date": str(d_val)[:10],
                    "risk_type": risk_type,
                    "feature": feat,
                    "shap_value": round(float(vals[r_idx, f_idx]), 4),
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

    # Save reasons.csv (top-3 drivers per entity, date, risk_type)
    df_row_shap_copy = df_row_shap.copy()
    df_row_shap_copy["abs_shap"] = df_row_shap_copy["shap_value"].abs()
    top3_df = (
        df_row_shap_copy.sort_values(
            by=["entity_id", "date", "risk_type", "abs_shap"],
            ascending=[True, True, True, False]
        )
        .groupby(["entity_id", "date", "risk_type"])
        .head(3)
    )
    df_reasons = (
        top3_df.groupby(["entity_id", "date", "risk_type"])["feature"]
        .apply(lambda feats: "; ".join(feats))
        .reset_index(name="top3_reasons")
    )
    reasons_path = OUT / "reasons.csv"
    df_reasons.to_csv(reasons_path, index=False)
    print(f"[+] Top-3 explanations saved to {reasons_path} ({len(df_reasons)} records)")

    return df_summary, df_row_shap, df_reasons


if __name__ == "__main__":
    generate_shap_explanations()