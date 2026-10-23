import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";

export function ForecastCurveChart({ data }) {
  if (!data || data.length === 0) {
    return <div style={{ color: "#94a3b8", fontSize: "13px", padding: "16px" }}>No time-series forecast records available.</div>;
  }

  return (
    <div style={{ width: "100%", height: "290px" }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#64748b" }} />
          {/* Left Y-Axis for Demand volume */}
          <YAxis
            yAxisId="left"
            domain={['dataMin - 10', 'dataMax + 10']}
            tick={{ fontSize: 11, fill: "#2563eb" }}
            label={{ value: 'Demand (Units)', angle: -90, position: 'insideLeft', style: { fill: '#2563eb', fontSize: 11, fontWeight: 600 } }}
          />
          {/* Right Y-Axis for Delay days */}
          <YAxis
            yAxisId="right"
            orientation="right"
            domain={[0, 'dataMax + 1']}
            tick={{ fontSize: 11, fill: "#e11d48" }}
            label={{ value: 'Transit Delay (Days)', angle: 90, position: 'insideRight', style: { fill: '#e11d48', fontSize: 11, fontWeight: 600 } }}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #cbd5e1", fontSize: "12px", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)" }}
          />
          <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="chronos_forecast"
            name="Chronos-2 Demand Forecast (Units)"
            stroke="#2563eb"
            strokeWidth={3}
            dot={{ r: 5, fill: "#2563eb" }}
            activeDot={{ r: 7 }}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="patchtst_delay_forecast"
            name="PatchTST Delay Risk (Days)"
            stroke="#e11d48"
            strokeWidth={2.5}
            strokeDasharray="5 5"
            dot={{ r: 4, fill: "#e11d48" }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
