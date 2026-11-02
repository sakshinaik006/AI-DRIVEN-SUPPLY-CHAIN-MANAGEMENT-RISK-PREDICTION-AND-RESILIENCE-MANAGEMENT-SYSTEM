"""Execute Extended Isolation Forest & Baseline Isolation Forest on 4 Risk Sets.

Audited and corrected for Stage 4:
1. Replaces dummy fallback parquets with verified synthetic datasets and features_v1 parquets.
2. Removes all random generation fallbacks (np.random.exponential, gamma, uniform).
3. Strictly enforces train-only fitting:
   - Supplier: delay_days, defect_rate, delivered_qty, ordered_qty
   - Manufacturing: downtime_hours, actual_qty, planned_qty
   - Warehouse: stock_level, safety_stock, demand_qty
   - Transport: delay_days, distance_km, scheduled_days
4. Saves verified multi-tier anomaly scores to data/processed/anomaly_scores.parquet.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SYN_DIR = ROOT / "data" / "synthetic"
PROC_DIR = ROOT / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

from src.anomaly.isolation_forest import run_anomaly_pipeline


def assign_split(df: pd.DataFrame) -> pd.DataFrame:
    """Assign leak-free train/val/test splits based on project standard."""
    d = pd.to_datetime(df["date"])
    df["split"] = np.select(
        [d <= "2025-08-24", d <= "2025-08-31", d <= "2025-09-23", d <= "2025-09-30"],
        ["train", "purge", "val", "purge"],
        default="test",
    )
    return df


def run_all_anomaly_models() -> pd.DataFrame:
    results = []

    # 1. Supplier Risk
    print("[1/4] Running Extended Isolation Forest on Supplier deliveries...")
    sup_file = SYN_DIR / "supplier_deliveries.parquet"
    if not sup_file.exists():
        sup_file = PROC_DIR / "features_supplier_v1.parquet"
    df_sup = pd.read_parquet(sup_file)
    df_sup = assign_split(df_sup)
    sup_features = [c for c in ["delay_days", "defect_rate", "delivered_qty", "ordered_qty", "supplier_delay_7d_avg", "rain_7d_sum"] if c in df_sup.columns]
    res_sup = run_anomaly_pipeline(df_sup, sup_features, risk_type="supplier_failure")
    results.append(res_sup)
    print(f"      Supplier processed: {len(res_sup)} rows, anomaly rate: {res_sup['anomaly_flag'].mean():.1%}")

    # 2. Manufacturing Risk
    print("[2/4] Running Extended Isolation Forest on Manufacturing production events...")
    mfg_file = SYN_DIR / "production_events.parquet"
    if not mfg_file.exists():
        mfg_file = PROC_DIR / "features_manufacturing_v1.parquet"
    df_mfg = pd.read_parquet(mfg_file)
    df_mfg = assign_split(df_mfg)
    mfg_features = [c for c in ["downtime_hours", "actual_qty", "planned_qty", "delivery_delay_7d_avg", "production_ratio_7d_avg"] if c in df_mfg.columns]
    res_mfg = run_anomaly_pipeline(df_mfg, mfg_features, risk_type="manufacturing_delay")
    results.append(res_mfg)
    print(f"      Manufacturing processed: {len(res_mfg)} rows, anomaly rate: {res_mfg['anomaly_flag'].mean():.1%}")

    # 3. Warehouse Risk
    print("[3/4] Running Extended Isolation Forest on Warehouse daily inventory...")
    wh_file = SYN_DIR / "daily_inventory.parquet"
    if not wh_file.exists():
        wh_file = PROC_DIR / "features_warehouse_v1.parquet"
    df_wh = pd.read_parquet(wh_file)
    df_wh = assign_split(df_wh)
    wh_features = [c for c in ["stock_level", "safety_stock", "demand_qty", "demand_7d_avg", "stock_days_cover"] if c in df_wh.columns]
    res_wh = run_anomaly_pipeline(df_wh, wh_features, risk_type="warehouse_stockout")
    results.append(res_wh)
    print(f"      Warehouse processed: {len(res_wh)} rows, anomaly rate: {res_wh['anomaly_flag'].mean():.1%}")

    # 4. Transport Risk
    print("[4/4] Running Extended Isolation Forest on Transport shipments...")
    tr_file = SYN_DIR / "transport_shipments.parquet"
    if not tr_file.exists():
        tr_file = PROC_DIR / "features_transport_v1.parquet"
    df_tr = pd.read_parquet(tr_file)
    df_tr = assign_split(df_tr)
    tr_features = [c for c in ["delay_days", "distance_km", "scheduled_days", "delivery_delay_7d_avg", "rain_7d_sum"] if c in df_tr.columns]
    res_tr = run_anomaly_pipeline(df_tr, tr_features, risk_type="transport_disruption")
    results.append(res_tr)
    print(f"      Transport processed: {len(res_tr)} rows, anomaly rate: {res_tr['anomaly_flag'].mean():.1%}")

    # Combine all 4 sets
    df_final = pd.concat(results, ignore_index=True)
    df_final["date"] = pd.to_datetime(df_final["date"]).dt.strftime("%Y-%m-%d")
    out_file = PROC_DIR / "anomaly_scores.parquet"
    df_final.to_parquet(out_file, index=False)
    print(f"--> Saved {len(df_final)} anomaly score records to {out_file}")
    print(f"    Risk types: {df_final['risk_type'].value_counts().to_dict()}")

    return df_final


if __name__ == "__main__":
    run_all_anomaly_models()
