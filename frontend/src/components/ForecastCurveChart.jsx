import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";

export function ForecastCurveChart({ data }) {
  if (!data || data.length === 0) {
    return <div style={{ color: "#94a3b8", fontSize: "13px", padding: "16px" }}>No time-series forecast records available.</div>;
  }

  return (
    <div style={{ width: "100%", height: "260px" }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#64748b" }} />
          <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
          <Tooltip
            contentStyle={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #cbd5e1", fontSize: "12px", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)" }}
          />
          <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
          <Line
            type="monotone"
            dataKey="chronos_forecast"
            name="Chronos-2 Demand Forecast"
            stroke="#2563eb"
            strokeWidth={2.5}
            dot={{ r: 4, fill: "#2563eb" }}
          />
          <Line
            type="monotone"
            dataKey="patchtst_delay_forecast"
            name="PatchTST Delay Risk (Days)"
            stroke="#e11d48"
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={{ r: 3, fill: "#e11d48" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
