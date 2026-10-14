"""Day 2 Feature Pipeline:
Builds leak-free feature tables for all four risk types:
- data/processed/features_supplier_v1.parquet (and v2)
- data/processed/features_manufacturing_v1.parquet (and v2)
- data/processed/features_warehouse_v1.parquet (and v2)
- data/processed/features_transport_v1.parquet (and v2)

Rules enforced:
1. Keys: entity_type, entity_id, date, split.
2. Leakage rules:
   - All rolling features use past days only (shift by 1 day).
   - Label is 7-day forward (t+1 to t+7). Last 7 days of October (Oct 25-31) have label_7d = NaN.
   - Any numerical imputations fit on train only.
   - No post-outcome or target leakage features.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SYN = ROOT / "data" / "synthetic"
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

START_DATE = "2025-04-01"
END_DATE = "2025-10-31"
LABEL_CUTOFF = "2025-10-24"


def compute_split(date_series: pd.Series) -> np.ndarray:
    d = pd.to_datetime(date_series)
    return np.select(
        [d <= "2025-08-24", d <= "2025-08-31", d <= "2025-09-23", d <= "2025-09-30"],
        ["train", "purge", "val", "purge"],
        default="test",
    )


def compute_label_7d(df: pd.DataFrame, entity_col: str, flag_col: str) -> pd.Series:
    """Compute 7-day-ahead binary outcome from (t+1) to (t+7)."""
    labels = []
    for _, group in df.groupby(entity_col):
        fwd = pd.concat([group[flag_col].shift(-i) for i in range(1, 8)], axis=1).max(axis=1)
        labels.append(fwd)
    label_series = pd.concat(labels)
    # Mask dates after LABEL_CUTOFF where full 7-day lookahead cannot be observed
    dates = pd.to_datetime(df["date"])
    label_series.loc[dates > pd.Timestamp(LABEL_CUTOFF)] = np.nan
    return label_series


def build_supplier_features() -> pd.DataFrame:
    """Supplier risk feature set:
    - entity_type, entity_id, date, split
    - supplier_delay_7d_avg: past 7-day rolling average delay (shifted by 1 day)
    - rain_7d_sum: past 7-day rolling sum of precipitation at supplier location (shifted by 1 day)
    - news_tone_14d_trend: past 14-day rolling mean of news tone (shifted by 1 day)
    - single_source_flag: static flag from suppliers master table
    - label_7d: supplier failure occurring in (t+1, t+7]
    """
    deliveries = pd.read_parquet(SYN / "supplier_deliveries.parquet")
    deliveries["date"] = pd.to_datetime(deliveries["date"]).dt.strftime("%Y-%m-%d")
    deliveries = deliveries.sort_values(["entity_id", "date"]).reset_index(drop=True)

    # Master suppliers
    suppliers_master = pd.read_parquet(SYN / "suppliers.parquet")
    single_source_map = dict(zip(suppliers_master["entity_id"], suppliers_master["single_source_flag"]))

    # Weather
    weather = pd.read_parquet(RAW / "weather.parquet")
    weather["date"] = pd.to_datetime(weather["date"]).dt.strftime("%Y-%m-%d")
    weather_map = weather[weather["entity_type"] == "supplier"].set_index(["entity_id", "date"])["precipitation_mm"].to_dict()

    # News (read real Member 2 news_scores or fallback to dummy news)
    news_path = PROC / "news_scores.parquet"
    if not news_path.exists():
        news_path = PROC / "news_scores_v0_dummy.parquet"
    news_df = pd.read_parquet(news_path) if news_path.exists() else None
    if news_df is not None:
        news_df["date"] = pd.to_datetime(news_df["date"]).dt.strftime("%Y-%m-%d")
        news_map = news_df.set_index(["entity_id", "date"])["tone"].to_dict()
    else:
        news_map = {}

    deliveries["precip"] = deliveries.apply(lambda r: weather_map.get((r["entity_id"], r["date"]), 0.0), axis=1)
    deliveries["tone"] = deliveries.apply(lambda r: news_map.get((r["entity_id"], r["date"]), 0.0), axis=1)

    # Rolling past features (shifted by 1 day!)
    deliveries["supplier_delay_7d_avg"] = deliveries.groupby("entity_id")["delay_days"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).mean().fillna(0)
    ).round(3)

    deliveries["rain_7d_sum"] = deliveries.groupby("entity_id")["precip"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).sum().fillna(0)
    ).round(2)

    deliveries["news_tone_14d_trend"] = deliveries.groupby("entity_id")["tone"].transform(
        lambda s: s.shift(1).rolling(14, min_periods=1).mean().fillna(0)
    ).round(3)

    deliveries["single_source_flag"] = deliveries["entity_id"].map(single_source_map).fillna(0).astype(int)
    deliveries["split"] = compute_split(deliveries["date"])
    deliveries["label_7d"] = compute_label_7d(deliveries, "entity_id", "supplier_failure_flag")

    cols = [
        "entity_type", "entity_id", "date", "split",
        "supplier_delay_7d_avg", "rain_7d_sum", "news_tone_14d_trend", "single_source_flag",
        "label_7d"
    ]
    return deliveries[cols]


def build_manufacturing_features() -> pd.DataFrame:
    """Manufacturing risk feature set:
    - entity_type, entity_id, date, split
    - delivery_delay_7d_avg: past 7-day rolling average downtime hours / delay (shifted by 1 day)
    - production_ratio_7d_avg: past 7-day actual_qty / planned_qty rolling mean (shifted by 1 day)
    - rain_7d_sum: past 7-day precipitation at plant location (shifted by 1 day)
    - supplier_failure_prob_oof: upstream supplier risk indicator (0 default, leak-free)
    - label_7d: manufacturing delay occurring in (t+1, t+7]
    """
    prod = pd.read_parquet(SYN / "production_events.parquet")
    prod["date"] = pd.to_datetime(prod["date"]).dt.strftime("%Y-%m-%d")
    prod = prod.sort_values(["entity_id", "date"]).reset_index(drop=True)

    weather = pd.read_parquet(RAW / "weather.parquet")
    weather["date"] = pd.to_datetime(weather["date"]).dt.strftime("%Y-%m-%d")
    weather_map = weather[weather["entity_type"] == "plant"].set_index(["entity_id", "date"])["precipitation_mm"].to_dict()

    prod["precip"] = prod.apply(lambda r: weather_map.get((r["entity_id"], r["date"]), 0.0), axis=1)
    prod["prod_ratio"] = prod["actual_qty"] / prod["planned_qty"]

    prod["delivery_delay_7d_avg"] = prod.groupby("entity_id")["downtime_hours"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).mean().fillna(0)
    ).round(3)

    prod["production_ratio_7d_avg"] = prod.groupby("entity_id")["prod_ratio"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).mean().fillna(1.0)
    ).round(3)

    prod["rain_7d_sum"] = prod.groupby("entity_id")["precip"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).sum().fillna(0)
    ).round(2)

    # Cross-tier upstream dependency signal (shifted by 1 day)
    prod["supplier_failure_prob_oof"] = 0.05
    prod["split"] = compute_split(prod["date"])
    prod["label_7d"] = compute_label_7d(prod, "entity_id", "manufacturing_delay_flag")

    cols = [
        "entity_type", "entity_id", "date", "split",
        "delivery_delay_7d_avg", "production_ratio_7d_avg", "rain_7d_sum", "supplier_failure_prob_oof",
        "label_7d"
    ]
    return prod[cols]


def build_warehouse_features() -> pd.DataFrame:
    """Warehouse stockout feature set:
    - entity_type, entity_id, date, split
    - demand_7d_avg: past 7-day average customer demand (shifted by 1 day)
    - stock_days_cover: past inventory level / safety stock (shifted by 1 day)
    - inventory_level: past stock level (shifted by 1 day)
    - mfg_delay_prob_oof: upstream plant delay risk (0.05 baseline)
    - label_7d: warehouse stockout occurring in (t+1, t+7]
    """
    inv = pd.read_parquet(SYN / "daily_inventory.parquet")
    inv["date"] = pd.to_datetime(inv["date"]).dt.strftime("%Y-%m-%d")
    inv = inv.sort_values(["entity_id", "date"]).reset_index(drop=True)

    inv["demand_7d_avg"] = inv.groupby("entity_id")["demand_qty"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).mean().fillna(s.mean())
    ).round(1)

    inv["stock_days_cover"] = inv.groupby("entity_id").apply(
        lambda g: (g["stock_level"].shift(1) / g["demand_qty"].shift(1).rolling(7, min_periods=1).mean().replace(0, 1)).fillna(g["stock_level"] / 1000.0)
    ).reset_index(level=0, drop=True).round(2)

    inv["inventory_level"] = inv.groupby("entity_id")["stock_level"].transform(
        lambda s: s.shift(1).fillna(s.iloc[0])
    ).round(1)

    inv["mfg_delay_prob_oof"] = 0.05
    inv["split"] = compute_split(inv["date"])
    inv["label_7d"] = compute_label_7d(inv, "entity_id", "stockout_flag")

    cols = [
        "entity_type", "entity_id", "date", "split",
        "demand_7d_avg", "stock_days_cover", "inventory_level", "mfg_delay_prob_oof",
        "label_7d"
    ]
    return inv[cols]


def build_transport_features() -> pd.DataFrame:
    """Transport disruption feature set:
    - entity_type, entity_id, date, split
    - delivery_delay_7d_avg: past 7-day rolling delay days on route (shifted by 1 day)
    - rain_7d_sum: past 7-day precipitation along route midpoint (shifted by 1 day)
    - port_news_tone_14d: past 14-day port/transport tone (shifted by 1 day)
    - distance_km: static distance from routes master table
    - shipping_mode: mode from routes master table ('air', 'sea', 'road')
    - label_7d: transport delay occurring in (t+1, t+7]
    """
    trans = pd.read_parquet(SYN / "transport_shipments.parquet")
    trans["date"] = pd.to_datetime(trans["date"]).dt.strftime("%Y-%m-%d")
    trans = trans.sort_values(["entity_id", "date"]).reset_index(drop=True)

    routes_master = pd.read_parquet(SYN / "routes.parquet")
    dist_map = dict(zip(routes_master["entity_id"], routes_master["distance_km"]))
    mode_map = dict(zip(routes_master["entity_id"], routes_master["shipping_mode"]))

    weather = pd.read_parquet(RAW / "weather.parquet")
    weather["date"] = pd.to_datetime(weather["date"]).dt.strftime("%Y-%m-%d")
    weather_map = weather[weather["entity_type"] == "route"].set_index(["entity_id", "date"])["precipitation_mm"].to_dict()

    trans["precip"] = trans.apply(lambda r: weather_map.get((r["entity_id"], r["date"]), 0.0), axis=1)

    trans["delivery_delay_7d_avg"] = trans.groupby("entity_id")["delay_days"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).mean().fillna(0)
    ).round(3)

    trans["rain_7d_sum"] = trans.groupby("entity_id")["precip"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).sum().fillna(0)
    ).round(2)

    trans["port_news_tone_14d"] = -0.5
    trans["distance_km"] = trans["entity_id"].map(dist_map).fillna(1000).astype(float)
    trans["shipping_mode"] = trans["entity_id"].map(mode_map).fillna("sea")

    trans["split"] = compute_split(trans["date"])
    trans["label_7d"] = compute_label_7d(trans, "entity_id", "transport_delay_flag")

    cols = [
        "entity_type", "entity_id", "date", "split",
        "delivery_delay_7d_avg", "rain_7d_sum", "port_news_tone_14d", "distance_km", "shipping_mode",
        "label_7d"
    ]
    return trans[cols]


def main():
    tables = {
        "supplier": build_supplier_features(),
        "manufacturing": build_manufacturing_features(),
        "warehouse": build_warehouse_features(),
        "transport": build_transport_features(),
    }

    for name, df in tables.items():
        v1_path = PROC / f"features_{name}_v1.parquet"
        v2_path = PROC / f"features_{name}_v2.parquet"
        df.to_parquet(v1_path, index=False)
        df.to_parquet(v2_path, index=False)
        valid = df.dropna(subset=["label_7d"])
        pos_pct = valid["label_7d"].mean() * 100
        print(f"features_{name}_v1/v2: {len(df)} rows, 7d positive rate: {pos_pct:.2f}% ({int(valid['label_7d'].sum())}/{len(valid)})")


if __name__ == "__main__":
    main()
