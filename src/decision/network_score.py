"""Decision Layer: Composite Network Risk Score.
Owned by Member 1 (Data, Graph, and Dashboard Engineer).

Formula:
Network Risk = 0.25 * Supplier + 0.25 * Manufacturing + 0.20 * Stockout + 0.20 * Transport + 0.10 * External

Weights are explicit prototype assumptions documented in docs/assumptions.md and docs/disclosure.md.
"""
from typing import Dict, Any


DEFAULT_WEIGHTS = {
    "supplier": 0.25,
    "manufacturing": 0.25,
    "stockout": 0.20,
    "transport": 0.20,
    "external": 0.10,
}


def compute_network_risk(
    supplier_prob: float,
    manufacturing_prob: float,
    stockout_prob: float,
    transport_prob: float,
    external_score: float = 0.0,
    weights: Dict[str, float] | None = None,
    cutoffs: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    """Calculate the weighted composite network risk score and level.

    Args:
        supplier_prob: Probability of supplier disruption in [0, 1].
        manufacturing_prob: Probability of manufacturing shortfall in [0, 1].
        stockout_prob: Probability of warehouse stockout in [0, 1].
        transport_prob: Probability of transport delay in [0, 1].
        external_score: Weather/news risk indicator in [0, 1] (defaults to 0.0).
        weights: Dictionary of component weights summing to 1.0.
        cutoffs: Dictionary with 'low_max' and 'high_min' thresholds.

    Returns:
        Dictionary with composite network score, risk level, and component breakdown.
    """
    w = weights or DEFAULT_WEIGHTS
    c = cutoffs or {"low_max": 0.30, "high_min": 0.60}

    composite_score = (
        w["supplier"] * float(supplier_prob)
        + w["manufacturing"] * float(manufacturing_prob)
        + w["stockout"] * float(stockout_prob)
        + w["transport"] * float(transport_prob)
        + w["external"] * float(external_score)
    )
    composite_score = round(max(0.0, min(1.0, composite_score)), 4)

    if composite_score >= c["high_min"]:
        level = "High"
    elif composite_score >= c["low_max"]:
        level = "Medium"
    else:
        level = "Low"

    return {
        "network_risk": composite_score,
        "level": level,
        "components": {
            "supplier": round(float(supplier_prob), 4),
            "manufacturing": round(float(manufacturing_prob), 4),
            "stockout": round(float(stockout_prob), 4),
            "transport": round(float(transport_prob), 4),
            "external": round(float(external_score), 4),
        },
        "weights": w,
        "weights_are_assumptions": True,
    }
