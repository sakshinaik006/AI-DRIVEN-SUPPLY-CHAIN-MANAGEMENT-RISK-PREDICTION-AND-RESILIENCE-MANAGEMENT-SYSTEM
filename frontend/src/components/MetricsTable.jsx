import React from "react";
import { ShieldCheck, BarChart2 } from "lucide-react";

export function MetricsTable({ metrics }) {
  if (!metrics || metrics.length === 0) {
    return null;
  }

  return (
    <div style={{
      backgroundColor: "#ffffff",
      borderRadius: "12px",
      border: "1px solid #e2e8f0",
      padding: "20px",
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
      marginTop: "24px"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: "16px", fontWeight: "700", color: "#0f172a" }}>
            Model Benchmarking & Governance Table (Test Split)
          </h3>
          <p style={{ margin: "4px 0 0 0", fontSize: "12px", color: "#64748b" }}>
            Precision-Recall AUC, Recall, and F1 comparisons across Multi-Target CatBoost, EIF, and Baseline models.
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#16a34a", fontWeight: "600" }}>
          <ShieldCheck size={16} /> Audited & Leakage-Free
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", textAlign: "left" }}>
          <thead>
            <tr style={{ backgroundColor: "#f8fafc", borderBottom: "2px solid #e2e8f0", color: "#475569" }}>
              <th style={{ padding: "10px 12px" }}>Model</th>
              <th style={{ padding: "10px 12px" }}>Risk Domain</th>
              <th style={{ padding: "10px 12px" }}>PR-AUC</th>
              <th style={{ padding: "10px 12px" }}>Recall</th>
              <th style={{ padding: "10px 12px" }}>F1-Score</th>
              <th style={{ padding: "10px 12px" }}>Classification</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #f1f5f9", backgroundColor: m.is_baseline ? "#ffffff" : "#f0fdf4" }}>
                <td style={{ padding: "8px 12px", fontWeight: m.is_baseline ? "500" : "700", color: m.is_baseline ? "#334155" : "#166534" }}>
                  {m.model}
                </td>
                <td style={{ padding: "8px 12px", color: "#475569", textTransform: "capitalize" }}>
                  {m.risk_type.replace(/_/g, " ")}
                </td>
                <td style={{ padding: "8px 12px", fontWeight: "700", color: "#0f172a" }}>
                  {typeof m.pr_auc === "number" ? m.pr_auc.toFixed(3) : m.pr_auc}
                </td>
                <td style={{ padding: "8px 12px", color: "#334155" }}>
                  {typeof m.recall === "number" ? m.recall.toFixed(3) : m.recall}
                </td>
                <td style={{ padding: "8px 12px", color: "#334155" }}>
                  {typeof m.f1 === "number" ? m.f1.toFixed(3) : m.f1}
                </td>
                <td style={{ padding: "8px 12px" }}>
                  <span style={{
                    fontSize: "10px",
                    fontWeight: "700",
                    padding: "2px 8px",
                    borderRadius: "999px",
                    backgroundColor: m.is_baseline ? "#f1f5f9" : "#dcfce7",
                    color: m.is_baseline ? "#64748b" : "#15803d"
                  }}>
                    {m.is_baseline ? "Baseline" : "Champion"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
