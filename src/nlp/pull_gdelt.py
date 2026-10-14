"""GDELT News Retrieval & Realistic Supply Chain News Generator.

Extracts supply-chain headlines (shortages, strikes, floods, shutdowns,
port congestion, accidents, power cuts) for 1 Apr 2025 - 31 Oct 2025.
Saves to data/raw/gdelt_headlines.parquet with columns:
  date, title, country, city, theme, tone

Includes automated fallback to synthetic supply-chain news when
GDELT DOC 2.0 API does not cover historical dates.
"""
from pathlib import Path
import json
import logging
import numpy as np
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
SYN_DIR = ROOT / "data" / "synthetic"
RAW_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "2025-04-01"
END_DATE = "2025-10-31"

THEMES = [
    "shortage",
    "strike",
    "flood",
    "shutdown",
    "port_congestion",
    "accident",
    "power_cut",
]

# Cities and countries from master network tables
DEFAULT_LOCATIONS = [
    ("Hsinchu", "Taiwan", "semiconductor fabs"),
    ("Shenzhen", "China", "electronics assembly and ports"),
    ("Seoul", "South Korea", "display manufacturing hubs"),
    ("Icheon", "South Korea", "memory silicon foundries"),
    ("Dongguan", "China", "battery cell production plants"),
    ("Ningbo", "China", "container terminal and battery facilities"),
    ("Suzhou", "China", "precision optics manufacturing"),
    ("Pune", "India", "component stamping and assembly"),
    ("Chennai", "India", "smartphone final assembly plants"),
    ("Noida", "India", "handset manufacturing complex"),
    ("Bac Ninh", "Vietnam", "electronics assembly industrial park"),
    ("Mumbai", "India", "commercial container port and logistics"),
    ("Rotterdam", "Netherlands", "deepwater port terminals"),
    ("Los Angeles", "United States", "West Coast container gateways"),
    ("Singapore", "Singapore", "transshipment logistics hub"),
    ("Dubai", "United Arab Emirates", "air cargo and distribution center"),
]

HEADLINE_TEMPLATES = {
    "shortage": [
        "Critical wafer and component shortage disrupts technology supply chain near {city}",
        "Severe raw material and lithium shortage impacts manufacturers across {country}",
        "Component shortages force assembly delays at high-volume plants in {city}",
        "Display and memory supply shortages hit electronics production facilities in {city}",
    ],
    "strike": [
        "Labour union strike halts operations across industrial facilities in {city}",
        "Truckers strike and logistics protest disrupt freight corridors in {country}",
        "Dockworkers announce indefinite strike impacting container terminals near {city}",
        "Factory workers stage walkout over wage disputes in industrial {city}",
    ],
    "flood": [
        "Heavy monsoon rains and urban flooding stall supply routes around {city}",
        "Typhoon-induced flash floods submerge industrial zones near {city}",
        "Severe flood warnings trigger emergency closures across {country} transport hubs",
        "Rising river levels and flood damage disrupt freight transit through {city}",
    ],
    "shutdown": [
        "Emergency regulatory shutdown ordered for key manufacturing plant in {city}",
        "Unplanned maintenance shutdown halts production line in {city}",
        "Environmental compliance inspection forces temporary factory shutdown in {city}",
        "Industrial estate shutdown disrupts regional component shipping in {country}",
    ],
    "port_congestion": [
        "Massive container vessel backlog causes acute port congestion near {city}",
        "Customs clearance bottleneck and berth delays stall port throughput in {city}",
        "Vessel turnaround times spike amid worsening terminal congestion in {city}",
        "Supply chain paralysis reported as container congestion peaks across {country} ports",
    ],
    "accident": [
        "Industrial fire and chemical accident damages component facility in {city}",
        "Highway tanker collision and freight train derailment blocks main corridor near {city}",
        "Substation explosion triggers industrial park disruption in {city}",
        "Major infrastructure accident damages logistics warehouse complex in {city}",
    ],
    "power_cut": [
        "Severe power grid blackout brings industrial manufacturing to standstill in {city}",
        "Rolling power cuts implemented across energy-intensive industrial parks in {country}",
        "Transformer failure causes extended power cut at major production cluster in {city}",
        "Extreme heat wave triggers emergency electrical load shedding throughout {city}",
    ],
}

NEUTRAL_TEMPLATES = [
    "Logistics operators in {city} report steady cargo volumes and stable schedules",
    "Supply chain infrastructure investments underway across {country} industrial zones",
    "Regional trade conference in {city} highlights supply chain resilience initiatives",
    "Routine customs automation upgrades deployed at freight hubs in {city}",
    "Manufacturing output expands steadily at modern industrial parks in {city}",
]


def load_master_locations():
    """Load locations from synthetic tables if available."""
    locations = []
    for filename in ("suppliers.csv", "plants.csv", "warehouses.csv"):
        filepath = SYN_DIR / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            for _, r in df.iterrows():
                locations.append((r["city"], r["country"], r.get("name", "")))
    if locations:
        # Deduplicate by (city, country)
        unique = {}
        for city, country, desc in locations:
            if (city, country) not in unique:
                unique[(city, country)] = desc
        return [(c, cnt, d) for (c, cnt), d in unique.items()]
    return DEFAULT_LOCATIONS


def query_gdelt_api(query: str, start_dt: str, end_dt: str, max_records: int = 250):
    """Query GDELT DOC 2.0 API (returns empty or error if dates are outside rolling window)."""
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": max_records,
        "startdatetime": start_dt.replace("-", "") + "000000",
        "enddatetime": end_dt.replace("-", "") + "235959",
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            articles = data.get("articles", [])
            return articles
    except Exception as e:
        logger.warning(f"GDELT DOC 2.0 API call failed or timed out: {e}")
    return []


def generate_synthetic_news(seed: int = 42) -> pd.DataFrame:
    """Generate reproducible supply-chain headlines for the project dates and nodes."""
    rng = np.random.default_rng(seed)
    locations = load_master_locations()
    dates = pd.date_range(START_DATE, END_DATE, freq="D")

    records = []

    # Inject correlated events aligned with the supply chain network
    for dt in dates:
        dt_str = dt.strftime("%Y-%m-%d")
        # 1 to 4 news events per day
        n_events = int(rng.integers(1, 5))
        for _ in range(n_events):
            is_disruption = rng.random() < 0.65
            loc = locations[rng.integers(0, len(locations))]
            city, country = loc[0], loc[1]

            if is_disruption:
                theme = str(rng.choice(THEMES))
                template = str(rng.choice(HEADLINE_TEMPLATES[theme]))
                title = template.format(city=city, country=country)
                # Disruption tone: negative, e.g. -1.5 to -8.0
                tone = round(float(rng.normal(-4.5, 1.8)), 2)
                tone = min(-0.5, tone)
            else:
                theme = "general_business"
                template = str(rng.choice(NEUTRAL_TEMPLATES))
                title = template.format(city=city, country=country)
                # Neutral / slightly positive tone
                tone = round(float(rng.normal(1.2, 1.0)), 2)

            records.append({
                "date": dt_str,
                "title": title,
                "country": country,
                "city": city,
                "theme": theme,
                "tone": tone,
            })

    df = pd.DataFrame(records)
    # Sort chronologically
    df = df.sort_values(["date", "country", "city"]).reset_index(drop=True)
    return df


def pull_and_save_headlines(force_synthetic: bool = False) -> pd.DataFrame:
    """Pull GDELT headlines or build the fallback dataset and save to parquet."""
    headlines = []
    if not force_synthetic:
        logger.info("Checking GDELT DOC 2.0 API for Apr-Oct 2025 window...")
        articles = query_gdelt_api("supply chain shortage strike", START_DATE, END_DATE)
        if articles:
            logger.info(f"Retrieved {len(articles)} articles from GDELT API.")
            for a in articles:
                headlines.append({
                    "date": a.get("seendate", "")[:8],
                    "title": a.get("title", ""),
                    "country": a.get("sourcecountry", "Unknown"),
                    "city": "",
                    "theme": "shortage",
                    "tone": float(a.get("tone", 0.0)),
                })

    if not headlines:
        logger.info("GDELT API returned no records for 2025 window. Using synthetic news table fallback per project specifications.")
        df = generate_synthetic_news(seed=42)
    else:
        df = pd.DataFrame(headlines)

    out_file = RAW_DIR / "gdelt_headlines.parquet"
    df.to_parquet(out_file, index=False)
    logger.info(f"Saved {len(df)} headlines to {out_file}")
    logger.info(f"Themes distribution:\n{df['theme'].value_counts()}")
    logger.info(f"Tone summary: mean={df['tone'].mean():.2f}, min={df['tone'].min():.2f}, max={df['tone'].max():.2f}")
    return df


if __name__ == "__main__":
    pull_and_save_headlines()
