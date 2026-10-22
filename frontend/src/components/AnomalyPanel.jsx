import React from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";

export function AnomalyPanel({ anomalies }) {
  if (!anomalies || anomalies.length === 0) {
    return (
      <div style={{
        backgroundColor: "#ffffff",
        borderRadius: "12px",
        border: "1px solid #e2e8f0",
        padding: "20px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
      }}>
        <h3 style={{ margin: "0 0 8px 0", fontSize: "16px", fontWeight: "700", color: "#0f172a" }}>
          Extended Isolation Forest Anomaly Monitor
        </h3>
        <p style={{ fontSize: "12px", color: "#16a34a" }}>All telemetry streams operating within normal bounds.</p>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: "#ffffff",
      borderRadius: "12px",
      border: "1px solid #e2e8f0",
      padding: "20px",
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
      display: "flex",
      flexDirection: "column"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: "15px", fontWeight: "700", color: "#0f172a" }}>
            Unsupervised Outlier Monitor (EIF)
          </h3>
          <p style={{ margin: "2px 0 0 0", fontSize: "11px", color: "#64748b" }}>
            Hyperplane anomaly screening detecting multidimensional operational spikes.
          </p>
        </div>
        <span style={{
          backgroundColor: "#fee2e2",
          color: "#991b1b",
          fontSize: "11px",
          fontWeight: "700",
          padding: "3px 8px",
          borderRadius: "999px",
          border: "1px solid #f87171"
        }}>
          {anomalies.length} Flagged
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "8px", maxHeight: "240px", overflowY: "auto" }}>
        {anomalies.slice(0, 5).map((a, i) => (
          <div key={i} style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "8px 10px",
            borderRadius: "6px",
            backgroundColor: "#fff1f2",
            border: "1px solid #fecdd3",
            fontSize: "12px"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <AlertTriangle size={15} color="#e11d48" />
              <div>
                <strong style={{ color: "#9f1239" }}>{a.entity_id}</strong>
                <span style={{ marginLeft: "6px", color: "#64748b", textTransform: "capitalize" }}>
                  {a.risk_type ? a.risk_type.replace(/_/g, " ") : "risk"}
                </span>
              </div>
            </div>
            <div style={{ textAlign: "right" }}>
              <span style={{ fontWeight: "700", color: "#9f1239" }}>
                Score: {typeof a.anomaly_score === "number" ? a.anomaly_score.toFixed(3) : a.anomaly_score}
              </span>
              <div style={{ fontSize: "10px", color: "#64748b" }}>{a.date}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
