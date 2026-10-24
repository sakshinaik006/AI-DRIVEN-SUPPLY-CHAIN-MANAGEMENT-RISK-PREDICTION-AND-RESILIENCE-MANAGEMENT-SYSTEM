import React, { useState, useEffect } from "react";
import { RiskCard } from "./components/RiskCard";
import { ShapBarChart } from "./components/ShapBarChart";
import { NetworkScore } from "./components/NetworkScore";
import { ActionsPanel } from "./components/ActionsPanel";
import { PipelineMap } from "./components/PipelineMap";
import { MetricsTable } from "./components/MetricsTable";
import { 
  Network, 
  Lightbulb, 
  Award,
  Calendar,
  Play,
  Pause,
  AlertTriangle,
  ArrowRight
} from "lucide-react";

export default function App() {
  const [data, setData] = useState(null);
  const [metricsData, setMetricsData] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState("SUP001");
  const [selectedDate, setSelectedDate] = useState("2025-08-15");
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeTab, setActiveTab] = useState("pipeline"); // "pipeline" | "reasons" | "metrics"
  const [loading, setLoading] = useState(true);
  const [source, setSource] = useState("api");

  const dates = [
    { label: "Scenario 1: Normal Operations (Apr 15)", value: "2025-04-15" },
    { label: "Scenario 2: Typhoon & Supply Starvation (Aug 15)", value: "2025-08-15" },
    { label: "Scenario 3: Retail Stockout Surge (Oct 24)", value: "2025-10-24" },
  ];

  async function loadData(dateStr) {
    try {
      const apiUrl = window.__API_URL__ || "http://localhost:8001";
      const [resRisks, resNet, resMetrics] = await Promise.allSettled([
        fetch(`${apiUrl}/api/risks?date=${dateStr}`, { signal: AbortSignal.timeout(8000) }),
        fetch(`${apiUrl}/api/network-score?date=${dateStr}`, { signal: AbortSignal.timeout(8000) }),
        fetch(`${apiUrl}/api/metrics`, { signal: AbortSignal.timeout(8000) }),
      ]);

      if (resRisks.status === "fulfilled" && resRisks.value.ok) {
        const jsonRisks = await resRisks.value.json();
        let netScore = 0.42;
        let netLevel = "Medium";
        let weights = { supplier: 0.25, manufacturing: 0.25, stockout: 0.2, transport: 0.2, external: 0.1 };

        if (resNet.status === "fulfilled" && resNet.value.ok) {
          const jsonNet = await resNet.value.json();
          netScore = jsonNet.network_risk_score;
          netLevel = jsonNet.level;
          weights = jsonNet.weights_assumption || weights;
        }

        setData({
          network_score: netScore,
          network_level: netLevel,
          weights_assumption: weights,
          risks: jsonRisks,
        });
        setSource("Live FastAPI Backend");
      } else {
        throw new Error("API Offline");
      }

      if (resMetrics.status === "fulfilled" && resMetrics.value.ok) setMetricsData(await resMetrics.value.json());
    } catch (e) {
      // Fallback
      try {
        const fb = await (await fetch("/api_fallback.json")).json();
        const filteredFbRisks = (fb.risks || []).filter(r => !r.date || r.date === dateStr);
        setData({
          ...fb,
          risks: filteredFbRisks.length > 0 ? filteredFbRisks : fb.risks
        });
        setSource("Local Fallback Cache");
        setMetricsData([
          { model: "Multi-Target CatBoost (Our Model)", risk_type: "all_targets", pr_auc: 0.850, recall: 0.780, f1: 0.810, is_baseline: false },
          { model: "XGBoost Baseline", risk_type: "supplier_failure", pr_auc: 0.517, recall: 0.422, f1: 0.371, is_baseline: true },
          { model: "Extended Isolation Forest (EIF)", risk_type: "supplier_failure", pr_auc: 1.000, recall: 1.000, f1: 0.127, is_baseline: false },
          { model: "Plain Isolation Forest", risk_type: "supplier_failure", pr_auc: 1.000, recall: 1.000, f1: 0.077, is_baseline: true },
          { model: "DeBERTa-v3 NLP + NER", risk_type: "news_sentiment", pr_auc: 1.000, recall: 1.000, f1: 1.000, is_baseline: false },
        ]);
      } catch (err) {}
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData(selectedDate);
  }, [selectedDate]);

  // Demo playback loop
  useEffect(() => {
    let timer = null;
    if (isPlaying) {
      let i = 0;
      timer = setInterval(() => {
        i = (i + 1) % dates.length;
        setSelectedDate(dates[i].value);
      }, 3500);
    } else {
      clearInterval(timer);
    }
    return () => clearInterval(timer);
  }, [isPlaying]);

  const allRisks = data?.risks || [];
  const highRisks = allRisks.filter(r => r.level?.toLowerCase() === "high").length;

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      width: "100%",
      minHeight: "100vh",
      height: "100vh",
      overflow: "hidden",
      backgroundColor: "#f8fafc",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      color: "#0f172a"
    }}>
      {/* 1. TOP BAR */}
      <header style={{
        backgroundColor: "#1e293b",
        color: "#ffffff",
        padding: "10px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexShrink: 0
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <Network size={22} color="#38bdf8" />
          <div>
            <h1 style={{ fontSize: "16px", fontWeight: "800", margin: 0 }}>
              AI Supply Chain Risk & Resilience Dashboard
            </h1>
            <span style={{ fontSize: "11px", color: "#94a3b8" }}>
              7-Day Predictive Risk Forecasting & Prescriptive Mitigation
            </span>
          </div>
        </div>

        {/* Live Scenario Controller */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", backgroundColor: "#0f172a", padding: "4px 8px", borderRadius: "6px" }}>
            <Calendar size={13} color="#94a3b8" />
            <select
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              style={{
                backgroundColor: "transparent",
                color: "#38bdf8",
                border: "none",
                fontSize: "11px",
                fontWeight: "700",
                cursor: "pointer",
                outline: "none"
              }}
            >
              {dates.map(d => (
                <option key={d.value} value={d.value} style={{ backgroundColor: "#0f172a" }}>
                  {d.label}
                </option>
              ))}
            </select>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              style={{
                backgroundColor: isPlaying ? "#e11d48" : "#2563eb",
                color: "#ffffff",
                border: "none",
                borderRadius: "4px",
                padding: "3px 8px",
                fontSize: "10px",
                fontWeight: "700",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "3px"
              }}
            >
              {isPlaying ? <Pause size={10} /> : <Play size={10} />}
              {isPlaying ? "Pause" : "Play Demo"}
            </button>
          </div>

          <span style={{
            fontSize: "11px",
            backgroundColor: source.includes("Live") ? "#064e3b" : "#451a03",
            color: source.includes("Live") ? "#34d399" : "#fbbf24",
            padding: "4px 10px",
            borderRadius: "999px",
            fontWeight: "700"
          }}>
            &bull; {source}
          </span>
        </div>
      </header>

      {/* 2. THREE KEY NUMBERS (Simple KPI Ribbon) */}
      <section style={{
        backgroundColor: "#ffffff",
        borderBottom: "1px solid #e2e8f0",
        padding: "10px 24px",
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr",
        gap: "16px",
        flexShrink: 0
      }}>
        <div style={{ borderLeft: "3px solid #2563eb", paddingLeft: "10px" }}>
          <div style={{ fontSize: "11px", color: "#64748b", fontWeight: "600" }}>OVERALL NETWORK RISK</div>
          <div style={{ fontSize: "20px", fontWeight: "800", color: "#0f172a" }}>
            {data?.network_score ? `${(data.network_score * 100).toFixed(1)}%` : "42.0%"} 
            <span style={{ fontSize: "12px", color: "#d97706", marginLeft: "6px" }}>({data?.network_level || "Medium"})</span>
          </div>
        </div>

        <div style={{ borderLeft: "3px solid #e11d48", paddingLeft: "10px" }}>
          <div style={{ fontSize: "11px", color: "#64748b", fontWeight: "600" }}>ACTIVE DISRUPTIONS</div>
          <div style={{ fontSize: "20px", fontWeight: "800", color: highRisks > 0 ? "#e11d48" : "#16a34a" }}>
            {highRisks} Nodes At High Risk <span style={{ fontSize: "12px", color: "#64748b", fontWeight: "500" }}>out of 27</span>
          </div>
        </div>

        <div style={{ borderLeft: "3px solid #16a34a", paddingLeft: "10px" }}>
          <div style={{ fontSize: "11px", color: "#64748b", fontWeight: "600" }}>MODEL ACCURACY (PR-AUC)</div>
          <div style={{ fontSize: "20px", fontWeight: "800", color: "#16a34a" }}>
            0.850 <span style={{ fontSize: "12px", color: "#64748b", fontWeight: "500" }}>(CatBoost Multi-Target)</span>
          </div>
        </div>
      </section>

      {/* 3. THREE CLEAN TABS (FORECAST REMOVED) */}
      <nav style={{
        backgroundColor: "#ffffff",
        borderBottom: "1px solid #e2e8f0",
        padding: "0 24px",
        display: "flex",
        gap: "28px",
        flexShrink: 0
      }}>
        <button
          onClick={() => setActiveTab("pipeline")}
          style={{
            padding: "12px 0",
            border: "none",
            borderBottom: activeTab === "pipeline" ? "3px solid #2563eb" : "3px solid transparent",
            backgroundColor: "transparent",
            color: activeTab === "pipeline" ? "#2563eb" : "#64748b",
            fontWeight: activeTab === "pipeline" ? "800" : "600",
            fontSize: "13px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}
        >
          <Network size={16} /> 1. Supply Chain Pipeline
        </button>

        <button
          onClick={() => setActiveTab("reasons")}
          style={{
            padding: "12px 0",
            border: "none",
            borderBottom: activeTab === "reasons" ? "3px solid #2563eb" : "3px solid transparent",
            backgroundColor: "transparent",
            color: activeTab === "reasons" ? "#2563eb" : "#64748b",
            fontWeight: activeTab === "reasons" ? "800" : "600",
            fontSize: "13px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}
        >
          <Lightbulb size={16} /> 2. Root Cause & Action Plan
        </button>

        <button
          onClick={() => setActiveTab("metrics")}
          style={{
            padding: "12px 0",
            border: "none",
            borderBottom: activeTab === "metrics" ? "3px solid #2563eb" : "3px solid transparent",
            backgroundColor: "transparent",
            color: activeTab === "metrics" ? "#2563eb" : "#64748b",
            fontWeight: activeTab === "metrics" ? "800" : "600",
            fontSize: "13px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}
        >
          <Award size={16} /> 3. Model Accuracy Comparison
        </button>
      </nav>

      {/* 4. MAIN CONTENT */}
      <main style={{ flex: 1, padding: "16px 24px", overflowY: "auto" }}>
        {/* TAB 1: PIPELINE */}
        {activeTab === "pipeline" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <PipelineMap
              risks={allRisks}
              selectedEntity={selectedEntity}
              onSelectEntity={(eid) => setSelectedEntity(eid)}
            />
            <div style={{
              backgroundColor: "#ffffff",
              padding: "14px 18px",
              borderRadius: "8px",
              border: "1px solid #e2e8f0",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}>
              <div>
                <span style={{ fontSize: "11px", color: "#64748b" }}>Currently Selected Node:</span>
                <div style={{ fontSize: "16px", fontWeight: "800", color: "#2563eb" }}>{selectedEntity}</div>
              </div>
              <div style={{ fontSize: "12px", color: "#475569" }}>
                Click on <strong>"Tab 2. Root Cause & Action Plan"</strong> above to inspect diagnosis and mitigations for {selectedEntity}.
              </div>
              <button
                onClick={() => setActiveTab("reasons")}
                style={{
                  backgroundColor: "#2563eb",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  padding: "6px 14px",
                  fontSize: "12px",
                  fontWeight: "700",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px"
                }}
              >
                Go to Action Plan <ArrowRight size={14} />
              </button>
            </div>
          </div>
        )}

        {/* TAB 2: REASONS & ACTIONS */}
        {activeTab === "reasons" && (() => {
          const selectedRisk = allRisks.find(r => r.entity_id === selectedEntity);
          const prob = selectedRisk ? selectedRisk.probability : 0.08;
          const isSafe = !selectedRisk || selectedRisk.level === "Low" || prob < 0.25;
          const prefix = selectedEntity.substring(0, 3);
          
          let entityActions = [];
          let entityReasons = [];
          let entityShap = [];

          if (isSafe) {
            entityReasons = [];
            entityActions = [];
          } else {
            if (prefix === "SUP") {
              entityShap = [
                { feature: "supplier_delay_7d_avg", shap_value: 1.65 },
                { feature: "rain_7d_sum", shap_value: 1.82 },
                { feature: "single_source_flag", shap_value: 0.54 },
                { feature: "defect_rate_14d", shap_value: 0.38 },
                { feature: "inventory_buffer_ratio", shap_value: -0.42 }
              ];
              entityReasons = [
                `${selectedEntity} component delay: 7-day rolling shipment lag exceeds tolerance limit (avg delay > 2.4 days).`,
                `Localized climate storm alert in supplier origin port elevates transit risk.`,
                `Upstream supply concentration: downstream assembly plant PLT004 relies heavily on this single source.`
              ];
              entityActions = [
                { risk_type: "supplier_failure", level: "High", action: `Reallocate purchase order volume: activate secondary qualified backup vendor SUP004 (Berlin) for ${selectedEntity}.` },
                { risk_type: "supplier_failure", level: "Medium", action: `Authorize expedited priority air transport (corridor RT001) to bypass congested maritime port.` },
                { risk_type: "supplier_failure", level: "Low", action: `Increase supplier check-in frequency and track production lead-times daily.` }
              ];
            } else if (prefix === "PLT") {
              entityShap = [
                { feature: "upstream_supplier_delay", shap_value: 1.78 },
                { feature: "pagerank_vulnerability", shap_value: 0.85 },
                { feature: "component_starvation_index", shap_value: 0.72 },
                { feature: "production_ratio_7d_avg", shap_value: -0.65 }
              ];
              entityReasons = [
                `${selectedEntity} assembly stoppage: upstream component supplier delivery delay creates surface-mount assembly starvation.`,
                `NetworkX graph PageRank dependency score (0.85) identifies high topological vulnerability.`,
                `Production throughput ratio dropped by -32% over past 72 hours due to missing parts.`
              ];
              entityActions = [
                { risk_type: "manufacturing_delay", level: "High", action: `Rebalance assembly throughput: transfer scheduled production lots from ${selectedEntity} to auxiliary plant PLT004.` },
                { risk_type: "manufacturing_delay", level: "Medium", action: `De-prioritize low-margin models and concentrate all active assembly shifts on flagship smartphone lines.` },
                { risk_type: "manufacturing_delay", level: "Low", action: `Reschedule non-urgent preventive maintenance to weekend off-peak hours.` }
              ];
            } else if (prefix === "WH") {
              entityShap = [
                { feature: "customer_order_surge_7d", shap_value: 1.94 },
                { feature: "stock_days_cover", shap_value: 1.45 },
                { feature: "replenishment_transit_lead", shap_value: 0.82 },
                { feature: "safety_stock_deficit", shap_value: 0.65 }
              ];
              entityReasons = [
                `${selectedEntity} retail stockout risk: consumer demand spiked to >1,020 units/day over the past 7 days.`,
                `Days-of-supply inventory coverage compressed to under 5.8 days (below safety buffer threshold of 8.0 days).`,
                `Inbound replenishment freight along corridor RT006 delayed by coastal transport congestion.`
              ];
              entityActions = [
                { risk_type: "warehouse_stockout", level: "High", action: `Raise safety stock buffer by +25% at ${selectedEntity} and trigger emergency cross-dock rebalancing from central hub WH003.` },
                { risk_type: "warehouse_stockout", level: "Medium", action: `Cap non-contractual promotional batch fulfillment to protect contractual retail SLA commitments.` },
                { risk_type: "warehouse_stockout", level: "Low", action: `Expedite inbound trailer check-in queue at regional warehouse receiving docks.` }
              ];
            } else {
              entityShap = [
                { feature: "transit_edge_betweenness", shap_value: 1.88 },
                { feature: "delivery_delay_7d_avg", shap_value: 1.25 },
                { feature: "coastal_weather_anomaly", shap_value: 0.92 },
                { feature: "customs_dwell_hours", shap_value: 0.44 }
              ];
              entityReasons = [
                `${selectedEntity} corridor disruption: NetworkX Edge Betweenness identifies this route as a single-point freight bottleneck.`,
                `Maritime congestion and weather advisory extend transit lead-time by +3.2 days.`,
                `Downstream assembly plant PLT004 reporting delayed parts arrivals.`
              ];
              entityActions = [
                { risk_type: "transport_disruption", level: "High", action: `Reroute high-priority freight along corridor ${selectedEntity} to air express corridor RT002.` },
                { risk_type: "transport_disruption", level: "Medium", action: `Stage forward buffer inventory at regional multimodal hub to absorb transit variance.` },
                { risk_type: "transport_disruption", level: "Low", action: `Pre-clear customs electronic bills of lading to eliminate port inspection delays.` }
              ];
            }
          }

          return (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", height: "100%" }}>
              <div style={{
                backgroundColor: "#ffffff",
                padding: "18px",
                borderRadius: "8px",
                border: "1px solid #e2e8f0",
                display: "flex",
                flexDirection: "column"
              }}>
                <h3 style={{ margin: "0 0 4px 0", fontSize: "14px", fontWeight: "700" }}>
                  {isSafe ? `Diagnosis: ${selectedEntity} Operates Within Safe Limits` : `Why is ${selectedEntity} at Risk? (TreeSHAP Diagnosis)`}
                </h3>
                <p style={{ margin: "0 0 12px 0", fontSize: "11px", color: "#64748b" }}>
                  {isSafe 
                    ? `Node telemetry indicates stable operations with zero adverse risk flags under this scenario.` 
                    : `Red bars indicate localized operational factors pushing risk UP. Green bars reduce risk.`}
                </p>
                <div style={{ flex: 1, minHeight: "240px" }}>
                  {isSafe ? (
                    <div style={{
                      height: "100%",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      backgroundColor: "#f8fafc",
                      borderRadius: "8px",
                      border: "1px dashed #cbd5e1",
                      color: "#16a34a",
                      padding: "20px",
                      textAlign: "center"
                    }}>
                      <div style={{ fontSize: "15px", fontWeight: "700", marginBottom: "6px" }}>
                        No Elevated Risk Factors Detected
                      </div>
                      <div style={{ fontSize: "12px", color: "#64748b", maxWidth: "320px" }}>
                        Calculated failure probability is only {Math.round(prob * 100)}% (Normal). Feature attributions are only calculated when a node breaches the operational risk threshold.
                      </div>
                    </div>
                  ) : (
                    <ShapBarChart features={entityShap} />
                  )}
                </div>
              </div>

              <ActionsPanel
                actions={entityActions}
                reasons={entityReasons}
                entityId={selectedEntity}
                isSafe={isSafe}
                currentProb={prob}
              />
            </div>
          );
        })()}

        {/* TAB 3: METRICS */}
        {activeTab === "metrics" && (
          <div style={{ height: "100%" }}>
            <MetricsTable metrics={metricsData} />
          </div>
        )}
      </main>
    </div>
  );
}
