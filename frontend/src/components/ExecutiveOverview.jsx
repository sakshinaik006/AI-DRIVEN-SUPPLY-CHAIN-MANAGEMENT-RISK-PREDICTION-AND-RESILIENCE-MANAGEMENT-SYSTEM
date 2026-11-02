import React from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from "recharts";

export function ExecutiveOverview({
  scenarioData,
  selectedDate,
  onSelectDate,
  dateOptions,
  onNavigateToRiskAnalysis,
}) {
  if (!scenarioData) {
    return (
      <div style={{ padding: "32px", color: "var(--text-muted)" }}>
        Loading executive summary data...
      </div>
    );
  }

  const {
    total_entities = 27,
    high_risk_count = 0,
    medium_risk_count = 0,
    low_risk_count = 27,
    category_summary = {},
    top_alerts = [],
    overall_network_score = 0.0,
    overall_health = "Stable",
  } = scenarioData;

  // Distribution data for the single overall distribution visualization
  const distributionData = [
    {
      category: "Network Breakdown",
      low: low_risk_count,
      medium: medium_risk_count,
      high: high_risk_count,
    },
  ];

  const highPct = Math.round((high_risk_count / total_entities) * 100);
  const medPct = Math.round((medium_risk_count / total_entities) * 100);
  const lowPct = 100 - highPct - medPct;

  // Category mapping
  const categories = [
    {
      key: "Supplier Risk",
      internalKey: "supplier",
      title: "Supplier Failure",
      entityCount: 8,
      data: category_summary["Supplier Risk"] || { level: "Low", avg_probability: 0.05 },
    },
    {
      key: "Manufacturing Risk",
      internalKey: "manufacturing",
      title: "Manufacturing Delay",
      entityCount: 4,
      data: category_summary["Manufacturing Risk"] || { level: "Low", avg_probability: 0.05 },
    },
    {
      key: "Warehouse Stockout",
      internalKey: "warehouse",
      title: "Warehouse Stockout",
      entityCount: 5,
      data: category_summary["Warehouse Stockout"] || { level: "Low", avg_probability: 0.05 },
    },
    {
      key: "Transportation Delay",
      internalKey: "transport",
      title: "Transport Disruption",
      entityCount: 10,
      data: category_summary["Transportation Delay"] || { level: "Low", avg_probability: 0.05 },
    },
  ];

  function getBadgeStyle(level) {
    const l = (level || "Low").toLowerCase();
    if (l === "high") {
      return {
        color: "var(--risk-high-text)",
        backgroundColor: "var(--risk-high-bg)",
        border: "1px solid var(--risk-high-border)",
      };
    }
    if (l === "medium") {
      return {
        color: "var(--risk-medium-text)",
        backgroundColor: "var(--risk-medium-bg)",
        border: "1px solid var(--risk-medium-border)",
      };
    }
    return {
      color: "var(--risk-low-text)",
      backgroundColor: "var(--risk-low-bg)",
      border: "1px solid var(--risk-low-border)",
    };
  }

  // Maximum 3 priority alerts
  const priorityAlerts = (top_alerts || []).slice(0, 3);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* 1. REPORTING HEADER & CONTEXT */}
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
            Executive Supply Chain Overview
          </h1>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "2px" }}>
            7-day predictive risk horizon across 27 multi-tier nodes (Trained CatBoost & TreeSHAP models)
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <label htmlFor="reporting-date" style={{ fontSize: "12px", fontWeight: 500, color: "var(--text-secondary)" }}>
            Observation Date:
          </label>
          <select
            id="reporting-date"
            value={selectedDate}
            onChange={(e) => onSelectDate(e.target.value)}
            style={{
              padding: "6px 10px",
              fontSize: "13px",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--border-strong)",
              backgroundColor: "var(--bg-surface)",
              color: "var(--text-primary)",
              outline: "none",
            }}
          >
            {dateOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 2. FOUR KEY METRICS */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "14px",
        }}
      >
        {/* Metric 1 */}
        <div
          style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-light)",
            borderRadius: "var(--radius-md)",
            padding: "16px",
          }}
        >
          <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: 600 }}>
            Entities Monitored
          </div>
          <div style={{ fontSize: "28px", fontWeight: 700, color: "var(--text-primary)", marginTop: "6px" }}>
            {total_entities}
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
            8 Suppliers, 4 Plants, 5 Hubs, 10 Routes
          </div>
        </div>

        {/* Metric 2: High Risk */}
        <div
          style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-light)",
            borderLeft: high_risk_count > 0 ? "4px solid var(--risk-high-text)" : "1px solid var(--border-light)",
            borderRadius: "var(--radius-md)",
            padding: "16px",
          }}
        >
          <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: 600 }}>
            High-Risk Entities
          </div>
          <div style={{ fontSize: "28px", fontWeight: 700, color: high_risk_count > 0 ? "var(--risk-high-text)" : "var(--text-primary)", marginTop: "6px" }}>
            {high_risk_count}
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
            Immediate operational mitigation required
          </div>
        </div>

        {/* Metric 3: Medium Risk */}
        <div
          style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-light)",
            borderLeft: medium_risk_count > 0 ? "4px solid var(--risk-medium-text)" : "1px solid var(--border-light)",
            borderRadius: "var(--radius-md)",
            padding: "16px",
          }}
        >
          <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: 600 }}>
            Medium-Risk Entities
          </div>
          <div style={{ fontSize: "28px", fontWeight: 700, color: medium_risk_count > 0 ? "var(--risk-medium-text)" : "var(--text-primary)", marginTop: "6px" }}>
            {medium_risk_count}
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
            Close monitoring & safety buffer checks
          </div>
        </div>

        {/* Metric 4: Low Risk */}
        <div
          style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-light)",
            borderLeft: "4px solid var(--risk-low-text)",
            borderRadius: "var(--radius-md)",
            padding: "16px",
          }}
        >
          <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: 600 }}>
            Low-Risk / Nominal
          </div>
          <div style={{ fontSize: "28px", fontWeight: 700, color: "var(--risk-low-text)", marginTop: "6px" }}>
            {low_risk_count}
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
            Operating safely within baseline tolerances
          </div>
        </div>
      </div>

      {/* 3. OVERALL RISK DISTRIBUTION VISUALIZATION */}
      <div
        style={{
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-light)",
          borderRadius: "var(--radius-md)",
          padding: "16px 20px",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
          <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
            Network Risk Distribution
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
            Composite Index: <strong style={{ color: "var(--text-primary)" }}>{(overall_network_score * 100).toFixed(1)}%</strong> ({overall_health})
          </div>
        </div>

        {/* Single Proportional Stacked Bar */}
        <div
          style={{
            height: "22px",
            width: "100%",
            display: "flex",
            borderRadius: "var(--radius-sm)",
            overflow: "hidden",
            backgroundColor: "#f1f5f9",
          }}
        >
          {low_risk_count > 0 && (
            <div
              style={{
                width: `${lowPct}%`,
                backgroundColor: "#16a34a",
                transition: "width 0.3s ease",
              }}
              title={`Low Risk: ${low_risk_count} nodes (${lowPct}%)`}
            />
          )}
          {medium_risk_count > 0 && (
            <div
              style={{
                width: `${medPct}%`,
                backgroundColor: "#d97706",
                transition: "width 0.3s ease",
              }}
              title={`Medium Risk: ${medium_risk_count} nodes (${medPct}%)`}
            />
          )}
          {high_risk_count > 0 && (
            <div
              style={{
                width: `${highPct}%`,
                backgroundColor: "#dc2626",
                transition: "width 0.3s ease",
              }}
              title={`High Risk: ${high_risk_count} nodes (${highPct}%)`}
            />
          )}
        </div>

        {/* Distribution Legend */}
        <div style={{ display: "flex", gap: "24px", marginTop: "10px", fontSize: "12px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", backgroundColor: "#16a34a", borderRadius: "2px" }} />
            <span style={{ color: "var(--text-secondary)" }}>
              Low Risk: <strong>{low_risk_count}</strong> ({lowPct}%)
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", backgroundColor: "#d97706", borderRadius: "2px" }} />
            <span style={{ color: "var(--text-secondary)" }}>
              Medium Risk: <strong>{medium_risk_count}</strong> ({medPct}%)
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", backgroundColor: "#dc2626", borderRadius: "2px" }} />
            <span style={{ color: "var(--text-secondary)" }}>
              High Risk: <strong>{high_risk_count}</strong> ({highPct}%)
            </span>
          </div>
        </div>
      </div>

      {/* 4. FOUR RISK CATEGORY SUMMARIES */}
      <div>
        <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "10px" }}>
          Operational Risk Categories
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
            gap: "14px",
          }}
        >
          {categories.map((cat) => {
            const badge = getBadgeStyle(cat.data.level);
            return (
              <div
                key={cat.key}
                onClick={() => onNavigateToRiskAnalysis && onNavigateToRiskAnalysis(cat.internalKey)}
                style={{
                  backgroundColor: "var(--bg-surface)",
                  border: "1px solid var(--border-light)",
                  borderRadius: "var(--radius-md)",
                  padding: "16px",
                  cursor: "pointer",
                  transition: "border-color 0.15s ease",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--border-strong)")}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--border-light)")}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                    {cat.title}
                  </span>
                  <span
                    style={{
                      fontSize: "11px",
                      fontWeight: 600,
                      padding: "2px 8px",
                      borderRadius: "var(--radius-sm)",
                      ...badge,
                    }}
                  >
                    {cat.data.level}
                  </span>
                </div>

                <div style={{ marginTop: "12px", display: "flex", justifyContent: "space-between", fontSize: "12px", color: "var(--text-muted)" }}>
                  <span>Scope: {cat.entityCount} Nodes</span>
                  <span>Avg Probability: <strong>{Math.round(cat.data.avg_probability * 100)}%</strong></span>
                </div>

                <div
                  style={{
                    marginTop: "12px",
                    paddingTop: "10px",
                    borderTop: "1px solid var(--border-light)",
                    fontSize: "12px",
                    color: "var(--accent-teal)",
                    fontWeight: 500,
                    display: "flex",
                    justifyContent: "space-between",
                  }}
                >
                  <span>View Category Details</span>
                  <span>→</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 5. MAXIMUM THREE PRIORITY ALERTS */}
      <div
        style={{
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-light)",
          borderRadius: "var(--radius-md)",
          padding: "16px 20px",
        }}
      >
        <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "12px" }}>
          Priority Action Alerts (Top 3)
        </div>

        {priorityAlerts.length === 0 ? (
          <div style={{ fontSize: "13px", color: "var(--text-muted)", padding: "12px 0" }}>
            No elevated risk alerts for this reporting date. All nodes are operating within nominal baseline parameters.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {priorityAlerts.map((alert, idx) => {
              const badge = getBadgeStyle(alert.level);
              return (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    justifyContent: "space-between",
                    padding: "12px 14px",
                    backgroundColor: "var(--bg-app)",
                    border: "1px solid var(--border-light)",
                    borderRadius: "var(--radius-sm)",
                    gap: "12px",
                  }}
                >
                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
                        {alert.entity_id} — {alert.name || alert.entity_id}
                      </span>
                      <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                        ({alert.category || alert.risk_type})
                      </span>
                      <span
                        style={{
                          fontSize: "11px",
                          fontWeight: 600,
                          padding: "1px 6px",
                          borderRadius: "var(--radius-sm)",
                          ...badge,
                        }}
                      >
                        {alert.level} ({Math.round((alert.probability || 0.5) * 100)}%)
                      </span>
                    </div>
                    <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                      {alert.summary || alert.recommended_action || "Elevated disruption probability detected based on historical lead time and localized disruption signals."}
                    </div>
                  </div>

                  <button
                    onClick={() => onNavigateToRiskAnalysis && onNavigateToRiskAnalysis(null, alert.entity_id)}
                    style={{
                      fontSize: "12px",
                      color: "var(--accent-teal)",
                      fontWeight: 500,
                      whiteSpace: "nowrap",
                      padding: "4px 8px",
                      border: "1px solid var(--accent-teal-border)",
                      backgroundColor: "var(--accent-teal-subtle)",
                      borderRadius: "var(--radius-sm)",
                    }}
                  >
                    Inspect
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
