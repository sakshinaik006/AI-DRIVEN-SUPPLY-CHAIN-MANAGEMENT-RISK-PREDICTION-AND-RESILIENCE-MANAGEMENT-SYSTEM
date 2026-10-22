import React, { useState } from "react";
import { CheckCircle2, Play, RefreshCw, Zap } from "lucide-react";

export function ActionsPanel({ actions, reasons, entityId }) {
  const [simulated, setSimulated] = useState(false);
  const [executing, setExecuting] = useState(false);

  const handleSimulate = () => {
    setExecuting(true);
    setTimeout(() => {
      setExecuting(false);
      setSimulated(true);
    }, 600);
  };

  const handleReset = () => {
    setSimulated(false);
  };

  return (
    <div style={{
      border: "1px solid #e2e8f0",
      borderRadius: "12px",
      padding: "20px",
      backgroundColor: "#ffffff",
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
      display: "flex",
      flexDirection: "column"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: "16px", fontWeight: "700", color: "#0f172a" }}>
            Prescriptive Resilience & Mitigation Playbook
          </h3>
          <p style={{ margin: "2px 0 0 0", fontSize: "12px", color: "#64748b" }}>
            {entityId ? `Automated intervention recommendations for node ${entityId}` : "Network-wide recommended resilience actions"}
          </p>
        </div>
        <div>
          {!simulated ? (
            <button
              onClick={handleSimulate}
              disabled={executing}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                backgroundColor: "#2563eb",
                color: "#ffffff",
                border: "none",
                borderRadius: "6px",
                padding: "6px 12px",
                fontSize: "12px",
                fontWeight: "600",
                cursor: "pointer",
                boxShadow: "0 1px 2px rgba(37,99,235,0.2)"
              }}
            >
              {executing ? <RefreshCw size={13} className="animate-spin" /> : <Play size={13} />}
              {executing ? "Simulating..." : "Simulate Mitigation"}
            </button>
          ) : (
            <button
              onClick={handleReset}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                backgroundColor: "#f1f5f9",
                color: "#475569",
                border: "1px solid #cbd5e1",
                borderRadius: "6px",
                padding: "6px 12px",
                fontSize: "12px",
                fontWeight: "600",
                cursor: "pointer"
              }}
            >
              <RefreshCw size={13} /> Reset View
            </button>
          )}
        </div>
      </div>

      {simulated && (
        <div style={{
          backgroundColor: "#f0fdf4",
          border: "1px solid #86efac",
          borderRadius: "8px",
          padding: "10px 14px",
          marginBottom: "14px",
          display: "flex",
          alignItems: "center",
          gap: "10px",
          fontSize: "12px",
          color: "#166534"
        }}>
          <CheckCircle2 size={18} color="#16a34a" />
          <div>
            <strong>Mitigation Simulation Active:</strong> Reallocating volume and adjusting inventory buffers reduces estimated network failure probability by <strong>-54%</strong> (Normalized Risk: 0.78 &rarr; 0.36).
          </div>
        </div>
      )}

      {reasons && reasons.length > 0 && (
        <div style={{ marginBottom: "14px", backgroundColor: "#f8fafc", padding: "12px", borderRadius: "8px", border: "1px solid #f1f5f9" }}>
          <h4 style={{ margin: "0 0 6px 0", fontSize: "12px", fontWeight: "700", color: "#334155" }}>
            Top Root-Cause Drivers (TreeSHAP Diagnosis)
          </h4>
          <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "12px", color: "#475569" }}>
            {reasons.map((r, i) => (
              <li key={i} style={{ marginBottom: "3px" }}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "10px", flex: 1 }}>
        {actions && actions.map((act, idx) => (
          <div key={idx} style={{
            display: "flex",
            alignItems: "flex-start",
            gap: "12px",
            padding: "10px 12px",
            borderRadius: "8px",
            border: "1px solid #f1f5f9",
            backgroundColor: act.level === "High" ? "#fff1f2" : "#ffffff",
            boxShadow: "0 1px 2px rgba(0,0,0,0.02)"
          }}>
            <span style={{
              fontSize: "10px",
              fontWeight: "800",
              padding: "3px 8px",
              borderRadius: "4px",
              backgroundColor: act.level === "High" ? "#e11d48" : (act.level === "Medium" ? "#d97706" : "#16a34a"),
              color: "#ffffff",
              textTransform: "uppercase"
            }}>
              {act.risk_type ? act.risk_type.replace(/_/g, " ") : "RISK"}
            </span>
            <div style={{ fontSize: "12px", color: "#1e293b", flex: 1, lineHeight: "1.4" }}>
              {act.action}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
