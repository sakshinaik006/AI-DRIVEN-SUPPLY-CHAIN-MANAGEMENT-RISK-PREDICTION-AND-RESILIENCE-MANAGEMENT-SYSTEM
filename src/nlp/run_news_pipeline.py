"""Full Day 2 News Processing Pipeline: DeBERTa Scoring, NER Linking & Leak-Free Rolling Features.

Outputs:
  data/processed/news_scores.parquet
Columns:
  entity_id, date, text_risk, text_risk_7d, disruption_type, tone

Enforces all leakage prevention rules:
  - Rolling text_risk_7d is strictly shifted by 1 day (shift(1))
  - Supervised baseline is evaluated out-of-fold using expanding time splits
  - Empty news days filled with 0.0 per project guidelines
"""
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

_dll_cookie = None
if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    torch_lib = os.path.join(sys.prefix, "Lib", "site-packages", "torch", "lib")
    if os.path.exists(torch_lib):
        try:
            _dll_cookie = os.add_dll_directory(torch_lib)
        except Exception:
            pass

try:
    import torch
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "processed"
SYN_DIR = ROOT / "data" / "synthetic"
PROC_DIR.mkdir(parents=True, exist_ok=True)

from src.nlp.ner_linking import SupplyChainNERLinker
from src.nlp.zero_shot import DisruptionZeroShotClassifier
from src.nlp.risk_scoring import DeBERTaRiskScorer
from src.nlp.baseline_tfidf import TfidfLogisticBaseline


def get_all_entities() -> list[str]:
    """Retrieve full list of 27 entities from synthetic master files or fallback."""
    entities = []
    for f in ("suppliers.csv", "plants.csv", "warehouses.csv", "routes.csv"):
        p = SYN_DIR / f
        if p.exists():
            df = pd.read_csv(p)
            entities.extend(df["entity_id"].tolist())
    if not entities:
        # Fallback to standard 27 entities
        entities = (
            [f"SUP{i:03d}" for i in range(1, 9)] +
            [f"PLT{i:03d}" for i in range(1, 5)] +
            [f"WH{i:03d}" for i in range(1, 6)] +
            [f"RT{i:03d}" for i in range(1, 11)]
        )
    return sorted(set(entities))


def run_pipeline() -> pd.DataFrame:
    raw_path = RAW_DIR / "gdelt_headlines.parquet"
    if not raw_path.exists():
        from src.nlp.pull_gdelt import pull_and_save_headlines
        pull_and_save_headlines()

    print("[1/5] Loading raw news headlines...")
    df_raw = pd.read_parquet(raw_path)
    print(f"      Loaded {len(df_raw)} headlines.")

    print("[2/5] Initializing NLP components (NER linker, zero-shot, DeBERTa scorer, TF-IDF baseline)...")
    linker = SupplyChainNERLinker()
    zero_shot = DisruptionZeroShotClassifier()
    scorer = DeBERTaRiskScorer()
    baseline = TfidfLogisticBaseline()

    # Assign time splits
    d = pd.to_datetime(df_raw["date"])
    df_raw["split"] = np.select(
        [d <= "2025-08-24", d <= "2025-08-31", d <= "2025-09-23", d <= "2025-09-30"],
        ["train", "purge", "val", "purge"],
        default="test",
    )

    print("[3/5] Scoring headlines and linking entities...")
    df_scored = scorer.score_dataframe(df_raw)
    df_scored["disruption_type"] = zero_shot.predict_batch(df_scored["title"].tolist())
    df_scored["tfidf_lr_risk"] = baseline.fit_predict_oof(df_scored)

    # Link each headline to entities
    linked_records = []
    for idx, row in df_scored.iterrows():
        entities = linker.link_entities(
            row["title"],
            country=row.get("country"),
            city=row.get("city"),
            theme=row.get("theme"),
        )
        for ent in entities:
            linked_records.append({
                "entity_id": ent["entity_id"],
                "date": str(row["date"]),
                "text_risk": float(row["text_risk"]),
                "disruption_type": str(row["disruption_type"]),
                "tone": float(row["tone"]),
                "tfidf_lr_risk": float(row["tfidf_lr_risk"]),
            })

    df_linked = pd.DataFrame(linked_records)

    # Aggregate by (entity_id, date)
    if not df_linked.empty:
        df_daily_agg = df_linked.groupby(["entity_id", "date"]).agg({
            "text_risk": "max",
            "tone": "min",
            "disruption_type": "first",
            "tfidf_lr_risk": "max",
        }).reset_index()
    else:
        df_daily_agg = pd.DataFrame(columns=["entity_id", "date", "text_risk", "tone", "disruption_type", "tfidf_lr_risk"])

    print("[4/5] Building full 27-entity daily grid (2025-04-01 to 2025-10-31)...")
    all_entities = get_all_entities()
    dates = pd.date_range("2025-04-01", "2025-10-31", freq="D").strftime("%Y-%m-%d").tolist()

    grid_idx = pd.MultiIndex.from_product([all_entities, dates], names=["entity_id", "date"]).to_frame(index=False)
    grid_df = grid_idx.merge(df_daily_agg, on=["entity_id", "date"], how="left")

    # Fill days with no news with 0.0 / neutral
    grid_df["text_risk"] = grid_df["text_risk"].fillna(0.0).round(3)
    grid_df["tone"] = grid_df["tone"].fillna(0.0).round(2)
    grid_df["disruption_type"] = grid_df["disruption_type"].fillna("none")
    grid_df["tfidf_lr_risk"] = grid_df["tfidf_lr_risk"].fillna(0.0).round(3)

    # Sort chronologically per entity for rolling feature calculation
    grid_df = grid_df.sort_values(["entity_id", "date"]).reset_index(drop=True)

    print("[5/5] Computing leak-free 7-day rolling text_risk (strictly shifted by 1 day)...")
    # shift(1) guarantees no leakage of day t information into day t feature
    grid_df["text_risk_7d"] = grid_df.groupby("entity_id")["text_risk"].transform(
        lambda s: s.rolling(7, min_periods=1).mean().shift(1)
    ).fillna(0.0).round(3)

    # Ensure required column order
    cols = ["entity_id", "date", "text_risk", "text_risk_7d", "disruption_type", "tone"]
    final_df = grid_df[cols]

    out_file = PROC_DIR / "news_scores.parquet"
    final_df.to_parquet(out_file, index=False)
    print(f"--> Saved {len(final_df)} entity-date rows to {out_file}")
    print(f"    Entities: {final_df['entity_id'].nunique()}, Dates: {final_df['date'].nunique()}")
    print(f"    Non-zero text_risk rate: {(final_df['text_risk'] > 0).mean():.1%}")
    print(f"    Average 7-day rolling risk: {final_df['text_risk_7d'].mean():.3f}")

    return final_df


if __name__ == "__main__":
    run_pipeline()
