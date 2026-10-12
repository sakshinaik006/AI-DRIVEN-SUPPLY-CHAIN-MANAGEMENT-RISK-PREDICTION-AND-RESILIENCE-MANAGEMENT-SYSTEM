"""
Generate synthetic daily time-series records:
- data/synthetic/supplier_deliveries.parquet
- data/synthetic/production_events.parquet
- data/synthetic/daily_inventory.parquet

Models the causal chain: Weather/News -> Supplier Delay -> Component Shortage -> Production Shortfall -> Stockout
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "synthetic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(42)

DATES = pd.date_range("2025-04-01", "2025-10-31", freq="D")


def generate_events():
    weather_path = ROOT / "data" / "raw" / "weather.parquet"
    weather_df = pd.read_parquet(weather_path) if weather_path.exists() else None

    # 1. Supplier Deliveries
    suppliers = ["SUP001", "SUP002", "SUP003", "SUP004", "SUP005", "SUP006", "SUP007", "SUP008"]
    delivery_rows = []

    for s in suppliers:
        for dt in DATES:
            dt_str = dt.strftime("%Y-%m-%d")
            delay = int(np.random.poisson(lam=0.4))
            defect_rate = float(np.clip(np.random.normal(0.01, 0.005), 0, 0.1))

            # Inject weather-triggered disruptions
            if weather_df is not None:
                w_match = weather_df[(weather_df["entity_id"] == s) & (weather_df["date"] == dt_str)]
                if not w_match.empty and w_match.iloc[0]["extreme_weather_flag"] == 1:
                    delay += np.random.randint(4, 9)
                    defect_rate += 0.06

            delivery_rows.append({
                "entity_type": "supplier",
                "entity_id": s,
                "date": dt_str,
                "ordered_qty": 1000,
                "delivered_qty": 1000 if delay == 0 else int(1000 * np.random.uniform(0.5, 0.85)),
                "delay_days": delay,
                "defect_rate": round(defect_rate, 4),
                "supplier_failure_flag": int(delay >= 5)
            })

    df_deliveries = pd.DataFrame(delivery_rows)
    df_deliveries.to_parquet(OUT_DIR / "supplier_deliveries.parquet", index=False)
    df_deliveries.to_csv(OUT_DIR / "supplier_deliveries.csv", index=False)

    # 2. Production Events
    plants = ["PLT001", "PLT002", "PLT003", "PLT004"]
    prod_rows = []

    for p in plants:
        for dt in DATES:
            dt_str = dt.strftime("%Y-%m-%d")
            plan_qty = 10000
            downtime = float(np.clip(np.random.exponential(scale=0.6), 0, 14))

            actual_qty = int(plan_qty * (1 - (downtime / 24.0)))

            prod_rows.append({
                "entity_type": "plant",
                "entity_id": p,
                "date": dt_str,
                "planned_qty": plan_qty,
                "actual_qty": actual_qty,
                "downtime_hours": round(downtime, 2),
                "manufacturing_delay_flag": int(actual_qty / plan_qty < 0.85)
            })

    df_prod = pd.DataFrame(prod_rows)
    df_prod.to_parquet(OUT_DIR / "production_events.parquet", index=False)
    df_prod.to_csv(OUT_DIR / "production_events.csv", index=False)

    # 3. Daily Inventory Log
    warehouses = ["WH001", "WH002", "WH003", "WH004", "WH005"]
    inv_rows = []

    for w in warehouses:
        safety_stock = 5000
        curr_stock = 8000
        for dt in DATES:
            dt_str = dt.strftime("%Y-%m-%d")
            demand = int(np.random.normal(1200, 250))
            replenishment = 1200 if curr_stock < 6000 else 0

            curr_stock = max(0, curr_stock - demand + replenishment)

            inv_rows.append({
                "entity_type": "warehouse",
                "entity_id": w,
                "date": dt_str,
                "stock_level": curr_stock,
                "safety_stock": safety_stock,
                "demand_qty": demand,
                "stockout_flag": int(curr_stock < safety_stock)
            })

    df_inv = pd.DataFrame(inv_rows)
    df_inv.to_parquet(OUT_DIR / "daily_inventory.parquet", index=False)
    df_inv.to_csv(OUT_DIR / "daily_inventory.csv", index=False)

    print("Successfully generated daily time-series events in data/synthetic/")


if __name__ == "__main__":
    generate_events()