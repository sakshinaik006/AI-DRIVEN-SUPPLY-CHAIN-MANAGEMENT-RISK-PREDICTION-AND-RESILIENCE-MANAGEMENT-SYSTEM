from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[2]

csv_path = (
    root
    / "data"
    / "raw"
    / "DataCosupplychaindataset"
    / "DataCoSupplyChainDataset.csv"
)

output_path = root / "data" / "processed" / "dataco_electronics.parquet"

df = pd.read_csv(csv_path, encoding="latin1", low_memory=False)

order_col = "order date (DateOrders)"
shipping_col = "shipping date (DateOrders)"

df[order_col] = pd.to_datetime(df[order_col], errors="coerce")
df[shipping_col] = pd.to_datetime(df[shipping_col], errors="coerce")

df = df[df["Category Name"].eq("Electronics")].copy()
df = df.dropna(subset=[order_col])

source_start = df[order_col].min().normalize()
offset = pd.Timestamp("2025-04-01") - source_start

df["order_date_original"] = df[order_col]
df["shipping_date_original"] = df[shipping_col]

df[order_col] = df[order_col] + offset
df[shipping_col] = df[shipping_col] + offset

window_start = pd.Timestamp("2025-04-01")
window_end = pd.Timestamp("2025-10-31 23:59:59")

before_window_filter = len(df)
df = df[df[order_col].between(window_start, window_end)].copy()
removed = before_window_filter - len(df)

output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(output_path, index=False)

print(f"Electronics rows kept: {len(df):,}")
print(f"Rows outside shifted order-date window removed: {removed:,}")
print(f"Shifted order-date range: {df[order_col].min()} to {df[order_col].max()}")
print(f"Saved to: {output_path}")