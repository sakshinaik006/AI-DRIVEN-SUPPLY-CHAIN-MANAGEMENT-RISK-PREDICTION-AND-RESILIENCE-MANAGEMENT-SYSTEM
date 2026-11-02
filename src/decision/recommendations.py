"""Decision Layer: Actionable Resilience Recommendations.
Owned by Member 1 (Data, Graph, and Dashboard Engineer).

Audited and corrected for Stage 8:
- Connects prescriptive decision logic directly to verified network assets and risk categories.
- Distinguishes model-triggered mitigation recommendations from safe operating notices.
- Explicitly tags action type ('Prescriptive Mitigation' vs 'Operational Notice').
- Clears unsupported percentage claims and limits outputs for safe/low-risk entities.
"""
from typing import List, Dict, Any, Optional


def generate_recommendations(
    risk_type: str,
    level: str,
    entity_id: str,
    probability: Optional[float] = None,
    top_reasons: Optional[List[str]] = None,
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

    # Rule: Safe / Low-risk nodes do not receive emergency resilience playbooks
    if lvl == "Low" or (probability is not None and probability < 0.25):
        return [{
            "action": f"Node {entity_id} is operating safely within baseline tolerances. No emergency resilience intervention required.",
            "priority": "Normal",
            "action_type": "Operational Notice",
            "status": "Nominal",
        }]

    if risk_type == "supplier_failure":
        if lvl == "High":
            actions.append({
                "action": f"Initiate vendor failover for {entity_id}: switch purchase allocation to pre-qualified secondary tier supplier.",
                "priority": "Critical",
                "action_type": "Prescriptive Mitigation",
                "status": "Action Required",
            })
            actions.append({
                "action": f"Review active delivery backlog with {entity_id} and request priority air dispatch.",
                "priority": "High",
                "action_type": "Prescriptive Mitigation",
                "status": "Action Required",
            })
        elif lvl == "Medium":
            actions.append({
                "action": f"Increase supplier check-in frequency and track rolling lead-time variance for {entity_id}.",
                "priority": "Medium",
                "action_type": "Prescriptive Mitigation",
                "status": "Monitoring",
            })

    elif risk_type == "manufacturing_delay":
        if lvl == "High":
            actions.append({
                "action": f"Rebalance assembly lot schedule at {entity_id}: prioritize core contractual models.",
                "priority": "Critical",
                "action_type": "Prescriptive Mitigation",
                "status": "Action Required",
            })
            actions.append({
                "action": f"Prepare standby shift operator reallocation to recover output deficit at {entity_id}.",
                "priority": "High",
                "action_type": "Prescriptive Mitigation",
                "status": "Action Required",
            })
        elif lvl == "Medium":
            actions.append({
                "action": f"Reschedule non-urgent preventive maintenance during off-peak weekend hours at {entity_id}.",
                "priority": "Medium",
                "action_type": "Prescriptive Mitigation",
                "status": "Monitoring",
            })

    elif risk_type == "warehouse_stockout":
        if lvl == "High":
            actions.append({
                "action": f"Stockout alert at {entity_id}: raise safety stock buffer threshold by +20% and trigger emergency cross-dock hub transfer.",
                "priority": "Critical",
                "action_type": "Prescriptive Mitigation",
                "status": "Action Required",
            })
            actions.append({
                "action": f"Prioritize delivery of backlogged customer orders over bulk non-contractual orders at {entity_id}.",
                "priority": "High",
                "action_type": "Prescriptive Mitigation",
                "status": "Action Required",
            })
        elif lvl == "Medium":
            actions.append({
                "action": f"Increase safety stock buffer threshold by +15% at {entity_id} to absorb demand variance.",
                "priority": "Medium",
                "action_type": "Prescriptive Mitigation",
                "status": "Monitoring",
            })

    elif risk_type == "transport_disruption":
        if lvl == "High":
            actions.append({
                "action": f"Reroute high-priority freight shipments along corridor {entity_id} to alternative air express lane.",
                "priority": "Critical",
                "action_type": "Prescriptive Mitigation",
                "status": "Action Required",
            })
            actions.append({
                "action": f"Notify downstream receiving hubs of anticipated coastal/port transit dwell on {entity_id}.",
                "priority": "High",
                "action_type": "Prescriptive Mitigation",
                "status": "Action Required",
            })
        elif lvl == "Medium":
            actions.append({
                "action": f"Stage forward buffer inventory at regional multimodal hub along corridor {entity_id}.",
                "priority": "Medium",
                "action_type": "Prescriptive Mitigation",
                "status": "Monitoring",
            })

    return actions
