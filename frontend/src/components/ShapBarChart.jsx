import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from "recharts";

export function ShapBarChart({ features }) {
  if (!features || features.length === 0) {
    return <div style={{ color: "#94a3b8", fontSize: "14px" }}>No SHAP explanations available.</div>;
  }

  const data = features.map((f) => ({
    name: f.feature,
    value: parseFloat(f.shap_value.toFixed(2)),
  }));

  return (
    <div style={{ width: "100%", height: "260px" }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 10, right: 30, left: 120, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
          <XAxis type="number" tick={{ fontSize: 12 }} />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 12, fill: "#334155" }}
            width={110}
          />
          <Tooltip
            formatter={(val) => [`${val > 0 ? "+" : ""}${val}`, "SHAP Impact"]}
            contentStyle={{ backgroundColor: "#ffffff", borderRadius: "6px", border: "1px solid #cbd5e1" }}
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.value >= 0 ? "#ef4444" : "#10b981"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
