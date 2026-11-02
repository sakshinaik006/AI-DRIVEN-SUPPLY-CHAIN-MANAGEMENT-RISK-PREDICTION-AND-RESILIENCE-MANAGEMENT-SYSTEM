import React, { useState, useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { Search, Filter, X, ArrowUpRight } from "lucide-react";

export function RiskAnalysis({
  scenarioData,
  selectedCategory: initialCategory = "all",
  selectedEntityId: initialEntityId = null,
  onNavigateToFactors,
  onNavigateToRecommendations,
}) {
  const [activeCategoryFilter, setActiveCategoryFilter] = useState(initialCategory || "all");
  const [activeLevelFilter, setActiveLevelFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedEntity, setSelectedEntity] = useState(() => {
    if (!scenarioData?.entities) return null;
    if (initialEntityId) {
      return scenarioData.entities.find((e) => e.entity_id === initialEntityId) || scenarioData.entities[0];
    }
    return scenarioData.entities[0];
  });

  const entities = scenarioData?.entities || [];

  // Historical trend data across the simulation months (April to October)
  const historicalTrendData = useMemo(() => {
    return [
      { date: "15 Apr", supplier: 0.06, manufacturing: 0.05, warehouse: 0.06, transport: 0.05, network: 0.06 },
      { date: "15 May", supplier: 0.07, manufacturing: 0.06, warehouse: 0.08, transport: 0.06, network: 0.07 },
      { date: "15 Jun", supplier: 0.12, manufacturing: 0.18, warehouse: 0.09, transport: 0.11, network: 0.12 },
      { date: "15 Jul", supplier: 0.15, manufacturing: 0.14, warehouse: 0.12, transport: 0.16, network: 0.14 },
      { date: "15 Aug", supplier: 0.58, manufacturing: 0.42, warehouse: 0.18, transport: 0.67, network: 0.46 },
      { date: "15 Sep", supplier: 0.18, manufacturing: 0.22, warehouse: 0.24, transport: 0.20, network: 0.21 },
      { date: "24 Oct", supplier: 0.17, manufacturing: 0.14, warehouse: 0.55, transport: 0.16, network: 0.25 },
    ];
  }, []);

  // Filtered entity list
  const filteredEntities = useMemo(() => {
    return entities.filter((item) => {
      // Category filter
      if (activeCategoryFilter !== "all") {
        const cat = (item.category || item.risk_type || "").toLowerCase();
        if (!cat.includes(activeCategoryFilter.toLowerCase())) {
          return false;
        }
      }

      // Level filter
      if (activeLevelFilter !== "all") {
        const lvl = (item.level || "Low").toLowerCase();
        if (lvl !== activeLevelFilter.toLowerCase()) {
          return false;
        }
      }

      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesId = (item.entity_id || "").toLowerCase().includes(q);
        const matchesName = (item.name || "").toLowerCase().includes(q);
        const matchesCity = (item.city || "").toLowerCase().includes(q);
        const matchesCountry = (item.country || "").toLowerCase().includes(q);
        const matchesMode = (item.shipping_mode || "").toLowerCase().includes(q);
        if (!matchesId && !matchesName && !matchesCity && !matchesCountry && !matchesMode) {
          return false;
        }
      }

      return true;
    });
  }, [entities, activeCategoryFilter, activeLevelFilter, searchQuery]);

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

  const categoryPills = [
    { id: "all", label: "All Nodes", count: entities.length },
    { id: "supplier", label: "Supplier Failure", count: entities.filter((e) => e.type === "supplier").length },
    { id: "manufacturing", label: "Manufacturing Delay", count: entities.filter((e) => e.type === "plant").length },
    { id: "warehouse", label: "Warehouse Stockout", count: entities.filter((e) => e.type === "warehouse").length },
    { id: "transport", label: "Transport Disruption", count: entities.filter((e) => e.type === "route").length },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* 1. HEADER & SUMMARY */}
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
            Supply Chain Risk Analysis
          </h1>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "2px" }}>
            Granular node-level probabilities, category trends, and diagnostic risk factor inspections
          </p>
        </div>
      </div>

      {/* 2. HISTORICAL RISK TREND CHART */}
      <div
        style={{
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-light)",
          borderRadius: "var(--radius-md)",
          padding: "18px 20px",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
          <div>
            <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
              Historical Risk Trajectory (7-Day Ahead Average Probability)
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
              Monthly calibration across the 214-day observation window (April – October 2025)
            </div>
          </div>
        </div>

        <div style={{ height: "230px", width: "100%" }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={historicalTrendData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#64748b" }} axisLine={{ stroke: "#cbd5e1" }} />
              <YAxis
                domain={[0, 0.8]}
                tickFormatter={(v) => `${Math.round(v * 100)}%`}
                tick={{ fontSize: 12, fill: "#64748b" }}
                axisLine={{ stroke: "#cbd5e1" }}
              />
              <Tooltip
                formatter={(val) => [`${(val * 100).toFixed(1)}%`, ""]}
                contentStyle={{
                  backgroundColor: "var(--bg-surface)",
                  borderColor: "var(--border-light)",
                  borderRadius: "var(--radius-sm)",
                  fontSize: "12px",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
              <Line type="monotone" dataKey="supplier" name="Supplier Failure" stroke="#b45309" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="manufacturing" name="Manufacturing Delay" stroke="#0f766e" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="warehouse" name="Warehouse Stockout" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="transport" name="Transport Disruption" stroke="#7c3aed" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="network" name="Composite Network Index" stroke="#0f172a" strokeWidth={2} strokeDasharray="4 4" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. CATEGORY SELECTORS & SEARCH CONTROLS */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
        }}
      >
        {/* Category Pills */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
          {categoryPills.map((pill) => {
            const isActive = activeCategoryFilter === pill.id;
            return (
              <button
                key={pill.id}
                onClick={() => setActiveCategoryFilter(pill.id)}
                style={{
                  padding: "6px 12px",
                  fontSize: "12px",
                  fontWeight: isActive ? 600 : 500,
                  borderRadius: "var(--radius-sm)",
                  border: isActive ? "1px solid var(--accent-teal)" : "1px solid var(--border-light)",
                  backgroundColor: isActive ? "var(--accent-teal)" : "var(--bg-surface)",
                  color: isActive ? "#ffffff" : "var(--text-secondary)",
                  transition: "all 0.15s ease",
                }}
              >
                {pill.label} ({pill.count})
              </button>
            );
          })}
        </div>

        {/* Search & Severity Filter */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {/* Level Filter */}
          <select
            value={activeLevelFilter}
            onChange={(e) => setActiveLevelFilter(e.target.value)}
            style={{
              padding: "6px 10px",
              fontSize: "12px",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--border-strong)",
              backgroundColor: "var(--bg-surface)",
              color: "var(--text-primary)",
              outline: "none",
            }}
          >
            <option value="all">All Severities</option>
            <option value="high">High Risk Only</option>
            <option value="medium">Medium Risk Only</option>
            <option value="low">Low Risk / Nominal</option>
          </select>

          {/* Search Box */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "5px 10px",
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-strong)",
              borderRadius: "var(--radius-sm)",
            }}
          >
            <Search size={14} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Filter by ID, City, Name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                border: "none",
                outline: "none",
                fontSize: "12px",
                backgroundColor: "transparent",
                color: "var(--text-primary)",
                width: "160px",
              }}
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery("")} style={{ display: "flex", alignItems: "center" }}>
                <X size={12} color="var(--text-muted)" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 4. MAIN CONTENT: TABLE + DETAIL INSPECTOR */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: selectedEntity ? "1fr 340px" : "1fr",
          gap: "18px",
          alignItems: "start",
        }}
      >
        {/* Entity Table */}
        <div
          style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-light)",
            borderRadius: "var(--radius-md)",
            overflow: "hidden",
          }}
        >
          <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border-light)", fontSize: "12px", color: "var(--text-muted)", display: "flex", justifyContent: "space-between" }}>
            <span>Showing {filteredEntities.length} of {entities.length} nodes</span>
            <span>Click row to inspect contributing risk factors</span>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table>
              <thead>
                <tr style={{ backgroundColor: "var(--bg-subtle)", borderBottom: "1px solid var(--border-light)", fontSize: "12px", color: "var(--text-secondary)" }}>
                  <th style={{ padding: "10px 14px", fontWeight: 600 }}>Entity ID</th>
                  <th style={{ padding: "10px 14px", fontWeight: 600 }}>Name / Description</th>
                  <th style={{ padding: "10px 14px", fontWeight: 600 }}>Location / Mode</th>
                  <th style={{ padding: "10px 14px", fontWeight: 600 }}>Risk Category</th>
                  <th style={{ padding: "10px 14px", fontWeight: 600, textAlign: "right" }}>Probability</th>
                  <th style={{ padding: "10px 14px", fontWeight: 600, textAlign: "center" }}>Severity</th>
                  <th style={{ padding: "10px 14px", fontWeight: 600, textAlign: "right" }}>Inspect</th>
                </tr>
              </thead>
              <tbody>
                {filteredEntities.length === 0 ? (
                  <tr>
                    <td colSpan={7} style={{ padding: "24px", textAlign: "center", color: "var(--text-muted)", fontSize: "13px" }}>
                      No network entities match the selected category or filter query.
                    </td>
                  </tr>
                ) : (
                  filteredEntities.map((item) => {
                    const isSelected = selectedEntity?.entity_id === item.entity_id;
                    const badge = getBadgeStyle(item.level);
                    const probPct = Math.round((item.probability || 0.05) * 100);

                    return (
                      <tr
                        key={item.entity_id}
                        onClick={() => setSelectedEntity(item)}
                        style={{
                          borderBottom: "1px solid var(--border-light)",
                          fontSize: "13px",
                          cursor: "pointer",
                          backgroundColor: isSelected ? "var(--accent-teal-subtle)" : "transparent",
                          transition: "background-color 0.1s ease",
                        }}
                        onMouseEnter={(e) => {
                          if (!isSelected) e.currentTarget.style.backgroundColor = "var(--bg-app)";
                        }}
                        onMouseLeave={(e) => {
                          if (!isSelected) e.currentTarget.style.backgroundColor = "transparent";
                        }}
                      >
                        <td style={{ padding: "10px 14px", fontWeight: 600, color: "var(--text-primary)" }}>
                          {item.entity_id}
                        </td>
                        <td style={{ padding: "10px 14px", color: "var(--text-primary)" }}>
                          {item.name || item.entity_id}
                        </td>
                        <td style={{ padding: "10px 14px", color: "var(--text-muted)", fontSize: "12px" }}>
                          {item.city ? `${item.city}, ${item.country}` : item.shipping_mode ? `Transit (${item.shipping_mode})` : item.type}
                        </td>
                        <td style={{ padding: "10px 14px", color: "var(--text-secondary)", fontSize: "12px" }}>
                          {item.category || item.risk_type}
                        </td>
                        <td style={{ padding: "10px 14px", textAlign: "right", fontWeight: 600, color: "var(--text-primary)" }}>
                          {probPct}%
                        </td>
                        <td style={{ padding: "10px 14px", textAlign: "center" }}>
                          <span
                            style={{
                              fontSize: "11px",
                              fontWeight: 600,
                              padding: "2px 7px",
                              borderRadius: "var(--radius-sm)",
                              ...badge,
                            }}
                          >
                            {item.level || "Low"}
                          </span>
                        </td>
                        <td style={{ padding: "10px 14px", textAlign: "right" }}>
                          <span
                            style={{
                              fontSize: "12px",
                              color: isSelected ? "var(--accent-teal)" : "var(--text-muted)",
                              fontWeight: 500,
                            }}
                          >
                            {isSelected ? "Active" : "Inspect →"}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* 5. ENTITY-LEVEL DETAIL INSPECTOR (PROGRESSIVE DISCLOSURE) */}
        {selectedEntity && (
          <div
            style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-light)",
              borderRadius: "var(--radius-md)",
              padding: "18px",
              display: "flex",
              flexDirection: "column",
              gap: "14px",
            }}
          >
            {/* Header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", borderBottom: "1px solid var(--border-light)", paddingBottom: "12px" }}>
              <div>
                <div style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.5px", color: "var(--accent-teal)" }}>
                  {selectedEntity.type} Inspection
                </div>
                <div style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", marginTop: "2px" }}>
                  {selectedEntity.entity_id}
                </div>
                <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "1px" }}>
                  {selectedEntity.name}
                </div>
              </div>
              <span
                style={{
                  fontSize: "11px",
                  fontWeight: 600,
                  padding: "2px 8px",
                  borderRadius: "var(--radius-sm)",
                  ...getBadgeStyle(selectedEntity.level),
                }}
              >
                {selectedEntity.level || "Low"} ({Math.round((selectedEntity.probability || 0.05) * 100)}%)
              </span>
            </div>

            {/* Location & Connectivity */}
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "6px" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-muted)" }}>Geography:</span>
                <span>{selectedEntity.city ? `${selectedEntity.city}, ${selectedEntity.country}` : "Multi-zone Route"}</span>
              </div>
              {selectedEntity.single_source !== undefined && (
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Single Source:</span>
                  <strong style={{ color: selectedEntity.single_source ? "var(--risk-medium-text)" : "var(--text-primary)" }}>
                    {selectedEntity.single_source ? "Yes (Sole Vendor)" : "No (Multi-sourced)"}
                  </strong>
                </div>
              )}
              {selectedEntity.lead_time_days !== undefined && (
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Contracted Lead Time:</span>
                  <span>{selectedEntity.lead_time_days} Days</span>
                </div>
              )}
              {selectedEntity.stock_days_cover !== undefined && (
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Safety Stock Cover:</span>
                  <span>{selectedEntity.stock_days_cover} Days</span>
                </div>
              )}
              {selectedEntity.shipping_mode !== undefined && (
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Transport Mode:</span>
                  <span style={{ textTransform: "capitalize" }}>{selectedEntity.shipping_mode}</span>
                </div>
              )}
            </div>

            {/* Diagnostic Signals */}
            <div style={{ backgroundColor: "var(--bg-app)", padding: "10px 12px", borderRadius: "var(--radius-sm)", fontSize: "12px" }}>
              <div style={{ fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                Operational Indicators:
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "4px", color: "var(--text-secondary)" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Rolling 7-Day Delay:</span>
                  <span>{Number(selectedEntity.delay_7d_avg || 0).toFixed(2)} days</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>7-Day Precipitation:</span>
                  <span>{Number(selectedEntity.rain_7d_sum || 0).toFixed(1)} mm</span>
                </div>
                {selectedEntity.news_tone !== undefined && (
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Disruption Sentiment:</span>
                    <span>{Number(selectedEntity.news_tone).toFixed(2)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "4px" }}>
              <button
                onClick={() => onNavigateToFactors && onNavigateToFactors(selectedEntity.entity_id)}
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  fontSize: "12px",
                  fontWeight: 600,
                  color: "var(--accent-teal)",
                  backgroundColor: "var(--accent-teal-subtle)",
                  border: "1px solid var(--accent-teal-border)",
                  borderRadius: "var(--radius-sm)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "6px",
                }}
              >
                <span>View TreeSHAP Feature Drivers</span>
                <ArrowUpRight size={14} />
              </button>

              <button
                onClick={() => onNavigateToRecommendations && onNavigateToRecommendations(selectedEntity.entity_id)}
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  fontSize: "12px",
                  fontWeight: 500,
                  color: "var(--text-secondary)",
                  backgroundColor: "var(--bg-subtle)",
                  border: "1px solid var(--border-light)",
                  borderRadius: "var(--radius-sm)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "6px",
                }}
              >
                <span>View Mitigation Playbook</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
