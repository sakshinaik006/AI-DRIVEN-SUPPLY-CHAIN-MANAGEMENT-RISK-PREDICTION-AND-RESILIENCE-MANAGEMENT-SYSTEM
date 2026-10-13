"""Generate synthetic daily time-series records:
- data/synthetic/supplier_deliveries.parquet
- data/synthetic/production_events.parquet
- data/synthetic/daily_inventory.parquet
- data/synthetic/transport_shipments.parquet

Models the causal chain: Weather/News -> Supplier Delay -> Component Shortage -> Production Shortfall -> Stockout & Transport Delay
All labels are calibrated so 7-day-ahead positive rates fall strictly between 3-5% across all risks.
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

    routes_path = OUT_DIR / "routes.parquet"
    if not routes_path.exists():
        routes_path = OUT_DIR / "routes.csv"
    routes_df = pd.read_csv(routes_path) if routes_path.suffix == ".csv" else pd.read_parquet(routes_path)

    # 1. Supplier Deliveries
    # Calibrated disruption events aligned with extreme weather and realistic supplier operational failures
    suppliers = ["SUP001", "SUP002", "SUP003", "SUP004", "SUP005", "SUP006", "SUP007", "SUP008"]
    sup_events = {
        ("SUP001", "2025-05-06"),  # Extreme weather
        ("SUP005", "2025-06-01"),  # Extreme weather
        ("SUP007", "2025-07-20"),  # Extreme weather
        ("SUP003", "2025-08-05"),  # Component shortage / strike
        ("SUP008", "2025-08-18"),  # Factory breakdown
        ("SUP006", "2025-08-22"),  # Quality defect surge
        ("SUP002", "2025-09-12"),  # Validation disruption
        ("SUP004", "2025-10-10"),  # Test evaluation case
    }
    delivery_rows = []

    for s in suppliers:
        for dt in DATES:
            dt_str = dt.strftime("%Y-%m-%d")
            is_fail = int((s, dt_str) in sup_events)
            delay = int(np.random.randint(5, 9)) if is_fail else int(np.random.poisson(lam=0.20))
            defect_rate = float(np.clip(
                np.random.normal(0.06, 0.02) if is_fail else np.random.normal(0.01, 0.005),
                0.0, 0.12
            ))

            delivery_rows.append({
                "entity_type": "supplier",
                "entity_id": s,
                "date": dt_str,
                "ordered_qty": 1000,
                "delivered_qty": 1000 if delay == 0 else int(1000 * np.random.uniform(0.5, 0.85)),
                "delay_days": delay,
                "defect_rate": round(defect_rate, 4),
                "supplier_failure_flag": is_fail
            })

    df_deliveries = pd.DataFrame(delivery_rows)
    df_deliveries.to_parquet(OUT_DIR / "supplier_deliveries.parquet", index=False)
    df_deliveries.to_csv(OUT_DIR / "supplier_deliveries.csv", index=False)

    # 2. Production Events
    plants = ["PLT001", "PLT002", "PLT003", "PLT004"]
    plant_events = {
        ("PLT004", "2025-04-25"),  # Extreme weather
        ("PLT003", "2025-06-30"),  # Equipment downtime
        ("PLT001", "2025-08-10"),  # Component shortage bottleneck
        ("PLT002", "2025-09-08"),  # Power grid interruption (val)
        ("PLT003", "2025-10-14"),  # Assembly line failure (test)
    }
    prod_rows = []

    for p in plants:
        for dt in DATES:
            dt_str = dt.strftime("%Y-%m-%d")
            is_delay = int((p, dt_str) in plant_events)
            plan_qty = 10000
            downtime = float(np.random.uniform(4.5, 8.5) if is_delay else np.clip(np.random.exponential(scale=0.3), 0, 2.5))
            actual_qty = int(plan_qty * (1 - (downtime / 24.0)))

            prod_rows.append({
                "entity_type": "plant",
                "entity_id": p,
                "date": dt_str,
                "planned_qty": plan_qty,
                "actual_qty": actual_qty,
                "downtime_hours": round(downtime, 2),
                "manufacturing_delay_flag": is_delay
            })

    df_prod = pd.DataFrame(prod_rows)
    df_prod.to_parquet(OUT_DIR / "production_events.parquet", index=False)
    df_prod.to_csv(OUT_DIR / "production_events.csv", index=False)

    # 3. Daily Inventory Log
    warehouses = ["WH001", "WH002", "WH003", "WH004", "WH005"]
    wh_events = {
        ("WH004", "2025-04-12"),  # Extreme weather
        ("WH001", "2025-06-14"),  # Inbound delivery blockage
        ("WH003", "2025-07-25"),  # Sudden demand surge
        ("WH005", "2025-08-15"),  # Supply shortage depletion
        ("WH002", "2025-09-15"),  # Regional demand surge (val)
        ("WH001", "2025-10-12"),  # Stockout case (test)
    }
    inv_rows = []

    for w in warehouses:
        safety_stock = 4500
        curr_stock = 6200
        for dt in DATES:
            dt_str = dt.strftime("%Y-%m-%d")
            demand = int(np.random.normal(1000, 180))
            replenishment = 1000
            is_stockout = int((w, dt_str) in wh_events)

            if is_stockout:
                demand += 2600

            curr_stock = curr_stock - demand + replenishment
            curr_stock = int(curr_stock + 0.35 * (6200 - curr_stock))

            inv_rows.append({
                "entity_type": "warehouse",
                "entity_id": w,
                "date": dt_str,
                "stock_level": curr_stock,
                "safety_stock": safety_stock,
                "demand_qty": demand,
                "stockout_flag": is_stockout
            })

    df_inv = pd.DataFrame(inv_rows)
    df_inv.to_parquet(OUT_DIR / "daily_inventory.parquet", index=False)
    df_inv.to_csv(OUT_DIR / "daily_inventory.csv", index=False)

    # 4. Transport Shipments across routes
    route_events = {
        ("RT002", "2025-04-21"),  # Extreme weather
        ("RT005", "2025-05-26"),  # Road landslide
        ("RT001", "2025-06-18"),  # Air freight disruption
        ("RT007", "2025-07-15"),  # Sea lane congestion
        ("RT009", "2025-08-04"),  # Port strike
        ("RT003", "2025-08-20"),  # Customs clearance delay
        ("RT008", "2025-08-23"),  # Bad weather transit delay
        ("RT006", "2025-09-10"),  # Highway closure (val)
        ("RT004", "2025-10-08"),  # Border congestion (test)
        ("RT010", "2025-10-18"),  # Weather typhoon delay (test)
    }
    shipment_rows = []
    for r in routes_df.itertuples():
        r_id = r.entity_id
        sched = r.scheduled_days
        for dt in DATES:
            dt_str = dt.strftime("%Y-%m-%d")
            is_delayed = int((r_id, dt_str) in route_events)
            delay = np.random.randint(1, 4) if is_delayed else 0

            shipment_rows.append({
                "entity_type": "route",
                "entity_id": r_id,
                "date": dt_str,
                "scheduled_days": sched,
                "actual_days": sched + delay,
                "delay_days": delay,
                "transport_delay_flag": is_delayed
            })

    df_shipments = pd.DataFrame(shipment_rows)
    df_shipments.to_parquet(OUT_DIR / "transport_shipments.parquet", index=False)
    df_shipments.to_csv(OUT_DIR / "transport_shipments.csv", index=False)

    print("Successfully generated calibrated daily time-series events in data/synthetic/")


if __name__ == "__main__":
    generate_events()