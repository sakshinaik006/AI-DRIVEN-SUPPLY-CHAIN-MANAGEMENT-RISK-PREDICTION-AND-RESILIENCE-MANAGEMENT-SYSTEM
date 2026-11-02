"""Decision Layer: Composite Network Risk Score.
Owned by Member 1 (Data, Graph, and Dashboard Engineer).

Formula:
Network Risk = w_sup * Supplier + w_mfg * Manufacturing + w_wh * Stockout + w_tr * Transport + w_ext * External

Audited and corrected for Stage 8:
- Weights are strictly validated: must sum to 1.0 (with a 1e-4 tolerance).
- Component probabilities must be in [0.0, 1.0].
- Missing component probabilities raise ValueError rather than silently defaulting to 0.0.
"""
from typing import Dict, Any, Optional

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
    weights: Optional[Dict[str, float]] = None,
    cutoffs: Optional[Dict[str, float]] = None,
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

    # Validate weight sum
    weight_sum = sum(w.values())
    if abs(weight_sum - 1.0) > 1e-4:
        raise ValueError(f"Weights must sum to 1.0, got sum={weight_sum:.4f}")

    # Validate inputs
    inputs = {
        "supplier": supplier_prob,
        "manufacturing": manufacturing_prob,
        "stockout": stockout_prob,
        "transport": transport_prob,
        "external": external_score,
    }
    for k, val in inputs.items():
        if val is None:
            raise ValueError(f"Component '{k}' probability cannot be None")
        if not (0.0 <= float(val) <= 1.0):
            raise ValueError(f"Component '{k}' value {val} is out of valid range [0.0, 1.0]")

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
