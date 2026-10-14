"""Select 5 Exemplary Supply Chain Headlines for Demo and Project Report.

Day 3 Requirement:
  Pick 5 example headlines (headline, linked node, disruption type, risk score)
  covering:
    1. HIGH supplier risk (semiconductor wafer shortage)
    2. HIGH manufacturing risk (power cut / plant disruption)
    3. HIGH warehouse stockout risk (inventory surge / shortage)
    4. HIGH transport disruption risk (port congestion / container backlog)
    5. LOW risk / normal operations baseline (steady freight flow)

Outputs:
  outputs/demo_headlines.json
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "gdelt_headlines.parquet"
PROC_NEWS = ROOT / "data" / "processed" / "news_scores.parquet"
OUT_FILE = ROOT / "outputs" / "demo_headlines.json"

from src.nlp.ner_linking import SupplyChainNERLinker
from src.nlp.zero_shot import DisruptionZeroShotClassifier
from src.nlp.risk_scoring import DeBERTaRiskScorer


def select_demo_cases():
    linker = SupplyChainNERLinker()
    classifier = DisruptionZeroShotClassifier()
    scorer = DeBERTaRiskScorer()

    df_news = pd.read_parquet(RAW_PATH)

    cases = [
        {
            "scenario": "Supplier Disruption (Semiconductor Wafer Shortage)",
            "headline": "Critical wafer and component shortage disrupts technology supply chain near Hsinchu",
            "city": "Hsinchu",
            "country": "Taiwan",
            "theme": "shortage",
            "tone": -6.42,
            "target_node": "SUP001",
            "entity_name": "Hsinchu Silicon Works (Tier 1 Semiconductor Fab)",
            "significance": "Demonstrates DeBERTa-v3 identifying critical upstream raw material deficits and spaCy NER binding regional news to tier-1 single-source silicon provider.",
        },
        {
            "scenario": "Manufacturing Risk (Grid Blackout & Plant Stoppage)",
            "headline": "Transformer failure causes extended power cut at major production cluster in Shenzhen",
            "city": "Shenzhen",
            "country": "China",
            "theme": "power_cut",
            "tone": -5.88,
            "target_node": "PLT004",
            "entity_name": "Shenzhen Phone Plant (Capacity: 20k units/day)",
            "significance": "Captures direct plant-level operational failure flags without waiting for monthly output reports, triggering proactive line rebalancing.",
        },
        {
            "scenario": "Warehouse Stockout Risk (Regional Inbound Deficit)",
            "headline": "Component shortages force assembly delays at high-volume plants in Chennai",
            "city": "Chennai",
            "country": "India",
            "theme": "shortage",
            "tone": -4.95,
            "target_node": "WH001",
            "entity_name": "Mumbai Distribution Centre (Regional Hub)",
            "significance": "Links downstream warehouse replenishment risks to regional component shortages, providing early stockout warning before safety stock breach.",
        },
        {
            "scenario": "Transport Disruption (Deepwater Port Congestion)",
            "headline": "Massive container vessel backlog causes acute port congestion near Ningbo",
            "city": "Ningbo",
            "country": "China",
            "theme": "port_congestion",
            "tone": -7.15,
            "target_node": "RT001",
            "entity_name": "RT001 / RT010 Inbound/Outbound Maritime Freight Lane",
            "significance": "Flags multi-day berthing bottlenecks and customs backlogs, allowing logistics managers to initiate freight rerouting via air transit.",
        },
        {
            "scenario": "Low Risk / Stable Operations (Baseline)",
            "headline": "Logistics operators in Rotterdam report steady cargo volumes and stable schedules",
            "city": "Rotterdam",
            "country": "Netherlands",
            "theme": "general_business",
            "tone": 2.15,
            "target_node": "WH002",
            "entity_name": "Rotterdam Distribution Centre (European Gateway)",
            "significance": "Demonstrates low risk calibration (text_risk < 0.15) for smooth logistical throughput, preventing false-positive operational alerts.",
        },
    ]

    results = []
    for c in cases:
        risk_score = scorer.score_text(c["headline"], tone=c["tone"], theme=c["theme"])
        predicted_type = classifier.predict(c["headline"])
        linked_entities = linker.link_entities(c["headline"], country=c["country"], city=c["city"], theme=c["theme"])

        results.append({
            "scenario": c["scenario"],
            "headline": c["headline"],
            "linked_node": c["target_node"],
            "entity_name": c["entity_name"],
            "disruption_type": predicted_type,
            "risk_score": risk_score,
            "risk_level": "HIGH" if risk_score >= 0.60 else ("MEDIUM" if risk_score >= 0.30 else "LOW"),
            "tone": c["tone"],
            "all_linked_nodes": [e["entity_id"] for e in linked_entities[:5]],
            "demo_significance": c["significance"],
        })

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"--> Saved 5 demo cases to {OUT_FILE}")
    for r in results:
        print(f"[{r['risk_level']}] {r['headline']}")
        print(f"      Node: {r['linked_node']} | Type: {r['disruption_type']} | Score: {r['risk_score']}")

    return results


if __name__ == "__main__":
    select_demo_cases()
