"""Build the synthetic master tables (suppliers, plants, warehouses, products,
components, product_component_map, routes).

Run from the repo root:  python -m src.data.make_master

Everything is hand-defined and fully deterministic (no randomness), so every
member gets identical tables. Entity ids match docs/interface.md:
SUP001.., PLT001.., WH001.., RT001..

Outputs go to data/synthetic/. Each table is written as CSV (small, readable)
and also as parquet when pyarrow is installed.

SYNTHETIC: these tables are invented for the prototype. City names and
coordinates are real places so Open-Meteo weather and news matching work, but
the companies and their roles are made up (see docs/disclosure.md).
"""
from math import asin, cos, radians, sin, sqrt
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "synthetic"

# ---------------------------------------------------------------- components
COMPONENTS = [
    # component_id, name, type, criticality (1-3)
    ("C001", "Application processor (SoC)", "chip", 3),
    ("C002", "OLED display panel", "display", 3),
    ("C003", "Memory (DRAM + flash)", "memory", 3),
    ("C004", "Battery cell", "battery", 2),
    ("C005", "Camera module", "camera", 2),
    ("C006", "Housing and PCB", "assembly", 1),
]

# ----------------------------------------------------------------- suppliers
# supplier_id, name, country, city, lat, lon, tier, base_lead_time_days, components
SUPPLIERS = [
    ("SUP001", "Hsinchu Silicon Works", "Taiwan", "Hsinchu", 24.8138, 120.9675, 1, 21, ["C001"]),
    ("SUP002", "Seoul Display Systems", "South Korea", "Seoul", 37.5665, 126.9780, 1, 18, ["C002"]),
    ("SUP003", "Icheon Memory Corp", "South Korea", "Icheon", 37.2792, 127.4425, 1, 16, ["C003"]),
    ("SUP004", "Dongguan Power Cells", "China", "Dongguan", 23.0207, 113.7518, 1, 10, ["C004"]),
    ("SUP005", "Ningbo Battery Group", "China", "Ningbo", 29.8683, 121.5440, 1, 12, ["C004", "C006"]),
    ("SUP006", "Suzhou Optics", "China", "Suzhou", 31.2989, 120.5853, 1, 14, ["C005"]),
    ("SUP007", "Shenzhen Display Tech", "China", "Shenzhen", 22.5431, 114.0579, 1, 12, ["C002", "C005"]),
    ("SUP008", "Pune Assembly Parts", "India", "Pune", 18.5204, 73.8567, 1, 7, ["C006"]),
]

# -------------------------------------------------------------------- plants
# plant_id, name, country, city, lat, lon, capacity_units_per_day
PLANTS = [
    ("PLT001", "Chennai Phone Plant", "India", "Chennai", 13.0827, 80.2707, 12000),
    ("PLT002", "Noida Phone Plant", "India", "Noida", 28.5355, 77.3910, 10000),
    ("PLT003", "Bac Ninh Phone Plant", "Vietnam", "Bac Ninh", 21.1861, 106.0763, 15000),
    ("PLT004", "Shenzhen Phone Plant", "China", "Shenzhen", 22.5431, 114.0579, 20000),
]

# ---------------------------------------------------------------- warehouses
# warehouse_id, name, country, city, lat, lon, safety_stock_units
WAREHOUSES = [
    ("WH001", "Mumbai Distribution Centre", "India", "Mumbai", 19.0760, 72.8777, 6000),
    ("WH002", "Rotterdam Distribution Centre", "Netherlands", "Rotterdam", 51.9244, 4.4777, 5000),
    ("WH003", "Los Angeles Distribution Centre", "United States", "Los Angeles", 34.0522, -118.2437, 7000),
    ("WH004", "Singapore Distribution Centre", "Singapore", "Singapore", 1.3521, 103.8198, 4000),
    ("WH005", "Dubai Distribution Centre", "United Arab Emirates", "Dubai", 25.2048, 55.2708, 4500),
]

# ------------------------------------------------------------------ products
# product_id, name, tier, unit_price_usd
PRODUCTS = [
    ("P001", "Phone Lite", "budget", 180),
    ("P002", "Phone Core", "mid", 320),
    ("P003", "Phone Core Plus", "mid", 410),
    ("P004", "Phone Pro", "premium", 720),
    ("P005", "Phone Max", "premium", 950),
]

# product -> {component: quantity per phone}; every phone uses one of each
# component, premium phones use a second camera module.
PRODUCT_COMPONENTS = {
    "P001": {"C001": 1, "C002": 1, "C003": 1, "C004": 1, "C005": 1, "C006": 1},
    "P002": {"C001": 1, "C002": 1, "C003": 1, "C004": 1, "C005": 1, "C006": 1},
    "P003": {"C001": 1, "C002": 1, "C003": 1, "C004": 1, "C005": 2, "C006": 1},
    "P004": {"C001": 1, "C002": 1, "C003": 1, "C004": 1, "C005": 2, "C006": 1},
    "P005": {"C001": 1, "C002": 1, "C003": 1, "C004": 1, "C005": 2, "C006": 1},
}

# ------------------------------------------------------------------- routes
# Inbound = supplier -> plant, Outbound = plant -> warehouse.
# route_id, route_type, origin_id, destination_id, shipping_mode, scheduled_days
ROUTES = [
    ("RT001", "inbound", "SUP001", "PLT004", "air", 3),
    ("RT002", "inbound", "SUP002", "PLT003", "air", 3),
    ("RT003", "inbound", "SUP003", "PLT001", "air", 5),
    ("RT004", "inbound", "SUP004", "PLT004", "road", 2),
    ("RT005", "inbound", "SUP008", "PLT001", "road", 3),
    ("RT006", "outbound", "PLT001", "WH001", "road", 3),
    ("RT007", "outbound", "PLT002", "WH005", "sea", 9),
    ("RT008", "outbound", "PLT003", "WH004", "sea", 6),
    ("RT009", "outbound", "PLT004", "WH003", "sea", 21),
    ("RT010", "outbound", "PLT004", "WH002", "sea", 28),
]


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(a))


def build() -> dict[str, pd.DataFrame]:
    components = pd.DataFrame(COMPONENTS, columns=["component_id", "component_name", "component_type", "criticality"])

    # which components are supplied by only one supplier -> single-source
    suppliers_of = {c: [] for c in components["component_id"]}
    for s in SUPPLIERS:
        for c in s[8]:
            suppliers_of[c].append(s[0])

    rows = []
    for sid, name, country, city, lat, lon, tier, lead, comps in SUPPLIERS:
        rows.append({
            "entity_type": "supplier", "entity_id": sid, "name": name,
            "country": country, "city": city, "latitude": lat, "longitude": lon,
            "tier": tier, "base_lead_time_days": lead,
            "component_ids": ";".join(comps),
            "single_source_flag": int(any(len(suppliers_of[c]) == 1 for c in comps)),
        })
    suppliers = pd.DataFrame(rows)

    plants = pd.DataFrame(
        [{"entity_type": "plant", "entity_id": i, "name": n, "country": co, "city": ci,
          "latitude": la, "longitude": lo, "capacity_units_per_day": cap}
         for i, n, co, ci, la, lo, cap in PLANTS])

    warehouses = pd.DataFrame(
        [{"entity_type": "warehouse", "entity_id": i, "name": n, "country": co, "city": ci,
          "latitude": la, "longitude": lo, "safety_stock_units": ss}
         for i, n, co, ci, la, lo, ss in WAREHOUSES])

    products = pd.DataFrame(PRODUCTS, columns=["product_id", "product_name", "tier", "unit_price_usd"])

    pcm = pd.DataFrame(
        [{"product_id": p, "component_id": c, "quantity_per_unit": q}
         for p, comps in PRODUCT_COMPONENTS.items() for c, q in comps.items()])

    coords = {}
    for df in (suppliers, plants, warehouses):
        for r in df.itertuples():
            coords[r.entity_id] = (r.latitude, r.longitude, r.country, r.city)

    routes = []
    for rid, rtype, o, d, mode, days in ROUTES:
        (la1, lo1, c1, ci1), (la2, lo2, c2, ci2) = coords[o], coords[d]
        routes.append({
            "entity_type": "route", "entity_id": rid, "route_type": rtype,
            "origin_id": o, "destination_id": d,
            "origin_country": c1, "origin_city": ci1,
            "destination_country": c2, "destination_city": ci2,
            "shipping_mode": mode, "scheduled_days": days,
            "distance_km": round(haversine_km(la1, lo1, la2, lo2), 0),
            # route-level weather uses the midpoint of the lane
            "latitude": round((la1 + la2) / 2, 4), "longitude": round((lo1 + lo2) / 2, 4),
        })
    routes = pd.DataFrame(routes)

    return {"suppliers": suppliers, "plants": plants, "warehouses": warehouses,
            "products": products, "components": components,
            "product_component_map": pcm, "routes": routes}


def validate(t: dict[str, pd.DataFrame]) -> None:
    """Fail loudly if a table breaks the handover 2 check or a link is broken."""
    for name in ("suppliers", "plants", "warehouses", "routes"):
        df = t[name]
        assert df["entity_id"].is_unique, f"{name}: duplicate entity_id"
        assert df[["entity_type", "entity_id", "latitude", "longitude"]].notna().all().all(), f"{name}: missing key/coords"
    for name in ("suppliers", "plants", "warehouses"):
        df = t[name]
        assert df[["country", "city"]].notna().all().all(), f"{name}: missing country/city"
        assert df["latitude"].between(-90, 90).all() and df["longitude"].between(-180, 180).all(), f"{name}: bad coords"
    comp_ids = set(t["components"]["component_id"])
    supplied = {c for s in t["suppliers"]["component_ids"] for c in s.split(";")}
    assert supplied == comp_ids, f"components with no supplier: {comp_ids - supplied}"
    pcm = t["product_component_map"]
    assert set(pcm["product_id"]) == set(t["products"]["product_id"]), "product with no components"
    assert set(pcm["component_id"]) <= comp_ids, "map uses unknown component"
    known = set(t["suppliers"]["entity_id"]) | set(t["plants"]["entity_id"]) | set(t["warehouses"]["entity_id"])
    r = t["routes"]
    assert set(r["origin_id"]) <= known and set(r["destination_id"]) <= known, "route endpoint missing"
    assert set(t["plants"]["entity_id"]) <= set(r["origin_id"]) | set(r["destination_id"]), "plant with no route"
    assert set(t["warehouses"]["entity_id"]) <= set(r["destination_id"]), "warehouse with no inbound route"


def save(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / f"{name}.csv", index=False)
    try:
        df.to_parquet(OUT / f"{name}.parquet", index=False)
    except ImportError:
        pass  # pyarrow not installed: CSV only


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tables = build()
    validate(tables)
    for name, df in tables.items():
        save(df, name)
        print(f"{name}: {len(df)} rows -> data/synthetic/{name}.csv")


if __name__ == "__main__":
    main()
