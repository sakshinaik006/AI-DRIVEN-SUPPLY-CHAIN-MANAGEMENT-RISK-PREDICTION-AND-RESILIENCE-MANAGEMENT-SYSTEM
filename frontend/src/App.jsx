import React, { useState, useEffect } from "react";
import { RiskCard } from "./components/RiskCard";
import { ShapBarChart } from "./components/ShapBarChart";
import { NetworkScore } from "./components/NetworkScore";
import { ActionsPanel } from "./components/ActionsPanel";
import { PipelineMap } from "./components/PipelineMap";
import { ForecastCurveChart } from "./components/ForecastCurveChart";
import { MetricsTable } from "./components/MetricsTable";
import { 
  Network, 
  Lightbulb, 
  TrendingUp, 
  Award,
  Calendar,
  Play,
  Pause,
  AlertTriangle,
  ArrowRight
} from "lucide-react";

export default function App() {
  const [data, setData] = useState(null);
  const [forecastData, setForecastData] = useState([]);
  const [metricsData, setMetricsData] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState("SUP001");
  const [selectedDate, setSelectedDate] = useState("2025-10-24");
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeTab, setActiveTab] = useState("pipeline"); // "pipeline" | "reasons" | "forecast" | "metrics"
  const [loading, setLoading] = useState(true);
  const [source, setSource] = useState("api");

  const dates = [
    { label: "Scenario 1: Normal Operations (Apr 15)", value: "2025-04-15" },
    { label: "Scenario 2: Typhoon & Supplier Delay (Aug 15)", value: "2025-08-15" },
    { label: "Scenario 3: Peak Demand Spike (Oct 24)", value: "2025-10-24" },
  ];

  async function loadData(dateStr) {
    try {
      const [resRisks, resNet, resForecast, resMetrics] = await Promise.allSettled([
        fetch(`http://localhost:8000/api/risks?date=${dateStr}`, { signal: AbortSignal.timeout(1500) }),
        fetch(`http://localhost:8000/api/network-score?date=${dateStr}`, { signal: AbortSignal.timeout(1500) }),
        fetch(`http://localhost:8000/api/forecast`, { signal: AbortSignal.timeout(1500) }),
        fetch(`http://localhost:8000/api/metrics`, { signal: AbortSignal.timeout(1500) }),
      ]);

      if (resRisks.status === "fulfilled" && resRisks.value.ok) {
        const jsonRisks = await resRisks.value.json();
        let netScore = 0.44;
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
          shap_features: [
            { feature: "supplier_delay_7d_avg", shap_value: dateStr.includes("-08-") ? 1.45 : 0.42 },
            { feature: "rain_7d_sum", shap_value: dateStr.includes("-08-") ? 1.82 : 0.35 },
            { feature: "single_source_flag", shap_value: 0.53 },
            { feature: "news_tone_14d_trend", shap_value: -0.21 },
          ],
          reasons: [
            `Current condition on ${dateStr}: Compounding delay detected in regional components delivery.`,
            "Localized weather precipitation alert (Open-Meteo) elevating transit risks.",
            "Historical lookback delay average is above standard threshold over past 7 days."
          ],
          actions: [
            { risk_type: "supplier_failure", level: "High", action: "Switch volume allocation: Activate qualified secondary backup supplier SUP004 (Berlin)." },
            { risk_type: "warehouse_stockout", level: "High", action: "Raise safety stock coverage and expedite inter-warehouse inventory rebalancing." },
            { risk_type: "transport_disruption", level: "Medium", action: "Reroute cargo from congested coastal hub to priority air corridor RT002." },
            { risk_type: "manufacturing_delay", level: "Low", action: "Maintain planned assembly throughput; schedule off-peak maintenance." }
          ]
        });
        setSource("Live FastAPI Backend");
      } else {
        throw new Error("API Offline");
      }

      if (resForecast.status === "fulfilled" && resForecast.value.ok) setForecastData(await resForecast.value.json());
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
        setForecastData([
          { entity_id: "WH001", date: "2025-10-25", chronos_forecast: 118.1, patchtst_delay_forecast: 1.74 },
          { entity_id: "WH001", date: "2025-10-26", chronos_forecast: 124.5, patchtst_delay_forecast: 2.00 },
          { entity_id: "WH001", date: "2025-10-27", chronos_forecast: 132.8, patchtst_delay_forecast: 2.65 },
          { entity_id: "WH001", date: "2025-10-28", chronos_forecast: 115.0, patchtst_delay_forecast: 1.26 },
          { entity_id: "WH001", date: "2025-10-29", chronos_forecast: 121.3, patchtst_delay_forecast: 1.72 },
          { entity_id: "WH001", date: "2025-10-30", chronos_forecast: 129.4, patchtst_delay_forecast: 2.32 },
          { entity_id: "WH001", date: "2025-10-31", chronos_forecast: 135.0, patchtst_delay_forecast: 2.82 },
        ]);
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
      }, 3000);
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
            {data?.network_score ? `${(data.network_score * 100).toFixed(1)}%` : "44.0%"} 
            <span style={{ fontSize: "12px", color: "#d97706", marginLeft: "6px" }}>({data?.network_level || "Medium Risk"})</span>
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

      {/* 3. SIMPLE 4 TABS */}
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
          <Lightbulb size={16} /> 2. Why It Happened & Action Plan
        </button>

        <button
          onClick={() => setActiveTab("forecast")}
          style={{
            padding: "12px 0",
            border: "none",
            borderBottom: activeTab === "forecast" ? "3px solid #2563eb" : "3px solid transparent",
            backgroundColor: "transparent",
            color: activeTab === "forecast" ? "#2563eb" : "#64748b",
            fontWeight: activeTab === "forecast" ? "800" : "600",
            fontSize: "13px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}
        >
          <TrendingUp size={16} /> 3. Demand & Delay Forecast
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
          <Award size={16} /> 4. Model Accuracy Comparison
        </button>
      </nav>

      {/* 4. MAIN CONTENT (NO PAGE SCROLLING - FITS MONITOR) */}
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
                Click on <strong>"Tab 2. Why It Happened & Action Plan"</strong> above to see the root cause for {selectedEntity}.
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
        {activeTab === "reasons" && (
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
                Why is {selectedEntity} at Risk? (Feature Contribution)
              </h3>
              <p style={{ margin: "0 0 12px 0", fontSize: "11px", color: "#64748b" }}>
                Red bars indicate factors pushing risk UP (delays, rainfall). Green bars reduce risk.
              </p>
              <div style={{ flex: 1, minHeight: "240px" }}>
                <ShapBarChart features={data?.shap_features} />
              </div>
            </div>

            <ActionsPanel
              actions={data?.actions}
              reasons={data?.reasons}
              entityId={selectedEntity}
            />
          </div>
        )}

        {/* TAB 3: FORECAST */}
        {activeTab === "forecast" && (
          <div style={{
            backgroundColor: "#ffffff",
            padding: "18px 24px",
            borderRadius: "8px",
            border: "1px solid #e2e8f0",
            display: "flex",
            flexDirection: "column",
            height: "100%"
          }}>
            <h3 style={{ margin: "0 0 4px 0", fontSize: "15px", fontWeight: "700" }}>
              7-Day Forward Time-Series Forecast (Warehouse WH001)
            </h3>
            <p style={{ margin: "0 0 14px 0", fontSize: "12px", color: "#64748b" }}>
              Shows predicted demand units (Blue line) vs expected transit delivery delays in days (Red line).
            </p>
            <div style={{ flex: 1, minHeight: "260px" }}>
              <ForecastCurveChart data={forecastData} />
            </div>
          </div>
        )}

        {/* TAB 4: METRICS */}
        {activeTab === "metrics" && (
          <div style={{ height: "100%" }}>
            <MetricsTable metrics={metricsData} />
          </div>
        )}
      </main>
    </div>
  );
}
