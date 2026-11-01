import React, { useState } from "react";
import { 
  Building2, 
  Factory, 
  Warehouse, 
  Truck, 
  ChevronRight, 
  ShieldCheck, 
  AlertTriangle,
  Compass,
  ArrowRight
} from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export function RiskMonitoringPage({ data, initialCategory = "supplier", onSelectEntity, onNavigateTab }) {
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const [selectedEntityId, setSelectedEntityId] = useState(null);

  if (!data) return <div style={{ color: "#94a3b8" }}>Loading risk monitoring data...</div>;

  const entities = data.entities || [];

  const categoryMap = {
    supplier: {
      title: "Supplier Risk",
      icon: <Building2 size={18} />,
      type: "supplier",
      entities: entities.filter(e => e.type === "supplier")
    },
    manufacturing: {
      title: "Manufacturing Risk",
      icon: <Factory size={18} />,
      type: "plant",
      entities: entities.filter(e => e.type === "plant")
    },
    warehouse: {
      title: "Warehouse Risk",
      icon: <Warehouse size={18} />,
      type: "warehouse",
      entities: entities.filter(e => e.type === "warehouse")
    },
    transportation: {
      title: "Transportation Risk",
      icon: <Truck size={18} />,
      type: "route",
      entities: entities.filter(e => e.type === "route")
    }
  };

  const currentCategory = categoryMap[selectedCategory] || categoryMap.supplier;
  const currentEntities = currentCategory.entities;
  const activeEntity = currentEntities.find(e => e.entity_id === selectedEntityId) || currentEntities[0];

  const chartData = currentEntities.map(e => ({
    name: e.entity_id,
    probability: Math.round(e.probability * 100),
    level: e.level
  }));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      {/* 1. CATEGORY SELECTOR TABS */}
      <div style={{ display: "flex", gap: "10px", borderBottom: "1px solid #334155", paddingBottom: "10px" }}>
        {Object.entries(categoryMap).map(([key, item]) => {
          const isActive = selectedCategory === key;
          const highCount = item.entities.filter(e => e.level === "High").length;
          return (
            <button
              key={key}
              onClick={() => {
                setSelectedCategory(key);
                setSelectedEntityId(null);
              }}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "8px 16px",
                borderRadius: "6px",
                border: "none",
                backgroundColor: isActive ? "#0284c7" : "#1e293b",
                color: isActive ? "#ffffff" : "#94a3b8",
                fontWeight: "700",
                fontSize: "13px",
                cursor: "pointer",
                transition: "all 0.15s ease"
              }}
            >
              {item.icon}
              {item.title}
              {highCount > 0 && (
                <span style={{
                  backgroundColor: "#ef4444",
                  color: "#ffffff",
                  fontSize: "10px",
                  fontWeight: "800",
                  padding: "1px 6px",
                  borderRadius: "10px"
                }}>
                  {highCount}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* 2. CATEGORY COMPARISON CHART & SUMMARY */}
      <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: "16px" }}>
        {/* Risk Probability Comparison Chart */}
        <div style={cardStyle}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
              {currentCategory.title} Comparison (Failure Probability %)
            </div>
            <span style={{ fontSize: "11px", color: "#94a3b8" }}>{currentEntities.length} Monitored Entities</span>
          </div>
          <div style={{ width: "100%", height: "180px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "6px", color: "#f8fafc", fontSize: "12px" }}
                  formatter={(val) => [`${val}%`, "Risk Probability"]}
                />
                <Bar 
                  dataKey="probability" 
                  fill="#38bdf8" 
                  radius={[4, 4, 0, 0]}
                  onClick={(entry) => setSelectedEntityId(entry.name)}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Key Metrics Summary */}
        <div style={cardStyle}>
          <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc", marginBottom: "12px" }}>
            Operational Health Summary
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <div style={summaryRowStyle}>
              <span style={{ color: "#94a3b8" }}>Total Entities Monitored</span>
              <span style={{ fontWeight: "700", color: "#f8fafc" }}>{currentEntities.length}</span>
            </div>
            <div style={summaryRowStyle}>
              <span style={{ color: "#94a3b8" }}>High Risk Breaches</span>
              <span style={{ fontWeight: "700", color: "#ef4444" }}>
                {currentEntities.filter(e => e.level === "High").length}
              </span>
            </div>
            <div style={summaryRowStyle}>
              <span style={{ color: "#94a3b8" }}>Medium / Guarded Risk</span>
              <span style={{ fontWeight: "700", color: "#eab308" }}>
                {currentEntities.filter(e => e.level === "Medium").length}
              </span>
            </div>
            <div style={summaryRowStyle}>
              <span style={{ color: "#94a3b8" }}>Safe Operating Limit</span>
              <span style={{ fontWeight: "700", color: "#22c55e" }}>
                {currentEntities.filter(e => e.level === "Low").length}
              </span>
            </div>
            <div style={summaryRowStyle}>
              <span style={{ color: "#94a3b8" }}>Peak Failure Risk</span>
              <span style={{ fontWeight: "700", color: "#f8fafc" }}>
                {Math.max(...currentEntities.map(e => Math.round(e.probability * 100)))}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. ENTITY SELECTION GRID & INDIVIDUAL DETAILS */}
      <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1.3fr", gap: "16px" }}>
        {/* Entity List */}
        <div style={cardStyle}>
          <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc", marginBottom: "10px" }}>
            Select Entity to Inspect
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "6px", maxHeight: "320px", overflowY: "auto" }}>
            {currentEntities.map((e) => {
              const isSelected = activeEntity?.entity_id === e.entity_id;
              const isHigh = e.level === "High";
              const isMed = e.level === "Medium";
              return (
                <div
                  key={e.entity_id}
                  onClick={() => setSelectedEntityId(e.entity_id)}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "10px 12px",
                    borderRadius: "6px",
                    cursor: "pointer",
                    backgroundColor: isSelected ? "#0284c7" : "#0f172a",
                    border: isSelected ? "1px solid #38bdf8" : "1px solid #334155",
                    transition: "background-color 0.12s ease"
                  }}
                >
                  <div>
                    <div style={{ fontSize: "13px", fontWeight: "700", color: "#f8fafc" }}>
                      {e.entity_id} · <span style={{ fontSize: "11px", color: isSelected ? "#e0f2fe" : "#94a3b8", fontWeight: "400" }}>{e.name}</span>
                    </div>
                    <div style={{ fontSize: "11px", color: isSelected ? "#e0f2fe" : "#64748b" }}>
                      {e.city}, {e.country}
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span style={{
                      fontSize: "11px",
                      fontWeight: "700",
                      padding: "2px 8px",
                      borderRadius: "6px",
                      backgroundColor: isHigh ? "#ef4444" : (isMed ? "#eab308" : "#22c55e"),
                      color: "#ffffff"
                    }}>
                      {Math.round(e.probability * 100)}%
                    </span>
                    <ChevronRight size={14} color={isSelected ? "#ffffff" : "#64748b"} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Individual Entity Detail Panel */}
        {activeEntity && (
          <div style={{ ...cardStyle, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "14px" }}>
                <div>
                  <div style={{ fontSize: "16px", fontWeight: "800", color: "#f8fafc" }}>
                    {activeEntity.name} ({activeEntity.entity_id})
                  </div>
                  <div style={{ fontSize: "12px", color: "#94a3b8", marginTop: "2px" }}>
                    {activeEntity.city}, {activeEntity.country} · Category: {activeEntity.category}
                  </div>
                </div>
                <div style={{
                  padding: "4px 12px",
                  borderRadius: "6px",
                  fontSize: "12px",
                  fontWeight: "800",
                  backgroundColor: activeEntity.level === "High" ? "rgba(239, 68, 68, 0.2)" : (activeEntity.level === "Medium" ? "rgba(234, 179, 8, 0.2)" : "rgba(34, 197, 94, 0.2)"),
                  color: activeEntity.level === "High" ? "#ef4444" : (activeEntity.level === "Medium" ? "#eab308" : "#22c55e"),
                  border: `1px solid ${activeEntity.level === "High" ? "#ef4444" : (activeEntity.level === "Medium" ? "#eab308" : "#22c55e")}`
                }}>
                  {activeEntity.level} Risk ({Math.round(activeEntity.probability * 100)}%)
                </div>
              </div>

              {/* Specific Category Indicators */}
              <div style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "12px",
                backgroundColor: "#0f172a",
                padding: "14px",
                borderRadius: "6px",
                border: "1px solid #334155",
                marginBottom: "14px"
              }}>
                {activeEntity.type === "supplier" && (
                  <>
                    <div>
                      <div style={labelStyle}>Reliability Score</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: "#38bdf8" }}>
                        {activeEntity.reliability_score || 0.95} / 1.00
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Base Lead Time</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
                        {activeEntity.lead_time_days || 3} Days
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Rolling 7-Day Delay</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: activeEntity.delay_7d_avg > 1 ? "#ef4444" : "#22c55e" }}>
                        {activeEntity.delay_7d_avg || 0.0} Days
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Single Source Dependency</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: activeEntity.single_source ? "#eab308" : "#22c55e" }}>
                        {activeEntity.single_source ? "Yes (Sole Source)" : "No (Multi-sourced)"}
                      </div>
                    </div>
                  </>
                )}

                {activeEntity.type === "plant" && (
                  <>
                    <div>
                      <div style={labelStyle}>Planned Daily Capacity</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
                        {activeEntity.capacity_planned} Units/Day
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Actual Production Output</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: activeEntity.production_ratio < 0.8 ? "#ef4444" : "#22c55e" }}>
                        {activeEntity.actual_output} Units ({Math.round(activeEntity.production_ratio * 100)}%)
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Assembly Delay Index</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: activeEntity.delay_7d_avg > 0 ? "#ef4444" : "#22c55e" }}>
                        {activeEntity.delay_7d_avg} Days
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Production Status</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: activeEntity.level === "High" ? "#ef4444" : "#22c55e" }}>
                        {activeEntity.level === "High" ? "Assembly Starvation" : "Optimal Throughput"}
                      </div>
                    </div>
                  </>
                )}

                {activeEntity.type === "warehouse" && (
                  <>
                    <div>
                      <div style={labelStyle}>Current Inventory Level</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
                        {activeEntity.inventory_level} Units
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Safety Stock Target</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: "#38bdf8" }}>
                        {activeEntity.safety_stock} Units
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Days of Supply Coverage</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: activeEntity.stock_days_cover < 5 ? "#ef4444" : "#22c55e" }}>
                        {activeEntity.stock_days_cover} Days
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>7-Day Avg Daily Demand</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
                        {activeEntity.demand_7d_avg} Units/Day
                      </div>
                    </div>
                  </>
                )}

                {activeEntity.type === "route" && (
                  <>
                    <div>
                      <div style={labelStyle}>Corridor Type & Mode</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: "#38bdf8", textTransform: "capitalize" }}>
                        {activeEntity.route_type} ({activeEntity.shipping_mode})
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Distance / Scheduled Days</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
                        {activeEntity.distance_km} km ({activeEntity.scheduled_days} Days)
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Rolling Transit Delay</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: activeEntity.delay_7d_avg > 0 ? "#ef4444" : "#22c55e" }}>
                        {activeEntity.delay_7d_avg} Days
                      </div>
                    </div>
                    <div>
                      <div style={labelStyle}>Port Climate Alert</div>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: activeEntity.rain_7d_sum > 20 ? "#ef4444" : "#22c55e" }}>
                        {activeEntity.rain_7d_sum > 20 ? "Severe Storm Alert" : "Normal Conditions"}
                      </div>
                    </div>
                  </>
                )}
              </div>

              {/* Connected Dependencies */}
              <div style={{ fontSize: "12px", color: "#94a3b8", marginBottom: "8px" }}>
                Connected Topology: <span style={{ color: "#f8fafc", fontWeight: "600" }}>{activeEntity.connected_entities?.join(", ") || "None"}</span>
              </div>
            </div>

            {/* Quick Actions Footer */}
            <div style={{ display: "flex", gap: "10px", marginTop: "12px" }}>
              <button
                onClick={() => {
                  onSelectEntity(activeEntity.entity_id);
                  onNavigateTab("insights");
                }}
                style={{
                  flex: 1,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "6px",
                  padding: "8px 14px",
                  borderRadius: "6px",
                  backgroundColor: "#0284c7",
                  color: "#ffffff",
                  fontWeight: "700",
                  fontSize: "12px",
                  border: "none",
                  cursor: "pointer"
                }}
              >
                Explain with AI Insights <ArrowRight size={14} />
              </button>
              <button
                onClick={() => {
                  onSelectEntity(activeEntity.entity_id);
                  onNavigateTab("map");
                }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "8px 14px",
                  borderRadius: "6px",
                  backgroundColor: "#1e293b",
                  border: "1px solid #38bdf8",
                  color: "#38bdf8",
                  fontWeight: "700",
                  fontSize: "12px",
                  cursor: "pointer"
                }}
              >
                View on Map
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const cardStyle = {
  backgroundColor: "#1e293b",
  borderRadius: "8px",
  padding: "16px",
  border: "1px solid #334155"
};

const summaryRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "6px 0",
  borderBottom: "1px solid #0f172a",
  fontSize: "12px"
};

const labelStyle = {
  fontSize: "10px",
  fontWeight: "700",
  color: "#94a3b8",
  textTransform: "uppercase",
  marginBottom: "3px"
};
