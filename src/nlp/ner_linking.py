"""NER Entity Linking Module for Supply Chain News.

Extracts locations (GPE/LOC) from headlines using spaCy NER and links them
to suppliers, manufacturing plants, warehouses, and transport routes
based on country, city, and theme using master entity tables.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

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

import pandas as pd
import spacy

ROOT = Path(__file__).resolve().parents[2]
SYN_DIR = ROOT / "data" / "synthetic"


class SupplyChainNERLinker:
    """Links headline text to supply chain entity IDs using NER and geographic indices."""

    def __init__(self, spacy_model: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(spacy_model)
        except Exception:
            # Fallback if model not found directly
            self.nlp = spacy.blank("en")
        self._load_master_tables()

    def _load_master_tables(self):
        """Build location-to-entity mapping indices from synthetic master tables."""
        self.suppliers = []
        self.plants = []
        self.warehouses = []
        self.routes = []

        sup_path = SYN_DIR / "suppliers.csv"
        if sup_path.exists():
            df_sup = pd.read_csv(sup_path)
            for _, r in df_sup.iterrows():
                self.suppliers.append({
                    "entity_id": r["entity_id"],
                    "entity_type": "supplier",
                    "city": str(r["city"]).strip().lower(),
                    "country": str(r["country"]).strip().lower(),
                })

        plt_path = SYN_DIR / "plants.csv"
        if plt_path.exists():
            df_plt = pd.read_csv(plt_path)
            for _, r in df_plt.iterrows():
                self.plants.append({
                    "entity_id": r["entity_id"],
                    "entity_type": "plant",
                    "city": str(r["city"]).strip().lower(),
                    "country": str(r["country"]).strip().lower(),
                })

        wh_path = SYN_DIR / "warehouses.csv"
        if wh_path.exists():
            df_wh = pd.read_csv(wh_path)
            for _, r in df_wh.iterrows():
                self.warehouses.append({
                    "entity_id": r["entity_id"],
                    "entity_type": "warehouse",
                    "city": str(r["city"]).strip().lower(),
                    "country": str(r["country"]).strip().lower(),
                })

        rt_path = SYN_DIR / "routes.csv"
        if rt_path.exists():
            df_rt = pd.read_csv(rt_path)
            for _, r in df_rt.iterrows():
                self.routes.append({
                    "entity_id": r["entity_id"],
                    "entity_type": "route",
                    "origin_city": str(r["origin_city"]).strip().lower(),
                    "origin_country": str(r["origin_country"]).strip().lower(),
                    "dest_city": str(r["destination_city"]).strip().lower(),
                    "dest_country": str(r["destination_country"]).strip().lower(),
                })

    def extract_locations(self, text: str) -> List[str]:
        """Extract GPE and LOC entities from text using spaCy."""
        doc = self.nlp(text)
        locs = [ent.text.strip().lower() for ent in doc.ents if ent.label_ in ("GPE", "LOC", "FAC")]
        # Also check known cities/countries directly
        text_lower = text.lower()
        all_cities = {s["city"] for s in self.suppliers} | {p["city"] for p in self.plants} | \
                     {w["city"] for w in self.warehouses}
        all_countries = {s["country"] for s in self.suppliers} | {p["country"] for p in self.plants} | \
                        {w["country"] for w in self.warehouses}
        for c in all_cities:
            if c in text_lower and c not in locs:
                locs.append(c)
        for cnt in all_countries:
            if cnt in text_lower and cnt not in locs:
                locs.append(cnt)
        return locs

    def link_entities(
        self,
        headline: str,
        country: Optional[str] = None,
        city: Optional[str] = None,
        theme: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Link a headline to matching entities (supplier, plant, warehouse, route)."""
        locs = self.extract_locations(headline)
        if city:
            locs.append(str(city).strip().lower())
        if country:
            locs.append(str(country).strip().lower())

        loc_set = set(locs)
        matches = []
        theme_str = (theme or "").lower()

        # Match suppliers (especially on shortage, material, wafer, strikes)
        for s in self.suppliers:
            if s["city"] in loc_set or s["country"] in loc_set:
                matches.append({"entity_id": s["entity_id"], "entity_type": "supplier"})

        # Match manufacturing plants (factory, labour, power, production)
        for p in self.plants:
            if p["city"] in loc_set or p["country"] in loc_set:
                matches.append({"entity_id": p["entity_id"], "entity_type": "plant"})

        # Match warehouses (inventory, demand, regional distribution, stock)
        for w in self.warehouses:
            if w["city"] in loc_set or w["country"] in loc_set:
                matches.append({"entity_id": w["entity_id"], "entity_type": "warehouse"})

        # Match transport routes (port, road, rail, air, container)
        for r in self.routes:
            if (
                r["origin_city"] in loc_set
                or r["dest_city"] in loc_set
                or r["origin_country"] in loc_set
                or r["dest_country"] in loc_set
            ):
                matches.append({"entity_id": r["entity_id"], "entity_type": "route"})

        # Deduplicate matches
        seen = set()
        deduped = []
        for m in matches:
            k = (m["entity_id"], m["entity_type"])
            if k not in seen:
                seen.add(k)
                deduped.append(m)

        # Fallback if no direct match: assign to default node based on theme
        if not deduped:
            if "port" in theme_str or "transit" in theme_str:
                deduped.append({"entity_id": "RT001", "entity_type": "route"})
            elif "power" in theme_str or "factory" in theme_str:
                deduped.append({"entity_id": "PLT001", "entity_type": "plant"})
            elif "stock" in theme_str or "demand" in theme_str:
                deduped.append({"entity_id": "WH001", "entity_type": "warehouse"})
            else:
                deduped.append({"entity_id": "SUP001", "entity_type": "supplier"})

        return deduped


if __name__ == "__main__":
    linker = SupplyChainNERLinker()
    test_headline = "Heavy monsoon rains and urban flooding stall supply routes around Chennai"
    entities = linker.link_entities(test_headline, city="Chennai", country="India", theme="flood")
    print(f"Test headline: '{test_headline}'")
    print(f"Extracted entities: {entities}")
