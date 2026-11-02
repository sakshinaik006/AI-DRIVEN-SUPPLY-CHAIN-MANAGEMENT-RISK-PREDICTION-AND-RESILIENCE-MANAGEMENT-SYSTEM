import React, { useState, useMemo } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";
import { Info, ShieldCheck, Clock, Layers, AlertTriangle } from "lucide-react";

export function RiskFactorsResilience({
  scenarioData,
  selectedEntityId: initialEntityId = null,
  onNavigateToRecommendations,
}) {
  const [selectedCategory, setSelectedCategory] = useState("all");

  // Verified TreeSHAP feature importance extracted directly from outputs/shap_summary.csv
  const shapDataByCategory = useMemo(() => {
    return {
      supplier: [
        { feature: "Adverse News Sentiment (14d)", rawName: "news_tone_14d_trend", importance: 0.2048, impact: "Negative media tone and localized geopolitical/labor dispatch friction" },
        { feature: "Rolling Delivery Delay (7d)", rawName: "supplier_delay_7d_avg", importance: 0.197, impact: "Historical delivery tardiness directly elevates conditional failure odds" },
        { feature: "Severe Rainfall Sum (7d)", rawName: "rain_7d_sum", importance: 0.1854, impact: "Precipitation exceeding seasonal norms impacts component dispatch & logistics" },
        { feature: "Single Source Dependency", rawName: "single_source_flag", importance: 0.1463, impact: "Absence of a secondary qualified vendor prevents volume reallocation" },
      ],
      manufacturing: [
        { feature: "Local Precipitation (7d)", rawName: "rain_7d_sum", importance: 0.2774, impact: "Extreme weather causing localized worker transit and utility interruption" },
        { feature: "Component Delivery Lag (7d)", rawName: "delivery_delay_7d_avg", importance: 0.2203, impact: "Late component arrivals directly constrain assembly line schedules" },
        { feature: "Upstream Supplier Risk (OOF)", rawName: "supplier_failure_prob_oof", importance: 0.0995, impact: "Cascading upstream supplier failure probability propagating to plant" },
        { feature: "Production Ratio Deficit (7d)", rawName: "production_ratio_7d_avg", importance: 0.0916, impact: "Historical shortfall below 98% nominal assembly line throughput" },
      ],
      warehouse: [
        { feature: "Rolling Customer Demand (7d)", rawName: "demand_7d_avg", importance: 0.1412, impact: "Elevated consumer order velocity outpacing standard replenishment cycles" },
        { feature: "Upstream Plant Delay (OOF)", rawName: "mfg_delay_prob_oof", importance: 0.1144, impact: "Manufacturing output deficits starving warehouse replenishment orders" },
        { feature: "On-Hand Inventory Level", rawName: "inventory_level", importance: 0.0878, impact: "Current physical units available compared to safety stock baseline" },
        { feature: "Stock Days of Cover", rawName: "stock_days_cover", importance: 0.0855, impact: "Ratio of current stock to daily burn rate; <14 days triggers warning" },
      ],
      transport: [
        { feature: "Coastal Route Precipitation", rawName: "rain_7d_sum", importance: 0.3836, impact: "Monsoon and maritime storm activity along port and transit corridors" },
        { feature: "Port News Tone (14d)", rawName: "port_news_tone_14d", importance: 0.1614, impact: "Harbor congestion dispatches, container dwell delays, and customs news" },
        { feature: "Corridor Distance (km)", rawName: "distance_km", importance: 0.1237, impact: "Longer transit legs inherently accumulate greater transit variance" },
        { feature: "Shipping Mode (Air/Sea/Road)", rawName: "shipping_mode", importance: 0.0725, impact: "Sea freight exhibits higher variance compared to dedicated air express" },
        { feature: "Historical Transit Delay", rawName: "delivery_delay_7d_avg", importance: 0.0071, impact: "Recent historical delay along this specific corridor" },
      ],
    };
  }, []);

  // Display data based on category filter
  const displayedFeatures = useMemo(() => {
    if (selectedCategory !== "all") {
      return shapDataByCategory[selectedCategory] || [];
    }
    // Aggregate top 6 across all categories
    const all = [
      ...shapDataByCategory.supplier,
      ...shapDataByCategory.manufacturing,
      ...shapDataByCategory.warehouse,
      ...shapDataByCategory.transport,
    ];
    // Deduplicate by feature name keeping highest
    const map = new Map();
    for (const item of all) {
      if (!map.has(item.feature) || map.get(item.feature).importance < item.importance) {
        map.set(item.feature, item);
      }
    }
    return Array.from(map.values())
      .sort((a, b) => b.importance - a.importance)
      .slice(0, 7);
  }, [selectedCategory, shapDataByCategory]);

  const categoryOptions = [
    { id: "all", label: "Network-Wide (Top Drivers)" },
    { id: "supplier", label: "Supplier Failure" },
    { id: "manufacturing", label: "Manufacturing Delay" },
    { id: "warehouse", label: "Warehouse Stockout" },
    { id: "transport", label: "Transport Disruption" },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "22px" }}>
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
            Risk Factors & Resilience Indicators
          </h1>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "2px" }}>
            TreeSHAP root-cause attributions and supported operational resilience parameters
          </p>
        </div>

        {/* Category Filter */}
        <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
          {categoryOptions.map((opt) => {
            const isActive = selectedCategory === opt.id;
            return (
              <button
                key={opt.id}
                onClick={() => setSelectedCategory(opt.id)}
                style={{
                  padding: "5px 12px",
                  fontSize: "12px",
                  fontWeight: isActive ? 600 : 500,
                  borderRadius: "var(--radius-sm)",
                  border: isActive ? "1px solid var(--accent-teal)" : "1px solid var(--border-light)",
                  backgroundColor: isActive ? "var(--accent-teal)" : "var(--bg-surface)",
                  color: isActive ? "#ffffff" : "var(--text-secondary)",
                }}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. TREESHAP FEATURE IMPORTANCE CHART */}
      <div
        style={{
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-light)",
          borderRadius: "var(--radius-md)",
          padding: "18px 20px",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
          <div>
            <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
              Mean Absolute TreeSHAP Feature Attributions
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
              Quantifies relative contribution of each operational feature to predicted log-odds across all 5,778 instances
            </div>
          </div>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", backgroundColor: "var(--bg-subtle)", padding: "2px 8px", borderRadius: "var(--radius-sm)" }}>
            TreeExplainer (CatBoost)
          </span>
        </div>

        <div style={{ height: "260px", width: "100%" }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={displayedFeatures}
              margin={{ top: 10, right: 30, left: 160, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
              <XAxis
                type="number"
                domain={[0, 0.45]}
                tick={{ fontSize: 11, fill: "#64748b" }}
                tickFormatter={(v) => v.toFixed(2)}
                axisLine={{ stroke: "#cbd5e1" }}
              />
              <YAxis
                type="category"
                dataKey="feature"
                tick={{ fontSize: 12, fill: "#1e293b", fontWeight: 500 }}
                axisLine={{ stroke: "#cbd5e1" }}
                width={150}
              />
              <Tooltip
                formatter={(val) => [`SHAP: ${Number(val).toFixed(4)}`, "Mean Impact"]}
                contentStyle={{
                  backgroundColor: "var(--bg-surface)",
                  borderColor: "var(--border-light)",
                  borderRadius: "var(--radius-sm)",
                  fontSize: "12px",
                }}
              />
              <Bar dataKey="importance" fill="#0f766e" radius={[0, 4, 4, 0]}>
                {displayedFeatures.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={index === 0 ? "#0f766e" : "#14b8a6"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. CONTRIBUTING FACTOR EXPLANATIONS */}
      <div
        style={{
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-light)",
          borderRadius: "var(--radius-md)",
          padding: "18px 20px",
        }}
      >
        <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "12px" }}>
          Factor Interpretations & Physical Drivers
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: "12px",
          }}
        >
          {displayedFeatures.slice(0, 4).map((f, i) => (
            <div
              key={i}
              style={{
                padding: "12px 14px",
                backgroundColor: "var(--bg-app)",
                border: "1px solid var(--border-light)",
                borderRadius: "var(--radius-sm)",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
                  {f.feature}
                </span>
                <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--accent-teal)" }}>
                  {f.importance.toFixed(3)}
                </span>
              </div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px" }}>
                {f.impact}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. SUPPORTED RESILIENCE INDICATORS */}
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
              Supported Resilience Capabilities
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
              Empirical network parameters governing absorption and recovery across multi-tier entities
            </div>
          </div>
          <div
            style={{
              fontSize: "11px",
              color: "var(--text-secondary)",
              backgroundColor: "var(--bg-app)",
              border: "1px solid var(--border-light)",
              padding: "3px 8px",
              borderRadius: "var(--radius-sm)",
            }}
          >
            Verified Parameters Only
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "14px",
          }}
        >
          {/* Indicator 1: Alternative Supplier Availability */}
          <div
            style={{
              padding: "14px",
              border: "1px solid var(--border-light)",
              borderRadius: "var(--radius-sm)",
              backgroundColor: "var(--bg-app)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-primary)", fontWeight: 600, fontSize: "13px" }}>
              <ShieldCheck size={16} color="var(--accent-teal)" />
              <span>Vendor Redundancy</span>
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "8px" }}>
              • <strong>6 of 8 Suppliers</strong> have pre-qualified secondary tier vendors.
              <br />
              • <strong>2 Sole-Source Suppliers</strong> (SUP001 Hsinchu AP, SUP003 Icheon Memory) require direct executive safety-stock escalation.
            </div>
          </div>

          {/* Indicator 2: Inventory Days of Cover */}
          <div
            style={{
              padding: "14px",
              border: "1px solid var(--border-light)",
              borderRadius: "var(--radius-sm)",
              backgroundColor: "var(--bg-app)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-primary)", fontWeight: 600, fontSize: "13px" }}>
              <Layers size={16} color="var(--accent-teal)" />
              <span>Inventory Buffer Cover</span>
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "8px" }}>
              • <strong>Regional Warehouses:</strong> 16 to 24 days average stock cover.
              <br />
              • <strong>Threshold Policy:</strong> Buffer drops below 14 days trigger automatic inter-warehouse cross-dock rebalancing.
            </div>
          </div>

          {/* Indicator 3: Recovery Time Window (MTTR) */}
          <div
            style={{
              padding: "14px",
              border: "1px solid var(--border-light)",
              borderRadius: "var(--radius-sm)",
              backgroundColor: "var(--bg-app)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-primary)", fontWeight: 600, fontSize: "13px" }}>
              <Clock size={16} color="var(--accent-teal)" />
              <span>Recovery Time Bounds</span>
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "8px" }}>
              • <strong>Air Corridor Reroute:</strong> 24 to 48 hours.
              <br />
              • <strong>Secondary Vendor Failover:</strong> 5 to 7 calendar days.
              <br />
              • <strong>Assembly Line Lot Resequence:</strong> 12 to 24 hours.
            </div>
          </div>

          {/* Indicator 4: Disruption History */}
          <div
            style={{
              padding: "14px",
              border: "1px solid var(--border-light)",
              borderRadius: "var(--radius-sm)",
              backgroundColor: "var(--bg-app)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-primary)", fontWeight: 600, fontSize: "13px" }}>
              <AlertTriangle size={16} color="var(--accent-teal)" />
              <span>Disruption Exposure</span>
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "8px" }}>
              • <strong>Coastal Typhoon Exposure:</strong> RT001, RT002 maritime lanes.
              <br />
              • <strong>Historical Delivery Variance:</strong> Measured rolling 7-day delays range from 0.0 to 1.86 days across network nodes.
            </div>
          </div>
        </div>

        {/* Explicit Disclosure Footnote */}
        <div
          style={{
            marginTop: "14px",
            paddingTop: "10px",
            borderTop: "1px solid var(--border-light)",
            fontSize: "11px",
            color: "var(--text-muted)",
            display: "flex",
            alignItems: "center",
            gap: "6px",
          }}
        >
          <Info size={13} color="var(--text-muted)" />
          <span>
            Resilience parameters reflect empirical network structure, inventory coverage, and contracted vendor lead times. No speculative or unsupported composite resilience scores are displayed.
          </span>
        </div>
      </div>
    </div>
  );
}
