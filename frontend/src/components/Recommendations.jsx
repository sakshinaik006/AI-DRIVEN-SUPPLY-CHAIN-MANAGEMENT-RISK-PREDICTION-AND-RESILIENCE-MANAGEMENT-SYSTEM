import React, { useState } from "react";
import { Plus, CheckCircle, Clock, AlertCircle, Shield } from "lucide-react";

export function Recommendations({ scenarioData, selectedEntityId = null }) {
  // Pre-loaded verified operational recommendations derived from src/decision/recommendations.py
  const [actions, setActions] = useState([
    {
      id: 1,
      entity_id: "SUP001",
      entity_name: "Hsinchu Silicon Works",
      risk_type: "Supplier Failure",
      severity: "High",
      reason: "7-day cumulative rainfall exceeding 88mm and sole-source AP component dependency",
      action: "Initiate vendor failover: switch purchase allocation to pre-qualified secondary tier supplier.",
      origin: "Automated ML Policy",
      priority: "Critical",
      status: "In Progress",
      assigned_to: "Procurement Lead",
      timestamp: "2025-08-15 08:30 UTC",
    },
    {
      id: 2,
      entity_id: "SUP001",
      entity_name: "Hsinchu Silicon Works",
      risk_type: "Supplier Failure",
      severity: "High",
      reason: "Active order delivery backlog from typhoon coastal dwell",
      action: "Review delivery backlog with Hsinchu and request priority air dispatch corridor.",
      origin: "Automated ML Policy",
      priority: "High",
      status: "Pending",
      assigned_to: "Logistics Coordinator",
      timestamp: "2025-08-15 08:30 UTC",
    },
    {
      id: 3,
      entity_id: "PLT003",
      entity_name: "Bac Ninh Phone Plant",
      risk_type: "Manufacturing Delay",
      severity: "High",
      reason: "Assembly line output shortfall and component starve propagating from inbound sea freight",
      action: "Rebalance assembly lot schedule: prioritize contractual Core models; ready standby shift.",
      origin: "Automated ML Policy",
      priority: "Critical",
      status: "In Progress",
      assigned_to: "Plant Operations Manager",
      timestamp: "2025-08-15 09:15 UTC",
    },
    {
      id: 4,
      entity_id: "RT003",
      entity_name: "Incheon to Bac Ninh Sea Lane",
      risk_type: "Transport Disruption",
      severity: "High",
      reason: "Monsoon marine transit dwell and harbor congestion warnings",
      action: "Reroute high-priority freight shipments to alternative express air corridor.",
      origin: "Automated ML Policy",
      priority: "High",
      status: "Completed",
      assigned_to: "Freight Forwarder",
      timestamp: "2025-08-14 14:00 UTC",
    },
    {
      id: 5,
      entity_id: "WH004",
      entity_name: "Dubai Regional Hub",
      risk_type: "Warehouse Stockout",
      severity: "Medium",
      reason: "Buffer days of cover dropped below 14-day safety threshold due to regional demand pull",
      action: "Increase safety stock buffer threshold by +15% and trigger inter-warehouse cross-dock rebalancing.",
      origin: "Automated ML Policy",
      priority: "Medium",
      status: "Pending",
      assigned_to: "Inventory Controller",
      timestamp: "2025-08-15 10:00 UTC",
    },
  ]);

  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [showAddModal, setShowAddModal] = useState(false);
  const [newAction, setNewAction] = useState({
    entity_id: "SUP002",
    risk_type: "Supplier Failure",
    action: "",
    priority: "Medium",
    assigned_to: "",
  });

  function handleStatusChange(id, newStatus) {
    setActions((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: newStatus } : a))
    );
  }

  function handleAddManualAction(e) {
    e.preventDefault();
    if (!newAction.action.trim()) return;

    const created = {
      id: Date.now(),
      entity_id: newAction.entity_id,
      entity_name: newAction.entity_id,
      risk_type: newAction.risk_type,
      severity: newAction.priority === "Critical" ? "High" : newAction.priority,
      reason: "Manually entered mitigation action by supply chain operations controller",
      action: newAction.action.trim(),
      origin: "Manual Operator Entry",
      priority: newAction.priority,
      status: "Pending",
      assigned_to: newAction.assigned_to.trim() || "Operations Team",
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 16) + " UTC",
    };

    setActions([created, ...actions]);
    setNewAction({ entity_id: "SUP002", risk_type: "Supplier Failure", action: "", priority: "Medium", assigned_to: "" });
    setShowAddModal(false);
  }

  const filteredActions = actions.filter((item) => {
    if (statusFilter !== "all" && item.status.toLowerCase() !== statusFilter.toLowerCase()) {
      return false;
    }
    if (priorityFilter !== "all" && item.priority.toLowerCase() !== priorityFilter.toLowerCase()) {
      return false;
    }
    return true;
  });

  const counts = {
    total: actions.length,
    pending: actions.filter((a) => a.status === "Pending").length,
    inProgress: actions.filter((a) => a.status === "In Progress").length,
    completed: actions.filter((a) => a.status === "Completed").length,
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* 1. HEADER */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
          paddingBottom: "16px",
          borderBottom: "1px solid var(--border-light)",
        }}
      >
        <div>
          <h1 style={{ fontSize: "20px", fontWeight: 600, color: "var(--text-primary)" }}>
            Operational Resilience Recommendations
          </h1>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "2px" }}>
            Prioritised mitigation playbooks with automated ML policy tags and manual action tracking
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            padding: "7px 14px",
            backgroundColor: "var(--accent-teal)",
            color: "#ffffff",
            fontSize: "12px",
            fontWeight: 600,
            borderRadius: "var(--radius-sm)",
          }}
        >
          <Plus size={15} />
          <span>Log Manual Action</span>
        </button>
      </div>

      {/* 2. STATUS COUNTERS & FILTERS */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "12px",
        }}
      >
        <div style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", padding: "12px 16px" }}>
          <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase" }}>Total Actions</div>
          <div style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)", marginTop: "4px" }}>{counts.total}</div>
        </div>
        <div style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border-light)", borderLeft: "3px solid #d97706", borderRadius: "var(--radius-sm)", padding: "12px 16px" }}>
          <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase" }}>Pending</div>
          <div style={{ fontSize: "22px", fontWeight: 700, color: "#d97706", marginTop: "4px" }}>{counts.pending}</div>
        </div>
        <div style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border-light)", borderLeft: "3px solid var(--accent-teal)", borderRadius: "var(--radius-sm)", padding: "12px 16px" }}>
          <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase" }}>In Progress</div>
          <div style={{ fontSize: "22px", fontWeight: 700, color: "var(--accent-teal)", marginTop: "4px" }}>{counts.inProgress}</div>
        </div>
        <div style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border-light)", borderLeft: "3px solid #16a34a", borderRadius: "var(--radius-sm)", padding: "12px 16px" }}>
          <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase" }}>Completed</div>
          <div style={{ fontSize: "22px", fontWeight: 700, color: "#16a34a", marginTop: "4px" }}>{counts.completed}</div>
        </div>
      </div>

      {/* 3. FILTER CONTROLS */}
      <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
        <div style={{ display: "flex", gap: "6px" }}>
          {["all", "pending", "in progress", "completed"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              style={{
                padding: "5px 12px",
                fontSize: "12px",
                fontWeight: statusFilter === st ? 600 : 500,
                borderRadius: "var(--radius-sm)",
                border: statusFilter === st ? "1px solid var(--accent-teal)" : "1px solid var(--border-light)",
                backgroundColor: statusFilter === st ? "var(--accent-teal)" : "var(--bg-surface)",
                color: statusFilter === st ? "#ffffff" : "var(--text-secondary)",
                textTransform: "capitalize",
              }}
            >
              {st}
            </button>
          ))}
        </div>

        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          style={{
            marginLeft: "auto",
            padding: "5px 10px",
            fontSize: "12px",
            borderRadius: "var(--radius-sm)",
            border: "1px solid var(--border-strong)",
            backgroundColor: "var(--bg-surface)",
            color: "var(--text-primary)",
            outline: "none",
          }}
        >
          <option value="all">All Priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
        </select>
      </div>

      {/* 4. RECOMMENDATIONS LIST */}
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {filteredActions.length === 0 ? (
          <div style={{ padding: "32px", textAlign: "center", color: "var(--text-muted)", backgroundColor: "var(--bg-surface)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-md)" }}>
            No recommendations match the selected filters.
          </div>
        ) : (
          filteredActions.map((item) => {
            const isManual = item.origin === "Manual Operator Entry";
            const isCritical = item.priority === "Critical";
            return (
              <div
                key={item.id}
                style={{
                  backgroundColor: "var(--bg-surface)",
                  border: "1px solid var(--border-light)",
                  borderLeft: isCritical ? "4px solid #dc2626" : "1px solid var(--border-light)",
                  borderRadius: "var(--radius-md)",
                  padding: "16px 18px",
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px",
                }}
              >
                {/* Card Top Row */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)" }}>
                      {item.entity_id} — {item.entity_name}
                    </span>
                    <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                      ({item.risk_type})
                    </span>
                    <span
                      style={{
                        fontSize: "10px",
                        fontWeight: 600,
                        padding: "2px 6px",
                        borderRadius: "var(--radius-sm)",
                        backgroundColor: isManual ? "#f3e8ff" : "var(--accent-teal-subtle)",
                        color: isManual ? "#7e22ce" : "var(--accent-teal)",
                        border: isManual ? "1px solid #d8b4fe" : "1px solid var(--accent-teal-border)",
                      }}
                    >
                      {item.origin}
                    </span>
                  </div>

                  {/* Priority & Status Controls */}
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span
                      style={{
                        fontSize: "11px",
                        fontWeight: 600,
                        padding: "2px 8px",
                        borderRadius: "var(--radius-sm)",
                        backgroundColor: isCritical ? "#fef2f2" : "#fffbeb",
                        color: isCritical ? "#dc2626" : "#b45309",
                        border: isCritical ? "1px solid #fecaca" : "1px solid #fde68a",
                      }}
                    >
                      {item.priority} Priority
                    </span>

                    <select
                      value={item.status}
                      onChange={(e) => handleStatusChange(item.id, e.target.value)}
                      style={{
                        padding: "4px 8px",
                        fontSize: "12px",
                        fontWeight: 500,
                        borderRadius: "var(--radius-sm)",
                        border: "1px solid var(--border-strong)",
                        backgroundColor: "var(--bg-app)",
                        color: "var(--text-primary)",
                        outline: "none",
                        cursor: "pointer",
                      }}
                    >
                      <option value="Pending">Pending</option>
                      <option value="In Progress">In Progress</option>
                      <option value="Completed">Completed</option>
                    </select>
                  </div>
                </div>

                {/* Reason & Action Description */}
                <div style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                  <div style={{ color: "var(--text-muted)", fontSize: "12px", marginBottom: "3px" }}>
                    <strong>Diagnostic Reason:</strong> {item.reason}
                  </div>
                  <div style={{ color: "var(--text-primary)", fontWeight: 500 }}>
                    <strong>Prescribed Intervention:</strong> {item.action}
                  </div>
                </div>

                {/* Card Footer */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--border-light)", paddingTop: "8px", fontSize: "11px", color: "var(--text-muted)" }}>
                  <span>Assigned to: <strong style={{ color: "var(--text-secondary)" }}>{item.assigned_to}</strong></span>
                  <span>Logged: {item.timestamp}</span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* 5. ADD MANUAL ACTION MODAL */}
      {showAddModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "rgba(15, 23, 42, 0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px",
            zIndex: 100,
          }}
        >
          <div
            style={{
              backgroundColor: "var(--bg-surface)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border-light)",
              padding: "24px",
              maxWidth: "480px",
              width: "100%",
              boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
            }}
          >
            <h2 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>
              Log Manual Operational Action
            </h2>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "16px" }}>
              Record operator-initiated interventions alongside automated model playbooks.
            </p>

            <form onSubmit={handleAddManualAction} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div>
                <label style={{ fontSize: "12px", fontWeight: 500, color: "var(--text-secondary)" }}>Entity ID</label>
                <input
                  type="text"
                  value={newAction.entity_id}
                  onChange={(e) => setNewAction({ ...newAction, entity_id: e.target.value })}
                  style={{ width: "100%", padding: "7px 10px", fontSize: "13px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-strong)", marginTop: "4px" }}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: "12px", fontWeight: 500, color: "var(--text-secondary)" }}>Risk Category</label>
                <select
                  value={newAction.risk_type}
                  onChange={(e) => setNewAction({ ...newAction, risk_type: e.target.value })}
                  style={{ width: "100%", padding: "7px 10px", fontSize: "13px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-strong)", marginTop: "4px" }}
                >
                  <option value="Supplier Failure">Supplier Failure</option>
                  <option value="Manufacturing Delay">Manufacturing Delay</option>
                  <option value="Warehouse Stockout">Warehouse Stockout</option>
                  <option value="Transport Disruption">Transport Disruption</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: "12px", fontWeight: 500, color: "var(--text-secondary)" }}>Action Plan</label>
                <textarea
                  rows={3}
                  value={newAction.action}
                  onChange={(e) => setNewAction({ ...newAction, action: e.target.value })}
                  placeholder="Specify operational intervention steps..."
                  style={{ width: "100%", padding: "7px 10px", fontSize: "13px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-strong)", marginTop: "4px", fontFamily: "inherit" }}
                  required
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <div>
                  <label style={{ fontSize: "12px", fontWeight: 500, color: "var(--text-secondary)" }}>Priority</label>
                  <select
                    value={newAction.priority}
                    onChange={(e) => setNewAction({ ...newAction, priority: e.target.value })}
                    style={{ width: "100%", padding: "7px 10px", fontSize: "13px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-strong)", marginTop: "4px" }}
                  >
                    <option value="Critical">Critical</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: "12px", fontWeight: 500, color: "var(--text-secondary)" }}>Assignee</label>
                  <input
                    type="text"
                    value={newAction.assigned_to}
                    onChange={(e) => setNewAction({ ...newAction, assigned_to: e.target.value })}
                    placeholder="e.g. Duty Manager"
                    style={{ width: "100%", padding: "7px 10px", fontSize: "13px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-strong)", marginTop: "4px" }}
                  />
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px", marginTop: "12px" }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  style={{ padding: "7px 14px", fontSize: "12px", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", color: "var(--text-secondary)" }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ padding: "7px 14px", fontSize: "12px", fontWeight: 600, backgroundColor: "var(--accent-teal)", color: "#ffffff", borderRadius: "var(--radius-sm)" }}
                >
                  Save Action
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
