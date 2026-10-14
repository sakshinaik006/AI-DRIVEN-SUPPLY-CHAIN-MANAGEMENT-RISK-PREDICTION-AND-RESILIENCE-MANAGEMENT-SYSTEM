"""Decision Layer: Actionable Resilience Recommendations.
Owned by Member 1 (Data, Graph, and Dashboard Engineer).

Applies prescriptive decision rules across four operational risks:
- Supplier High: switch supplier to secondary qualified vendor.
- Stockout High: raise safety stock buffer and expedite inventory transfers.
- Transport High: reroute shipments along alternate multi-modal corridors.
- Manufacturing High: re-sequence production schedules and prioritize high-value customer orders.
"""
from typing import List, Dict, Any


def generate_recommendations(
    risk_type: str,
    level: str,
    entity_id: str,
    probability: float | None = None,
    top_reasons: List[str] | None = None,
) -> List[Dict[str, Any]]:
    """Generate prescriptive mitigation actions based on risk type and severity level.

    Args:
        risk_type: 'supplier_failure', 'manufacturing_delay', 'warehouse_stockout', 'transport_disruption'.
        level: 'Low', 'Medium', 'High'.
        entity_id: Identifier of the impacted entity (e.g. 'SUP001', 'WH002').
        probability: Probability value between 0.0 and 1.0.
        top_reasons: List of top diagnostic feature drivers from TreeSHAP.

    Returns:
        List of recommended action objects.
    """
    actions = []
    lvl = level.capitalize()

    if risk_type == "supplier_failure":
        if lvl == "High":
            actions.append({
                "action": f"Initiate vendor failover for {entity_id}: switch purchase allocation to pre-qualified secondary tier supplier.",
                "priority": "Critical",
                "estimated_sla_hours": 24,
            })
            actions.append({
                "action": "Freeze new purchase order commitments to primary vendor pending quality/delay audit.",
                "priority": "High",
                "estimated_sla_hours": 48,
            })
        elif lvl == "Medium":
            actions.append({
                "action": f"Request expedited delivery confirmation from {entity_id} and review dual-sourcing options.",
                "priority": "Medium",
                "estimated_sla_hours": 72,
            })
        else:
            actions.append({
                "action": f"Maintain standard replenishment schedule with {entity_id}.",
                "priority": "Normal",
                "estimated_sla_hours": 168,
            })

    elif risk_type == "manufacturing_delay":
        if lvl == "High":
            actions.append({
                "action": f"Adjust plant schedule at {entity_id}: prioritize premium/high-margin smartphone assembly runs.",
                "priority": "Critical",
                "estimated_sla_hours": 12,
            })
            actions.append({
                "action": "Defer low-priority maintenance shutdown and reallocate standby line operators.",
                "priority": "High",
                "estimated_sla_hours": 24,
            })
        elif lvl == "Medium":
            actions.append({
                "action": f"Monitor line downtime and prepare overtime shifts at {entity_id}.",
                "priority": "Medium",
                "estimated_sla_hours": 48,
            })
        else:
            actions.append({
                "action": f"Plant {entity_id} throughput is on schedule; proceed with standard operational plan.",
                "priority": "Normal",
                "estimated_sla_hours": 168,
            })

    elif risk_type == "warehouse_stockout":
        if lvl == "High":
            actions.append({
                "action": f"Stockout alert at {entity_id}: raise safety stock buffer threshold by +20% and trigger emergency hub transfer.",
                "priority": "Critical",
                "estimated_sla_hours": 24,
            })
            actions.append({
                "action": "Prioritize fulfillment of backlogged high-tier customer orders over bulk distribution.",
                "priority": "High",
                "estimated_sla_hours": 36,
            })
        elif lvl == "Medium":
            actions.append({
                "action": f"Rebalance buffer inventory from adjacent regional warehouses to {entity_id}.",
                "priority": "Medium",
                "estimated_sla_hours": 72,
            })
        else:
            actions.append({
                "action": f"Warehouse {entity_id} maintains adequate safety stock coverage.",
                "priority": "Normal",
                "estimated_sla_hours": 168,
            })

    elif risk_type == "transport_disruption":
        if lvl == "High":
            actions.append({
                "action": f"Transit bottleneck detected on lane {entity_id}: divert active dispatches to secondary rail/air corridor.",
                "priority": "Critical",
                "estimated_sla_hours": 18,
            })
            actions.append({
                "action": "Notify regional distribution centers of anticipated 48-72h transit delay.",
                "priority": "High",
                "estimated_sla_hours": 24,
            })
        elif lvl == "Medium":
            actions.append({
                "action": f"Monitor severe weather advisory along {entity_id} lane midpoint and alert carriers.",
                "priority": "Medium",
                "estimated_sla_hours": 48,
            })
        else:
            actions.append({
                "action": f"Transport lane {entity_id} operating under normal transit conditions.",
                "priority": "Normal",
                "estimated_sla_hours": 168,
            })

    return actions
