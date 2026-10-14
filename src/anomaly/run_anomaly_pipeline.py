"""Execute Extended Isolation Forest & Baseline Isolation Forest on 4 Risk Sets.

Strict train-only fitting on:
  1. Supplier: delay_days, defect_rate, delivered_qty, ordered_qty
  2. Manufacturing: downtime_hours, actual_qty, planned_qty
  3. Warehouse: stock_level, safety_stock, demand_qty
  4. Transport: delivery_delay_7d_avg, rain_7d_sum, distance_km

Outputs:
  data/processed/anomaly_scores.parquet
Columns:
  entity_id, date, risk_type, anomaly_score, anomaly_flag, if_baseline_score
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
    if sup_file.exists():
        df_sup = pd.read_parquet(sup_file)
    else:
        df_sup = pd.read_parquet(PROC_DIR / "features_supplier_v0_dummy.parquet")
    df_sup = assign_split(df_sup)
    sup_features = [c for c in ["delay_days", "defect_rate", "delivered_qty", "ordered_qty", "supplier_delay_7d_avg", "rain_7d_sum"] if c in df_sup.columns]
    res_sup = run_anomaly_pipeline(df_sup, sup_features, risk_type="supplier_failure")
    results.append(res_sup)
    print(f"      Supplier processed: {len(res_sup)} rows, anomaly rate: {res_sup['anomaly_flag'].mean():.1%}")

    # 2. Manufacturing Risk
    print("[2/4] Running Extended Isolation Forest on Manufacturing production events...")
    mfg_file = SYN_DIR / "production_events.parquet"
    if mfg_file.exists():
        df_mfg = pd.read_parquet(mfg_file)
    else:
        df_mfg = pd.read_parquet(PROC_DIR / "features_manufacturing_v0_dummy.parquet")
    df_mfg = assign_split(df_mfg)
    mfg_features = [c for c in ["downtime_hours", "actual_qty", "planned_qty", "delivery_delay_7d_avg", "production_ratio_7d_avg"] if c in df_mfg.columns]
    res_mfg = run_anomaly_pipeline(df_mfg, mfg_features, risk_type="manufacturing_delay")
    results.append(res_mfg)
    print(f"      Manufacturing processed: {len(res_mfg)} rows, anomaly rate: {res_mfg['anomaly_flag'].mean():.1%}")

    # 3. Warehouse Risk
    print("[3/4] Running Extended Isolation Forest on Warehouse daily inventory...")
    wh_file = SYN_DIR / "daily_inventory.parquet"
    if wh_file.exists():
        df_wh = pd.read_parquet(wh_file)
    else:
        df_wh = pd.read_parquet(PROC_DIR / "features_warehouse_v0_dummy.parquet")
    df_wh = assign_split(df_wh)
    wh_features = [c for c in ["stock_level", "safety_stock", "demand_qty", "demand_7d_avg", "stock_days_cover"] if c in df_wh.columns]
    res_wh = run_anomaly_pipeline(df_wh, wh_features, risk_type="warehouse_stockout")
    results.append(res_wh)
    print(f"      Warehouse processed: {len(res_wh)} rows, anomaly rate: {res_wh['anomaly_flag'].mean():.1%}")

    # 4. Transport Risk
    print("[4/4] Running Extended Isolation Forest on Transport routes...")
    tr_file = PROC_DIR / "features_transport_v0_dummy.parquet"
    if tr_file.exists():
        df_tr = pd.read_parquet(tr_file)
    else:
        # Generate synthetic transport grid if needed
        routes = [f"RT{i:03d}" for i in range(1, 11)]
        dates = pd.date_range("2025-04-01", "2025-10-31", freq="D").strftime("%Y-%m-%d")
        df_tr = pd.MultiIndex.from_product([routes, dates], names=["entity_id", "date"]).to_frame(index=False)
        df_tr["delivery_delay_7d_avg"] = np.random.exponential(1.2, len(df_tr))
        df_tr["rain_7d_sum"] = np.random.gamma(2.0, 5.0, len(df_tr))
        df_tr["distance_km"] = np.random.uniform(500, 8000, len(df_tr))
    df_tr = assign_split(df_tr)
    tr_features = [c for c in ["delivery_delay_7d_avg", "rain_7d_sum", "distance_km"] if c in df_tr.columns]
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
