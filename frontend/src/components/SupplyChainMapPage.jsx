import React, { useState } from "react";
import { 
  Building2, 
  Factory, 
  Warehouse, 
  Truck, 
  ArrowRight, 
  AlertTriangle, 
  ShieldCheck,
  Info
} from "lucide-react";

export function SupplyChainMapPage({ data, selectedEntityId, onSelectEntity, onNavigateTab }) {
  const [activeNodeId, setActiveNodeId] = useState(selectedEntityId || "SUP001");

  if (!data) return <div style={{ color: "#94a3b8" }}>Loading supply chain map...</div>;

  const entities = data.entities || [];

  const suppliers = entities.filter(e => e.type === "supplier");
  const routes = entities.filter(e => e.type === "route");
  const plants = entities.filter(e => e.type === "plant");
  const warehouses = entities.filter(e => e.type === "warehouse");

  const activeEntity = entities.find(e => e.entity_id === activeNodeId) || entities[0];

  function getNodeColor(level) {
    if (level === "High") return "#ef4444";
    if (level === "Medium") return "#eab308";
    return "#22c55e";
  }

  function getNodeBg(level) {
    if (level === "High") return "rgba(239, 68, 68, 0.15)";
    if (level === "Medium") return "rgba(234, 179, 8, 0.15)";
    return "rgba(34, 197, 94, 0.15)";
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {/* 1. TOP HEADER & LEGEND */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        backgroundColor: "#1e293b",
        padding: "12px 18px",
        borderRadius: "8px",
        border: "1px solid #334155"
      }}>
        <div>
          <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
            End-to-End Network Topology
          </div>
          <div style={{ fontSize: "11px", color: "#94a3b8" }}>
            Visualizes actual physical dependencies: Supplier → Transit Route → Manufacturing Plant → Warehouse
          </div>
        </div>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#f8fafc" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: "#22c55e" }} />
            Low Risk (Safe)
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#f8fafc" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: "#eab308" }} />
            Medium Risk (Guarded)
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#f8fafc" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: "#ef4444" }} />
            High Risk (Critical)
          </div>
        </div>
      </div>

      {/* 2. MAIN NETWORK DIAGRAM (4 TIERS) */}
      <div style={{
        backgroundColor: "#0f172a",
        border: "1px solid #334155",
        borderRadius: "8px",
        padding: "20px",
        display: "grid",
        gridTemplateColumns: "1.1fr 1.3fr 1.1fr 1.1fr",
        gap: "20px",
        minHeight: "420px"
      }}>
        {/* TIER 1: SUPPLIERS */}
        <div style={tierColStyle}>
          <div style={tierHeaderStyle}>
            <Building2 size={16} color="#38bdf8" /> Tier 1: Suppliers ({suppliers.length})
          </div>
          <div style={tierListStyle}>
            {suppliers.map(s => {
              const isSelected = s.entity_id === activeNodeId;
              const color = getNodeColor(s.level);
              return (
                <div
                  key={s.entity_id}
                  onClick={() => {
                    setActiveNodeId(s.entity_id);
                    onSelectEntity(s.entity_id);
                  }}
                  style={{
                    ...nodeCardStyle,
                    borderColor: isSelected ? "#38bdf8" : color,
                    backgroundColor: isSelected ? "#1e293b" : "#0f172a",
                    borderLeft: `4px solid ${color}`
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "12px", fontWeight: "700", color: "#f8fafc" }}>{s.entity_id}</span>
                    <span style={{
                      fontSize: "10px",
                      fontWeight: "700",
                      padding: "1px 6px",
                      borderRadius: "4px",
                      backgroundColor: getNodeBg(s.level),
                      color: color
                    }}>
                      {Math.round(s.probability * 100)}%
                    </span>
                  </div>
                  <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "2px" }}>{s.name}</div>
                  <div style={{ fontSize: "10px", color: "#64748b" }}>{s.city}, {s.country}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* TIER 2: TRANSIT CORRIDORS */}
        <div style={tierColStyle}>
          <div style={tierHeaderStyle}>
            <Truck size={16} color="#3b82f6" /> Transit Corridors ({routes.length})
          </div>
          <div style={tierListStyle}>
            {routes.map(r => {
              const isSelected = r.entity_id === activeNodeId;
              const color = getNodeColor(r.level);
              return (
                <div
                  key={r.entity_id}
                  onClick={() => {
                    setActiveNodeId(r.entity_id);
                    onSelectEntity(r.entity_id);
                  }}
                  style={{
                    ...nodeCardStyle,
                    borderColor: isSelected ? "#38bdf8" : color,
                    backgroundColor: isSelected ? "#1e293b" : "#0f172a",
                    borderLeft: `4px solid ${color}`
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "12px", fontWeight: "700", color: "#f8fafc" }}>{r.entity_id}</span>
                    <span style={{
                      fontSize: "10px",
                      fontWeight: "700",
                      padding: "1px 6px",
                      borderRadius: "4px",
                      backgroundColor: getNodeBg(r.level),
                      color: color
                    }}>
                      {Math.round(r.probability * 100)}%
                    </span>
                  </div>
                  <div style={{ fontSize: "10px", color: "#94a3b8", marginTop: "2px" }}>
                    {r.origin_id} → {r.destination_id} ({r.shipping_mode})
                  </div>
                  <div style={{ fontSize: "10px", color: "#64748b" }}>{r.distance_km} km · {r.scheduled_days}d</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* TIER 3: MANUFACTURING PLANTS */}
        <div style={tierColStyle}>
          <div style={tierHeaderStyle}>
            <Factory size={16} color="#a855f7" /> Assembly Plants ({plants.length})
          </div>
          <div style={tierListStyle}>
            {plants.map(p => {
              const isSelected = p.entity_id === activeNodeId;
              const color = getNodeColor(p.level);
              return (
                <div
                  key={p.entity_id}
                  onClick={() => {
                    setActiveNodeId(p.entity_id);
                    onSelectEntity(p.entity_id);
                  }}
                  style={{
                    ...nodeCardStyle,
                    borderColor: isSelected ? "#38bdf8" : color,
                    backgroundColor: isSelected ? "#1e293b" : "#0f172a",
                    borderLeft: `4px solid ${color}`
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "12px", fontWeight: "700", color: "#f8fafc" }}>{p.entity_id}</span>
                    <span style={{
                      fontSize: "10px",
                      fontWeight: "700",
                      padding: "1px 6px",
                      borderRadius: "4px",
                      backgroundColor: getNodeBg(p.level),
                      color: color
                    }}>
                      {Math.round(p.probability * 100)}%
                    </span>
                  </div>
                  <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "2px" }}>{p.name}</div>
                  <div style={{ fontSize: "10px", color: "#64748b" }}>Cap: {p.capacity_planned} / day</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* TIER 4: WAREHOUSES */}
        <div style={tierColStyle}>
          <div style={tierHeaderStyle}>
            <Warehouse size={16} color="#eab308" /> Warehouses ({warehouses.length})
          </div>
          <div style={tierListStyle}>
            {warehouses.map(w => {
              const isSelected = w.entity_id === activeNodeId;
              const color = getNodeColor(w.level);
              return (
                <div
                  key={w.entity_id}
                  onClick={() => {
                    setActiveNodeId(w.entity_id);
                    onSelectEntity(w.entity_id);
                  }}
                  style={{
                    ...nodeCardStyle,
                    borderColor: isSelected ? "#38bdf8" : color,
                    backgroundColor: isSelected ? "#1e293b" : "#0f172a",
                    borderLeft: `4px solid ${color}`
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "12px", fontWeight: "700", color: "#f8fafc" }}>{w.entity_id}</span>
                    <span style={{
                      fontSize: "10px",
                      fontWeight: "700",
                      padding: "1px 6px",
                      borderRadius: "4px",
                      backgroundColor: getNodeBg(w.level),
                      color: color
                    }}>
                      {Math.round(w.probability * 100)}%
                    </span>
                  </div>
                  <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "2px" }}>{w.name}</div>
                  <div style={{ fontSize: "10px", color: "#64748b" }}>Safety Buffer: {w.stock_days_cover}d</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 3. SELECTED NODE DETAIL & TOPOLOGICAL IMPACT */}
      {activeEntity && (
        <div style={{
          backgroundColor: "#1e293b",
          border: "1px solid #334155",
          borderRadius: "8px",
          padding: "16px 20px",
          display: "grid",
          gridTemplateColumns: "1.2fr 1fr 1fr",
          gap: "18px",
          alignItems: "center"
        }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <span style={{ fontSize: "16px", fontWeight: "800", color: "#f8fafc" }}>
                {activeEntity.name} ({activeEntity.entity_id})
              </span>
              <span style={{
                fontSize: "10px",
                fontWeight: "800",
                padding: "2px 8px",
                borderRadius: "4px",
                backgroundColor: getNodeBg(activeEntity.level),
                color: getNodeColor(activeEntity.level)
              }}>
                {activeEntity.level} Risk ({Math.round(activeEntity.probability * 100)}%)
              </span>
            </div>
            <div style={{ fontSize: "12px", color: "#94a3b8" }}>
              Location: {activeEntity.city}, {activeEntity.country} · Category: {activeEntity.category}
            </div>
          </div>

          <div>
            <div style={{ fontSize: "11px", fontWeight: "700", color: "#94a3b8", textTransform: "uppercase", marginBottom: "4px" }}>
              Direct Connected Entities
            </div>
            <div style={{ fontSize: "13px", fontWeight: "600", color: "#38bdf8" }}>
              {activeEntity.connected_entities?.length > 0 ? activeEntity.connected_entities.join(", ") : "Terminal Asset"}
            </div>
            <div style={{ fontSize: "11px", color: "#64748b", marginTop: "2px" }}>
              Upstream / Downstream Linkage
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
            <button
              onClick={() => {
                onSelectEntity(activeEntity.entity_id);
                onNavigateTab("insights");
              }}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                padding: "8px 16px",
                borderRadius: "6px",
                backgroundColor: "#0284c7",
                color: "#ffffff",
                fontWeight: "700",
                fontSize: "12px",
                border: "none",
                cursor: "pointer"
              }}
            >
              Analyze Root Cause <ArrowRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const tierColStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "10px"
};

const tierHeaderStyle = {
  fontSize: "12px",
  fontWeight: "700",
  color: "#f8fafc",
  display: "flex",
  alignItems: "center",
  gap: "6px",
  paddingBottom: "6px",
  borderBottom: "1px solid #334155"
};

const tierListStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
  overflowY: "auto",
  maxHeight: "360px"
};

const nodeCardStyle = {
  padding: "10px 12px",
  borderRadius: "6px",
  border: "1px solid #334155",
  cursor: "pointer",
  transition: "all 0.12s ease"
};
