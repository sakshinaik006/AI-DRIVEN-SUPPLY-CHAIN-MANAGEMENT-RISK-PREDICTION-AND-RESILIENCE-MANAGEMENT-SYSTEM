import React from "react";
import { 
  Building2, 
  Factory, 
  Warehouse, 
  Truck, 
  AlertTriangle, 
  ShieldCheck, 
  TrendingUp, 
  Clock, 
  Layers,
  ArrowRight
} from "lucide-react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export function OverviewPage({ data, onSelectEntity, onNavigateTab }) {
  if (!data) return <div style={{ color: "#94a3b8" }}>Loading control tower metrics...</div>;

  const {
    prediction_horizon,
    last_data_update,
    overall_health,
    total_suppliers,
    total_plants,
    total_warehouses,
    total_routes,
    overall_network_score,
    high_risk_count,
    medium_risk_count,
    low_risk_count,
    category_summary = {},
    risk_trend = [],
    alerts = [],
    entities = [],
    recommendations = []
  } = data;

  const affectedEntities = entities.filter(e => e.level === "High" || e.level === "Medium");

  const cards = [
    {
      title: "Supplier Failure",
      icon: <Building2 size={20} color="#38bdf8" />,
      info: category_summary["Supplier Risk"] || { level: "Low", affected_count: 0, avg_probability: 0.06 },
      categoryKey: "supplier"
    },
    {
      title: "Manufacturing Delay",
      icon: <Factory size={20} color="#a855f7" />,
      info: category_summary["Manufacturing Risk"] || { level: "Low", affected_count: 0, avg_probability: 0.05 },
      categoryKey: "manufacturing"
    },
    {
      title: "Warehouse Stockout",
      icon: <Warehouse size={20} color="#eab308" />,
      info: category_summary["Warehouse Stockout"] || { level: "Low", affected_count: 0, avg_probability: 0.07 },
      categoryKey: "warehouse"
    },
    {
      title: "Transportation Delay",
      icon: <Truck size={20} color="#3b82f6" />,
      info: category_summary["Transportation Delay"] || { level: "Low", affected_count: 0, avg_probability: 0.06 },
      categoryKey: "transportation"
    }
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* 1. TOP STATS BAR */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
        gap: "14px"
      }}>
        <div style={cardStyle}>
          <div style={labelStyle}>Prediction Horizon</div>
          <div style={{ fontSize: "18px", fontWeight: "700", color: "#38bdf8", display: "flex", alignItems: "center", gap: "6px" }}>
            <Clock size={16} /> {prediction_horizon || "Next 7 Days"}
          </div>
          <div style={subTextStyle}>Updated: {last_data_update || "Recent"}</div>
        </div>

        <div style={cardStyle}>
          <div style={labelStyle}>Overall Health</div>
          <div style={{
            fontSize: "16px",
            fontWeight: "700",
            color: high_risk_count > 0 ? "#ef4444" : (medium_risk_count > 0 ? "#eab308" : "#22c55e"),
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}>
            {high_risk_count > 0 ? <AlertTriangle size={18} /> : <ShieldCheck size={18} />}
            {overall_health || "Stable"}
          </div>
          <div style={subTextStyle}>Network Risk: {Math.round((overall_network_score || 0.06) * 100)}%</div>
        </div>

        <div style={cardStyle}>
          <div style={labelStyle}>Total Physical Assets</div>
          <div style={{ fontSize: "18px", fontWeight: "700", color: "#f8fafc" }}>
            {total_suppliers + total_plants + total_warehouses + total_routes} Entities
          </div>
          <div style={subTextStyle}>
            {total_suppliers} Sup · {total_plants} Plt · {total_warehouses} WH · {total_routes} Routes
          </div>
        </div>

        <div style={cardStyle}>
          <div style={labelStyle}>Network Risk Distribution</div>
          <div style={{ display: "flex", gap: "10px", alignItems: "center", marginTop: "4px" }}>
            <span style={{ fontSize: "14px", fontWeight: "700", color: "#ef4444" }}>{high_risk_count} High</span>
            <span style={{ fontSize: "14px", fontWeight: "700", color: "#eab308" }}>{medium_risk_count} Med</span>
            <span style={{ fontSize: "14px", fontWeight: "700", color: "#22c55e" }}>{low_risk_count} Low</span>
          </div>
          <div style={subTextStyle}>Across 27 Monitored Nodes</div>
        </div>
      </div>

      {/* 2. FOUR RISK SUMMARY CARDS */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "14px" }}>
        {cards.map((c, i) => {
          const isHigh = c.info.level === "High";
          const isMed = c.info.level === "Medium";
          const badgeColor = isHigh ? "#ef4444" : (isMed ? "#eab308" : "#22c55e");
          const bgBadge = isHigh ? "rgba(239, 68, 68, 0.15)" : (isMed ? "rgba(234, 179, 8, 0.15)" : "rgba(34, 197, 94, 0.15)");

          return (
            <div 
              key={i} 
              style={{
                ...cardStyle, 
                borderLeft: `4px solid ${badgeColor}`,
                cursor: "pointer",
                transition: "transform 0.15s ease"
              }}
              onClick={() => onNavigateTab("monitoring", { category: c.categoryKey })}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  {c.icon}
                  <span style={{ fontSize: "13px", fontWeight: "700", color: "#f8fafc" }}>{c.title}</span>
                </div>
                <span style={{
                  fontSize: "11px",
                  fontWeight: "700",
                  padding: "2px 8px",
                  borderRadius: "10px",
                  backgroundColor: bgBadge,
                  color: badgeColor
                }}>
                  {c.info.level} Risk
                </span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
                <div>
                  <div style={{ fontSize: "20px", fontWeight: "800", color: "#f8fafc" }}>
                    {c.info.affected_count} <span style={{ fontSize: "12px", fontWeight: "500", color: "#94a3b8" }}>affected</span>
                  </div>
                  <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "2px" }}>
                    Avg Probability: {Math.round(c.info.avg_probability * 100)}%
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "3px", fontSize: "11px", color: "#38bdf8", fontWeight: "600" }}>
                  Monitor <ArrowRight size={12} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 3. TREND CHART & IMPORTANT ALERTS */}
      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: "16px" }}>
        {/* Trend Chart */}
        <div style={cardStyle}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc", display: "flex", alignItems: "center", gap: "8px" }}>
              <TrendingUp size={16} color="#38bdf8" /> Historical Risk Trend & 7-Day Horizon
            </div>
            <span style={{ fontSize: "11px", color: "#94a3b8" }}>Daily Risk Index</span>
          </div>
          <div style={{ width: "100%", height: "200px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={risk_trend}>
                <defs>
                  <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.6} />
                <XAxis dataKey="day" stroke="#94a3b8" fontSize={10} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} domain={[0, 1]} tickFormatter={(v) => `${Math.round(v * 100)}%`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "6px", color: "#f8fafc", fontSize: "12px" }}
                  formatter={(val) => [`${Math.round(val * 100)}%`, "Network Risk"]}
                />
                <Area type="monotone" dataKey="network_risk" stroke="#38bdf8" strokeWidth={2} fillOpacity={1} fill="url(#riskGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Important Alerts */}
        <div style={{ ...cardStyle, display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
            <AlertTriangle size={16} color="#ef4444" /> Critical Disruption Alerts ({alerts.length})
          </div>
          <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "8px", maxHeight: "200px" }}>
            {alerts.length === 0 ? (
              <div style={{ color: "#22c55e", fontSize: "12px", padding: "16px 0", textAlign: "center" }}>
                ✓ Zero critical disruption alerts detected under this scenario.
              </div>
            ) : (
              alerts.map((alt, i) => (
                <div key={i} style={{
                  padding: "8px 12px",
                  borderRadius: "6px",
                  backgroundColor: alt.severity === "High" ? "rgba(239, 68, 68, 0.12)" : "rgba(234, 179, 8, 0.12)",
                  borderLeft: `3px solid ${alt.severity === "High" ? "#ef4444" : "#eab308"}`,
                  fontSize: "12px",
                  color: "#f8fafc"
                }}>
                  {alt.message}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* 4. AFFECTED ENTITIES TABLE & TOP RECOMMENDATIONS */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "16px" }}>
        {/* Affected Entities Table */}
        <div style={cardStyle}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
              Active Risk Pipeline ({affectedEntities.length} Entities Breaching Threshold)
            </div>
            <span style={{ fontSize: "11px", color: "#94a3b8" }}>Sorted by Severity</span>
          </div>
          <div style={{ overflowX: "auto", maxHeight: "220px" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", textAlign: "left" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid #334155", color: "#94a3b8" }}>
                  <th style={{ padding: "6px 8px" }}>Entity</th>
                  <th style={{ padding: "6px 8px" }}>Category</th>
                  <th style={{ padding: "6px 8px" }}>Risk Level</th>
                  <th style={{ padding: "6px 8px" }}>Probability</th>
                  <th style={{ padding: "6px 8px" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {affectedEntities.length === 0 ? (
                  <tr>
                    <td colSpan={5} style={{ padding: "16px", textAlign: "center", color: "#22c55e" }}>
                      All 27 entities are operating safely within baseline tolerances.
                    </td>
                  </tr>
                ) : (
                  affectedEntities.map((e, idx) => (
                    <tr key={idx} style={{ borderBottom: "1px solid #1e293b" }}>
                      <td style={{ padding: "6px 8px", fontWeight: "600", color: "#f8fafc" }}>
                        {e.entity_id} <span style={{ fontSize: "11px", color: "#94a3b8", fontWeight: "400" }}>({e.city})</span>
                      </td>
                      <td style={{ padding: "6px 8px", color: "#cbd5e1" }}>{e.category}</td>
                      <td style={{ padding: "6px 8px" }}>
                        <span style={{
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontSize: "10px",
                          fontWeight: "700",
                          backgroundColor: e.level === "High" ? "rgba(239,68,68,0.2)" : "rgba(234,179,8,0.2)",
                          color: e.level === "High" ? "#ef4444" : "#eab308"
                        }}>
                          {e.level}
                        </span>
                      </td>
                      <td style={{ padding: "6px 8px", fontWeight: "700", color: e.level === "High" ? "#ef4444" : "#eab308" }}>
                        {Math.round(e.probability * 100)}%
                      </td>
                      <td style={{ padding: "6px 8px" }}>
                        <button
                          onClick={() => {
                            onSelectEntity(e.entity_id);
                            onNavigateTab("insights");
                          }}
                          style={{
                            backgroundColor: "#1e293b",
                            border: "1px solid #38bdf8",
                            color: "#38bdf8",
                            borderRadius: "4px",
                            padding: "2px 8px",
                            fontSize: "10px",
                            fontWeight: "600",
                            cursor: "pointer"
                          }}
                        >
                          Inspect AI
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Recommendations Requiring Attention */}
        <div style={cardStyle}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
              Top Prescriptive Actions ({recommendations.length})
            </div>
            <button 
              onClick={() => onNavigateTab("recommendations")}
              style={{ background: "none", border: "none", color: "#38bdf8", fontSize: "11px", fontWeight: "600", cursor: "pointer", display: "flex", alignItems: "center", gap: "2px" }}
            >
              View All <ArrowRight size={12} />
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", maxHeight: "220px", overflowY: "auto" }}>
            {recommendations.length === 0 ? (
              <div style={{ color: "#22c55e", fontSize: "12px", padding: "16px 0", textAlign: "center" }}>
                ✓ No emergency resilience intervention or volume reallocation required.
              </div>
            ) : (
              recommendations.slice(0, 4).map((rec, idx) => (
                <div key={idx} style={{
                  padding: "10px",
                  borderRadius: "6px",
                  backgroundColor: "#0f172a",
                  border: "1px solid #334155"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                    <span style={{ fontSize: "11px", fontWeight: "700", color: "#38bdf8" }}>{rec.entity_id} · {rec.category}</span>
                    <span style={{
                      fontSize: "9px",
                      fontWeight: "700",
                      padding: "1px 6px",
                      borderRadius: "4px",
                      backgroundColor: rec.priority === "Critical" ? "#ef4444" : "#eab308",
                      color: "#ffffff"
                    }}>
                      {rec.priority}
                    </span>
                  </div>
                  <div style={{ fontSize: "12px", color: "#f8fafc", fontWeight: "500", marginBottom: "4px" }}>
                    {rec.action}
                  </div>
                  <div style={{ fontSize: "10px", color: "#22c55e", fontWeight: "600" }}>
                    {rec.mitigation_effect}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const cardStyle = {
  backgroundColor: "#1e293b",
  borderRadius: "8px",
  padding: "14px 16px",
  border: "1px solid #334155",
  boxShadow: "0 2px 4px rgba(0, 0, 0, 0.2)"
};

const labelStyle = {
  fontSize: "11px",
  fontWeight: "600",
  color: "#94a3b8",
  textTransform: "uppercase",
  letterSpacing: "0.5px",
  marginBottom: "4px"
};

const subTextStyle = {
  fontSize: "11px",
  color: "#64748b",
  marginTop: "4px"
};
