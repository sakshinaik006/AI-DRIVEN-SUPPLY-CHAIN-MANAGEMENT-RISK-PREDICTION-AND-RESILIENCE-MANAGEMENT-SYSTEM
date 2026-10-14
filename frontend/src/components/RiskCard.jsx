import React from "react";

export function RiskCard({ item }) {
  const getBadgeStyle = (level) => {
    switch (level?.toLowerCase()) {
      case "high":
        return { backgroundColor: "#fee2e2", color: "#b91c1c", border: "1px solid #f87171" };
      case "medium":
        return { backgroundColor: "#fef3c7", color: "#b45309", border: "1px solid #fbbf24" };
      default:
        return { backgroundColor: "#dcfce7", color: "#15803d", border: "1px solid #86efac" };
    }
  };

  const formatTitle = (riskType) => {
    return riskType ? riskType.replace(/_/g, " ").toUpperCase() : "RISK";
  };

  return (
    <div style={{
      border: "1px solid #e2e8f0",
      borderRadius: "8px",
      padding: "16px",
      backgroundColor: "#ffffff",
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
      display: "flex",
      flexDirection: "column",
      gap: "8px"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: "14px", fontWeight: "600", color: "#334155" }}>
          {formatTitle(item.risk_type)}
        </span>
        <span style={{
          padding: "3px 10px",
          borderRadius: "9999px",
          fontSize: "12px",
          fontWeight: "700",
          ...getBadgeStyle(item.level)
        }}>
          {item.level || "Low"}
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "baseline", gap: "6px" }}>
        <span style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a" }}>
          {(item.probability * 100).toFixed(1)}%
        </span>
        <span style={{ fontSize: "12px", color: "#64748b" }}>probability</span>
      </div>

      <div style={{ fontSize: "12px", color: "#64748b", borderTop: "1px solid #f1f5f9", paddingTop: "8px" }}>
        <span>Entity: <strong>{item.entity_id}</strong> ({item.entity_type || "node"})</span>
        <br />
        <span>Date: {item.date}</span>
      </div>
    </div>
  );
}
