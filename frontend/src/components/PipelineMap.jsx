import React from "react";
import { Truck, Factory, Warehouse, ShieldAlert, CheckCircle2, ArrowRight } from "lucide-react";

export function PipelineMap({ risks, selectedEntity, onSelectEntity }) {
  const tiers = [
    {
      type: "supplier",
      title: "Tier-1 Suppliers",
      icon: <Factory size={16} color="#475569" />,
      items: risks.filter(r => r.entity_type === "supplier" || (r.entity_id && r.entity_id.startsWith("SUP"))),
    },
    {
      type: "plant",
      title: "Assembly Plants",
      icon: <Factory size={16} color="#475569" />,
      items: risks.filter(r => r.entity_type === "plant" || (r.entity_id && r.entity_id.startsWith("PLT"))),
    },
    {
      type: "warehouse",
      title: "Fulfillment Hubs",
      icon: <Warehouse size={16} color="#475569" />,
      items: risks.filter(r => r.entity_type === "warehouse" || (r.entity_id && r.entity_id.startsWith("WH"))),
    },
    {
      type: "route",
      title: "Transit Corridors",
      icon: <Truck size={16} color="#475569" />,
      items: risks.filter(r => r.entity_type === "route" || (r.entity_id && r.entity_id.startsWith("RT"))),
    },
  ];

  const getStatusColor = (lvl) => {
    switch (lvl?.toLowerCase()) {
      case "high":
        return { bg: "#fee2e2", text: "#991b1b", border: "#f87171" };
      case "medium":
        return { bg: "#fef3c7", text: "#92400e", border: "#fbbf24" };
      default:
        return { bg: "#dcfce7", text: "#166534", border: "#86efac" };
    }
  };

  return (
    <div style={{
      backgroundColor: "#ffffff",
      borderRadius: "12px",
      border: "1px solid #e2e8f0",
      padding: "20px",
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
      marginBottom: "24px"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: "16px", fontWeight: "700", color: "#0f172a" }}>
            Multi-Tier Supply Chain Ecosystem Pipeline
          </h3>
          <p style={{ margin: "4px 0 0 0", fontSize: "12px", color: "#64748b" }}>
            Click any network node to inspect its TreeSHAP feature attributions, anomaly status, and resilience playbook.
          </p>
        </div>
        <div style={{ display: "flex", gap: "12px", fontSize: "11px", fontWeight: "600" }}>
          <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "#dc2626" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#dc2626" }} /> High Risk (≥60%)
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "#d97706" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#d97706" }} /> Moderate
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "#16a34a" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#16a34a" }} /> Normal
          </span>
        </div>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
        gap: "16px",
        alignItems: "stretch"
      }}>
        {tiers.map((tier, idx) => (
          <div key={tier.type} style={{
            backgroundColor: "#f8fafc",
            borderRadius: "8px",
            border: "1px solid #e2e8f0",
            padding: "14px",
            display: "flex",
            flexDirection: "column"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px", borderBottom: "1px solid #e2e8f0", paddingBottom: "8px" }}>
              {tier.icon}
              <span style={{ fontSize: "13px", fontWeight: "700", color: "#1e293b" }}>{tier.title}</span>
              <span style={{ marginLeft: "auto", fontSize: "11px", backgroundColor: "#e2e8f0", padding: "2px 6px", borderRadius: "999px", color: "#475569" }}>
                {tier.items.length}
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px", flex: 1 }}>
              {tier.items.length === 0 ? (
                <div style={{ fontSize: "12px", color: "#94a3b8", textAlign: "center", padding: "12px 0" }}>
                  Active node telemetry synced
                </div>
              ) : (
                tier.items.map((it) => {
                  const isSelected = selectedEntity === it.entity_id;
                  const colors = getStatusColor(it.level);
                  return (
                    <button
                      key={`${it.entity_id}-${it.risk_type}`}
                      onClick={() => onSelectEntity(it.entity_id)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "8px 10px",
                        borderRadius: "6px",
                        border: isSelected ? "2px solid #2563eb" : `1px solid ${colors.border}`,
                        backgroundColor: isSelected ? "#eff6ff" : colors.bg,
                        cursor: "pointer",
                        textAlign: "left",
                        transition: "all 0.15s ease",
                        outline: "none"
                      }}
                    >
                      <div>
                        <div style={{ fontSize: "12px", fontWeight: "700", color: isSelected ? "#1e40af" : colors.text }}>
                          {it.entity_id}
                        </div>
                        <div style={{ fontSize: "10px", color: "#64748b", textTransform: "capitalize" }}>
                          {it.risk_type ? it.risk_type.replace(/_/g, " ") : "risk"}
                        </div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: "12px", fontWeight: "800", color: colors.text }}>
                          {typeof it.probability === "number" ? `${(it.probability * 100).toFixed(0)}%` : "--"}
                        </div>
                        <div style={{ fontSize: "9px", textTransform: "uppercase", fontWeight: "700", color: colors.text }}>
                          {it.level}
                        </div>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
