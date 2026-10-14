import React from "react";

export function NetworkScore({ score, level, weights }) {
  const getBadgeStyle = (lvl) => {
    switch (lvl?.toLowerCase()) {
      case "high":
        return { backgroundColor: "#fee2e2", color: "#b91c1c" };
      case "medium":
        return { backgroundColor: "#fef3c7", color: "#b45309" };
      default:
        return { backgroundColor: "#dcfce7", color: "#15803d" };
    }
  };

  return (
    <div style={{
      border: "1px solid #e2e8f0",
      borderRadius: "8px",
      padding: "20px",
      backgroundColor: "#ffffff",
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>Composite Network Risk Score</h3>
        <span style={{
          padding: "4px 12px",
          borderRadius: "9999px",
          fontWeight: "700",
          fontSize: "13px",
          ...getBadgeStyle(level)
        }}>
          {level || "Medium"}
        </span>
      </div>

      <div style={{ marginTop: "12px", display: "flex", alignItems: "baseline", gap: "8px" }}>
        <span style={{ fontSize: "36px", fontWeight: "800", color: "#0f172a" }}>
          {typeof score === "number" ? (score * 100).toFixed(1) : "42.0"}%
        </span>
        <span style={{ fontSize: "14px", color: "#64748b" }}>overall system risk index</span>
      </div>

      <p style={{ fontSize: "12px", color: "#64748b", margin: "8px 0 12px 0" }}>
        Formula (Assumption): <em>0.25 × Supplier + 0.25 × Manufacturing + 0.20 × Stockout + 0.20 × Transport + 0.10 × External</em>
      </p>

      {weights && (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(100px, 1fr))",
          gap: "8px",
          backgroundColor: "#f8fafc",
          padding: "10px",
          borderRadius: "6px",
          fontSize: "11px",
          color: "#475569"
        }}>
          {Object.entries(weights).map(([k, v]) => (
            <div key={k} style={{ textAlign: "center" }}>
              <div style={{ textTransform: "capitalize", fontWeight: "600" }}>{k}</div>
              <div style={{ color: "#2563eb", fontWeight: "700" }}>{(v * 100).toFixed(0)}%</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
