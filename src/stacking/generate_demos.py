"""Generate Verified Demo Cases and Visualizations directly from Model Predictions.

Audited and verified for Stage 5:
- Extracts genuine prediction records from outputs/predictions.csv.
- Replaces hardcoded demo probabilities with verified model predictions.
- Eliminates fabricated risk scores and ensures 100% consistency across demo files.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.explain.generate_shap_plots import generate_shap_visuals
OUT = ROOT / "outputs"
DEMOS_DIR = OUT / "demos"
DEMOS_DIR.mkdir(parents=True, exist_ok=True)


def generate_demo_cases():
    preds_path = OUT / "predictions.csv"
    if not preds_path.exists():
        raise FileNotFoundError(f"Missing {preds_path}. Run Stage 3 CatBoost training first!")

    preds = pd.read_csv(preds_path)

    # Helper to fetch exact verified record
    def get_exact_record(eid, dt, rt):
        sub = preds[(preds["entity_id"] == eid) & (preds["date"] == dt) & (preds["risk_type"] == rt)]
        if sub.empty:
            raise ValueError(f"No prediction record found for {eid} on {dt} ({rt})")
        row = sub.iloc[0]
        return {
            "entity_id": str(row["entity_id"]),
            "entity_type": str(row["entity_type"]),
            "risk_type": str(row["risk_type"]),
            "date": str(row["date"]),
            "risk_level": str(row["level"]).upper(),
            "probability": round(float(row["probability"]), 4),
        }

    # 1. Audited demo records
    case_1 = get_exact_record("SUP001", "2025-08-15", "supplier_failure")
    case_2 = get_exact_record("WH001", "2025-10-24", "warehouse_stockout")
    case_3 = get_exact_record("SUP008", "2025-04-15", "supplier_failure")

    # 2. Peak elevated risk records for demonstration
    peak_sup = preds[preds["risk_type"] == "supplier_failure"].sort_values("probability", ascending=False).iloc[0]
    peak_wh = preds[preds["risk_type"] == "warehouse_stockout"].sort_values("probability", ascending=False).iloc[0]

    demo_cases = {
        "case_1_high_supplier_risk": case_1,
        "case_2_stockout": case_2,
        "case_3_low_risk": case_3,
        "case_peak_supplier_risk": {
            "entity_id": str(peak_sup["entity_id"]),
            "entity_type": str(peak_sup["entity_type"]),
            "risk_type": str(peak_sup["risk_type"]),
            "date": str(peak_sup["date"]),
            "risk_level": str(peak_sup["level"]).upper(),
            "probability": round(float(peak_sup["probability"]), 4),
        },
        "case_peak_warehouse_stockout": {
            "entity_id": str(peak_wh["entity_id"]),
            "entity_type": str(peak_wh["entity_type"]),
            "risk_type": str(peak_wh["risk_type"]),
            "date": str(peak_wh["date"]),
            "risk_level": str(peak_wh["level"]).upper(),
            "probability": round(float(peak_wh["probability"]), 4),
        },
    }

    demo_cases_path = DEMOS_DIR / "demo_cases.json"
    with open(demo_cases_path, "w", encoding="utf-8") as f:
        json.dump(demo_cases, f, indent=4)

    print(f"[+] Verified demo cases saved to {demo_cases_path}:")
    for k, v in demo_cases.items():
        print(f"    - {k}: {v['entity_id']} ({v['date']}) -> Prob {v['probability']} ({v['risk_level']})")

    # Generate visual artifacts
    generate_shap_visuals()


if __name__ == "__main__":
    generate_demo_cases()