import React from "react";

export function ActionsPanel({ actions, reasons }) {
  return (
    <div style={{
      border: "1px solid #e2e8f0",
      borderRadius: "8px",
      padding: "20px",
      backgroundColor: "#ffffff",
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
    }}>
      <h3 style={{ margin: "0 0 12px 0", fontSize: "16px", color: "#1e293b" }}>
        Recommended Resilience Actions & Explanations
      </h3>

      {reasons && reasons.length > 0 && (
        <div style={{ marginBottom: "16px", backgroundColor: "#f8fafc", padding: "12px", borderRadius: "6px" }}>
          <h4 style={{ margin: "0 0 8px 0", fontSize: "13px", color: "#334155" }}>Top Model Diagnosis (TreeSHAP)</h4>
          <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "13px", color: "#475569" }}>
            {reasons.map((r, i) => (
              <li key={i} style={{ marginBottom: "4px" }}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {actions && actions.map((act, idx) => (
          <div key={idx} style={{
            display: "flex",
            alignItems: "flex-start",
            gap: "12px",
            padding: "10px",
            borderRadius: "6px",
            border: "1px solid #f1f5f9",
            backgroundColor: act.level === "High" ? "#fff1f2" : "#ffffff"
          }}>
            <span style={{
              fontSize: "11px",
              fontWeight: "700",
              padding: "2px 8px",
              borderRadius: "4px",
              backgroundColor: act.level === "High" ? "#e11d48" : (act.level === "Medium" ? "#d97706" : "#16a34a"),
              color: "#ffffff"
            }}>
              {act.risk_type ? act.risk_type.replace(/_/g, " ").toUpperCase() : "RISK"}
            </span>
            <div style={{ fontSize: "13px", color: "#1e293b", flex: 1 }}>
              {act.action}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
