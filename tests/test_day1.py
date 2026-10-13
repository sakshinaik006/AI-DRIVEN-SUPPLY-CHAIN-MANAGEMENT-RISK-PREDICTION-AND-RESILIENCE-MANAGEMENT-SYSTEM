"""Unit and integration tests for Member 1 deliverables:
- Day 1: Master tables, coordinates, cities, weather coverage, calibrated positive label rates.
- DataCo processing: Electronics subset, date shifting into 2025-04-01 to 2025-10-31.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DIR = ROOT / "data" / "synthetic"
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def test_master_tables_handover2_compliance():
    """Handover 2 check: Country, city, and entity_id are present for every row."""
    for table_name in ("suppliers", "plants", "warehouses"):
        parquet_path = SYNTHETIC_DIR / f"{table_name}.parquet"
        assert parquet_path.exists(), f"Missing {parquet_path}"
        df = pd.read_parquet(parquet_path)
        assert "entity_id" in df.columns, f"entity_id missing from {table_name}"
        assert "country" in df.columns, f"country missing from {table_name}"
        assert "city" in df.columns, f"city missing from {table_name}"
        assert df["entity_id"].notna().all(), f"Null entity_id in {table_name}"
        assert df["country"].notna().all(), f"Null country in {table_name}"
        assert df["city"].notna().all(), f"Null city in {table_name}"
        assert df["entity_id"].is_unique, f"Duplicate entity_id in {table_name}"


def test_routes_table_integrity():
    """Routes must link valid origins and destinations with coordinates and scheduled days."""
    routes_path = SYNTHETIC_DIR / "routes.parquet"
    assert routes_path.exists(), "Missing routes.parquet"
    df = pd.read_parquet(routes_path)
    assert len(df) == 10, "Expected exactly 10 routes"
    assert set(df["shipping_mode"]) <= {"air", "sea", "road"}
    assert (df["scheduled_days"] > 0).all()
    assert df["latitude"].between(-90, 90).all()
    assert df["longitude"].between(-180, 180).all()


def test_weather_coverage_handover3():
    """Handover 3 check: weather covers 1 Apr to 31 Oct 2025 for all entities."""
    weather_path = RAW_DIR / "weather.parquet"
    assert weather_path.exists(), "Missing weather.parquet"
    df = pd.read_parquet(weather_path)
    assert len(df) == 5778, f"Expected 5,778 rows (27 locations * 214 days), got {len(df)}"
    assert df["date"].min() == "2025-04-01"
    assert df["date"].max() == "2025-10-31"
    assert df[["entity_id", "precipitation_mm", "max_wind_speed_kmh", "extreme_weather_flag"]].notna().all().all()


def test_dataco_electronics_dates_and_filter():
    """DataCo electronics dataset is filtered and shifted into the active time window."""
    dataco_path = PROCESSED_DIR / "dataco_electronics.parquet"
    assert dataco_path.exists(), "Missing dataco_electronics.parquet"
    df = pd.read_parquet(dataco_path)
    assert len(df) > 0, "DataCo electronics table is empty"
    order_col = "order date (DateOrders)"
    assert order_col in df.columns, f"Missing {order_col}"
    order_dates = pd.to_datetime(df[order_col])
    assert order_dates.min() >= pd.Timestamp("2025-04-01")
    assert order_dates.max() <= pd.Timestamp("2025-10-31 23:59:59")


def test_calibrated_positive_label_rates():
    """Check that each risk label achieves balanced positive rate within 2.5% to 6.5%."""
    checks = [
        ("supplier_deliveries.parquet", "supplier_failure_flag"),
        ("production_events.parquet", "manufacturing_delay_flag"),
        ("daily_inventory.parquet", "stockout_flag"),
        ("transport_shipments.parquet", "transport_delay_flag"),
    ]
    for filename, flag_col in checks:
        path = SYNTHETIC_DIR / filename
        assert path.exists(), f"Missing {filename}"
        df = pd.read_parquet(path)
        records = []
        for _, g in df.groupby("entity_id"):
            fwd = pd.concat([g[flag_col].shift(-i) for i in range(1, 8)], axis=1).max(axis=1)
            records.append(fwd)
        all_fwd = pd.concat(records).dropna()
        pos_rate = all_fwd.mean()
        assert 0.025 <= pos_rate <= 0.065, f"{filename} 7d positive rate {pos_rate:.1%} out of bounds [2.5%, 6.5%]"
