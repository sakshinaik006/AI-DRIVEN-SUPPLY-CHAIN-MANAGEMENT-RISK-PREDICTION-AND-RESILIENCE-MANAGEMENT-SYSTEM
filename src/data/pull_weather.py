"""
Pull Open-Meteo daily weather for suppliers, plants, warehouses, and route midpoints.
Output: data/raw/weather.parquet
"""
from pathlib import Path
import time
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_DIR = ROOT / "data" / "synthetic"
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "2025-04-01"
END_DATE = "2025-10-31"

def create_session() -> requests.Session:
    """Create a requests session with retries for robust network calls."""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def load_locations() -> pd.DataFrame:
    locs = []
    for name in ("suppliers", "plants", "warehouses", "routes"):
        path = SYNTHETIC_DIR / f"{name}.parquet"
        if not path.exists():
            path = SYNTHETIC_DIR / f"{name}.csv"
        df = pd.read_csv(path) if path.suffix == ".csv" else pd.read_parquet(path)
        
        for r in df.itertuples():
            locs.append({
                "entity_id": r.entity_id,
                "entity_type": r.entity_type,
                "latitude": r.latitude,
                "longitude": r.longitude
            })
    return pd.DataFrame(locs)

def fetch_weather() -> None:
    locations = load_locations()
    all_records = []
    session = create_session()
    
    print(f"Fetching weather for {len(locations)} locations from {START_DATE} to {END_DATE}...")
    
    for idx_loc, r in enumerate(locations.itertuples(), start=1):
        url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={r.latitude}&longitude={r.longitude}&"
            f"start_date={START_DATE}&end_date={END_DATE}&"
            f"daily=precipitation_sum,wind_speed_10m_max,weather_code&timezone=UTC"
        )
        try:
            res = session.get(url, timeout=30).json()
            daily = res.get("daily", {})
            
            if "time" not in daily:
                print(f"[{idx_loc}/{len(locations)}] Warning: No weather data returned for {r.entity_id}")
                continue
                
            for idx, date_str in enumerate(daily["time"]):
                rain = daily["precipitation_sum"][idx] or 0.0
                wind = daily["wind_speed_10m_max"][idx] or 0.0
                
                all_records.append({
                    "entity_id": r.entity_id,
                    "entity_type": r.entity_type,
                    "date": date_str,
                    "precipitation_mm": rain,
                    "max_wind_speed_kmh": wind,
                    "extreme_weather_flag": int(rain > 50.0 or wind > 60.0)
                })
            print(f"[{idx_loc}/{len(locations)}] Pulled weather for {r.entity_id}")
        except Exception as e:
            print(f"[{idx_loc}/{len(locations)}] Failed to fetch {r.entity_id}: {e}")
            
        time.sleep(0.5)  # Pause to avoid connection drops and rate limits
            
    df_weather = pd.DataFrame(all_records)
    out_path = RAW_DIR / "weather.parquet"
    df_weather.to_parquet(out_path, index=False)
    print(f"\nSaved weather data ({len(df_weather)} rows) to {out_path}")

if __name__ == "__main__":
    fetch_weather()