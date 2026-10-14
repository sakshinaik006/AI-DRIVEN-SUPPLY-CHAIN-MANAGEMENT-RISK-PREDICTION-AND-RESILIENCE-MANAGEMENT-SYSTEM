import React, { useState, useEffect } from "react";

export function NewsPanel({ newsItems }) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    if (newsItems && newsItems.length > 0) {
      setItems(newsItems);
    } else {
      // Default / fallback to demo headlines
      setItems([
        {
          headline: "Critical wafer and component shortage disrupts technology supply chain near Hsinchu",
          linked_node: "SUP001",
          entity_name: "Hsinchu Silicon Works (Taiwan)",
          disruption_type: "shortage",
          risk_score: 0.798,
          risk_level: "HIGH",
          tone: -6.42,
        },
        {
          headline: "Transformer failure causes extended power cut at major production cluster in Shenzhen",
          linked_node: "PLT004",
          entity_name: "Shenzhen Phone Plant (China)",
          disruption_type: "power_cut",
          risk_score: 0.783,
          risk_level: "HIGH",
          tone: -5.88,
        },
        {
          headline: "Component shortages force assembly delays at high-volume plants in Chennai",
          linked_node: "WH001",
          entity_name: "Mumbai Distribution Centre (India)",
          disruption_type: "shortage",
          risk_score: 0.767,
          risk_level: "HIGH",
          tone: -4.95,
        },
        {
          headline: "Massive container vessel backlog causes acute port congestion near Ningbo",
          linked_node: "RT001",
          entity_name: "Ningbo Maritime Freight Lane",
          disruption_type: "port_congestion",
          risk_score: 0.754,
          risk_level: "HIGH",
          tone: -7.15,
        },
        {
          headline: "Logistics operators in Rotterdam report steady cargo volumes and stable schedules",
          linked_node: "WH002",
          entity_name: "Rotterdam Distribution Centre (Netherlands)",
          disruption_type: "general_business",
          risk_score: 0.122,
          risk_level: "LOW",
          tone: 2.15,
        },
      ]);
    }
  }, [newsItems]);

  const getBadgeColor = (level) => {
    switch (level) {
      case "HIGH":
        return { bg: "#fef2f2", text: "#b91c1c", border: "#fecaca" };
      case "MEDIUM":
        return { bg: "#fffbeb", text: "#b45309", border: "#fde68a" };
      default:
        return { bg: "#f0fdf4", text: "#15803d", border: "#bbf7d0" };
    }
  };

  return (
    <div style={{
      backgroundColor: "#ffffff",
      padding: "20px",
      borderRadius: "8px",
      border: "1px solid #e2e8f0",
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
      marginTop: "24px",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px", flexWrap: "wrap", gap: "8px" }}>
        <div>
          <h3 style={{ margin: "0 0 4px 0", fontSize: "16px", color: "#1e293b", display: "flex", alignItems: "center", gap: "8px" }}>
            <span>Global News Disruption Intelligence</span>
            <span style={{ fontSize: "11px", backgroundColor: "#eff6ff", color: "#2563eb", padding: "2px 8px", borderRadius: "12px", border: "1px solid #bfdbfe" }}>
              DeBERTa-v3 + spaCy NER
            </span>
          </h3>
          <p style={{ margin: 0, fontSize: "13px", color: "#64748b" }}>
            Real-time supply chain disruption detection linked to network nodes by geographic entity recognition.
          </p>
        </div>
        <span style={{ fontSize: "12px", color: "#64748b" }}>
          Showing <strong>{items.length}</strong> active alerts
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {items.map((item, idx) => {
          const colors = getBadgeColor(item.risk_level);
          return (
            <div
              key={idx}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "12px 14px",
                borderRadius: "6px",
                border: "1px solid #f1f5f9",
                backgroundColor: idx % 2 === 0 ? "#f8fafc" : "#ffffff",
                flexWrap: "wrap",
                gap: "10px",
              }}
            >
              <div style={{ flex: "1 1 500px" }}>
                <div style={{ fontSize: "14px", fontWeight: "600", color: "#1e293b", marginBottom: "4px" }}>
                  {item.headline}
                </div>
                <div style={{ fontSize: "12px", color: "#64748b", display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
                  <span>
                    Linked Node: <strong style={{ color: "#334155" }}>{item.linked_node}</strong> ({item.entity_name})
                  </span>
                  <span>
                    Type: <strong style={{ textTransform: "capitalize", color: "#475569" }}>{item.disruption_type?.replace("_", " ")}</strong>
                  </span>
                  <span>
                    Tone: <strong style={{ color: item.tone < 0 ? "#dc2626" : "#16a34a" }}>{item.tone > 0 ? `+${item.tone}` : item.tone}</strong>
                  </span>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "11px", color: "#64748b" }}>Text Risk</div>
                  <div style={{ fontSize: "14px", fontWeight: "700", color: colors.text }}>
                    {(item.risk_score * 100).toFixed(1)}%
                  </div>
                </div>
                <span
                  style={{
                    fontSize: "11px",
                    fontWeight: "700",
                    padding: "4px 10px",
                    borderRadius: "4px",
                    backgroundColor: colors.bg,
                    color: colors.text,
                    border: `1px solid ${colors.border}`,
                    letterSpacing: "0.5px",
                  }}
                >
                  {item.risk_level}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default NewsPanel;
