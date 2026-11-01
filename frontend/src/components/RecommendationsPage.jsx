import React, { useState } from "react";
import { 
  CheckCircle2, 
  AlertTriangle, 
  Filter, 
  Play, 
  RotateCcw, 
  ShieldCheck, 
  Sparkles,
  ArrowRight
} from "lucide-react";

export function RecommendationsPage({ data, onSelectEntity, onNavigateTab }) {
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedPriority, setSelectedPriority] = useState("All");
  const [simulatedRecId, setSimulatedRecId] = useState(null);

  if (!data) return <div style={{ color: "#94a3b8" }}>Loading recommendations...</div>;

  const rawRecs = data.recommendations || [];

  const filteredRecs = rawRecs.filter(r => {
    const matchesCat = selectedCategory === "All" || r.category.toLowerCase().includes(selectedCategory.toLowerCase());
    const matchesPri = selectedPriority === "All" || r.priority === selectedPriority;
    return matchesCat && matchesPri;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      {/* 1. TOP STATS & RESILIENCE PLAYBOOK BANNER */}
      <div style={{
        backgroundColor: "#1e293b",
        borderRadius: "8px",
        padding: "16px 20px",
        border: "1px solid #334155",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <div>
          <div style={{ fontSize: "16px", fontWeight: "800", color: "#f8fafc", display: "flex", alignItems: "center", gap: "8px" }}>
            <Sparkles size={18} color="#38bdf8" /> Prescriptive Resilience & Action Playbooks
          </div>
          <div style={{ fontSize: "12px", color: "#94a3b8", marginTop: "2px" }}>
            Actionable interventions prioritized by AI risk severity, asset topology, and operational impact
          </div>
        </div>

        <div style={{ display: "flex", gap: "14px" }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase" }}>Critical Actions</div>
            <div style={{ fontSize: "18px", fontWeight: "800", color: "#ef4444" }}>
              {rawRecs.filter(r => r.priority === "Critical").length}
            </div>
          </div>
          <div style={{ width: "1px", backgroundColor: "#334155" }} />
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase" }}>Total Generated</div>
            <div style={{ fontSize: "18px", fontWeight: "800", color: "#38bdf8" }}>
              {rawRecs.length}
            </div>
          </div>
        </div>
      </div>

      {/* 2. FILTER CONTROLS */}
      <div style={{
        display: "flex",
        gap: "14px",
        alignItems: "center",
        backgroundColor: "#0f172a",
        padding: "10px 16px",
        borderRadius: "6px",
        border: "1px solid #334155"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#94a3b8" }}>
          <Filter size={14} /> Filter by Category:
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={selectStyle}
        >
          <option value="All">All Categories</option>
          <option value="Supplier">Supplier Risk</option>
          <option value="Manufacturing">Manufacturing Risk</option>
          <option value="Warehouse">Warehouse Risk</option>
          <option value="Transportation">Transportation Risk</option>
        </select>

        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#94a3b8", marginLeft: "10px" }}>
          Priority:
        </div>
        <select
          value={selectedPriority}
          onChange={(e) => setSelectedPriority(e.target.value)}
          style={selectStyle}
        >
          <option value="All">All Priorities</option>
          <option value="Critical">Critical Priority</option>
          <option value="Moderate">Moderate Priority</option>
        </select>
      </div>

      {/* 3. RECOMMENDATIONS LIST */}
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {filteredRecs.length === 0 ? (
          <div style={{
            backgroundColor: "#1e293b",
            borderRadius: "8px",
            padding: "30px",
            textAlign: "center",
            border: "1px solid #334155"
          }}>
            <ShieldCheck size={36} color="#22c55e" style={{ margin: "0 auto 10px auto" }} />
            <div style={{ fontSize: "15px", fontWeight: "700", color: "#22c55e" }}>
              No Emergency Interventions Required
            </div>
            <div style={{ fontSize: "12px", color: "#94a3b8", maxWidth: "400px", margin: "6px auto 0 auto" }}>
              All physical entities operate within baseline parameters. Prescriptive recommendations are strictly withheld for safe or zero-risk assets.
            </div>
          </div>
        ) : (
          filteredRecs.map((rec) => {
            const isSimulated = simulatedRecId === rec.id;
            const isCritical = rec.priority === "Critical";
            return (
              <div
                key={rec.id}
                style={{
                  backgroundColor: "#1e293b",
                  borderRadius: "8px",
                  padding: "16px 20px",
                  border: isSimulated ? "1px solid #22c55e" : "1px solid #334155",
                  borderLeft: `4px solid ${isCritical ? "#ef4444" : "#eab308"}`,
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                      <span style={{ fontSize: "13px", fontWeight: "800", color: "#38bdf8" }}>
                        {rec.id}
                      </span>
                      <span style={{ fontSize: "13px", fontWeight: "700", color: "#f8fafc" }}>
                        {rec.entity_name} ({rec.entity_id})
                      </span>
                      <span style={{
                        fontSize: "10px",
                        fontWeight: "800",
                        padding: "1px 6px",
                        borderRadius: "4px",
                        backgroundColor: isCritical ? "rgba(239, 68, 68, 0.2)" : "rgba(234, 179, 8, 0.2)",
                        color: isCritical ? "#ef4444" : "#eab308"
                      }}>
                        {rec.priority}
                      </span>
                      <span style={{
                        fontSize: "10px",
                        fontWeight: "700",
                        padding: "1px 6px",
                        borderRadius: "4px",
                        backgroundColor: "#0f172a",
                        color: "#94a3b8"
                      }}>
                        {rec.category}
                      </span>
                    </div>
                    <div style={{ fontSize: "13px", color: "#f8fafc", fontWeight: "600", marginTop: "4px" }}>
                      {rec.action}
                    </div>
                    <div style={{ fontSize: "12px", color: "#94a3b8", marginTop: "2px" }}>
                      Root Cause: {rec.reason}
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <button
                      onClick={() => setSimulatedRecId(isSimulated ? null : rec.id)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        padding: "6px 14px",
                        borderRadius: "6px",
                        border: "none",
                        backgroundColor: isSimulated ? "#22c55e" : "#0284c7",
                        color: "#ffffff",
                        fontSize: "11px",
                        fontWeight: "700",
                        cursor: "pointer"
                      }}
                    >
                      {isSimulated ? <CheckCircle2 size={13} /> : <Play size={13} />}
                      {isSimulated ? "Mitigation Applied" : "Simulate Mitigation"}
                    </button>
                    <button
                      onClick={() => {
                        onSelectEntity(rec.entity_id);
                        onNavigateTab("insights");
                      }}
                      style={{
                        padding: "6px 12px",
                        borderRadius: "6px",
                        backgroundColor: "#0f172a",
                        border: "1px solid #334155",
                        color: "#38bdf8",
                        fontSize: "11px",
                        fontWeight: "600",
                        cursor: "pointer"
                      }}
                    >
                      Inspect AI
                    </button>
                  </div>
                </div>

                {/* Simulated Risk Reduction Box */}
                <div style={{
                  backgroundColor: "#0f172a",
                  padding: "8px 12px",
                  borderRadius: "6px",
                  border: "1px solid #1e293b",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  fontSize: "12px"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px", color: isSimulated ? "#22c55e" : "#94a3b8" }}>
                    <ShieldCheck size={14} color={isSimulated ? "#22c55e" : "#38bdf8"} />
                    <span style={{ fontWeight: "600" }}>Expected Impact: </span> {rec.mitigation_effect}
                  </div>
                  <span style={{
                    fontSize: "10px",
                    fontWeight: "700",
                    color: isSimulated ? "#22c55e" : "#38bdf8",
                    textTransform: "uppercase"
                  }}>
                    {isSimulated ? "Status: Live Simulation Active" : "Status: Action Required"}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

const selectStyle = {
  backgroundColor: "#1e293b",
  color: "#f8fafc",
  border: "1px solid #334155",
  borderRadius: "4px",
  padding: "4px 10px",
  fontSize: "12px",
  cursor: "pointer"
};
