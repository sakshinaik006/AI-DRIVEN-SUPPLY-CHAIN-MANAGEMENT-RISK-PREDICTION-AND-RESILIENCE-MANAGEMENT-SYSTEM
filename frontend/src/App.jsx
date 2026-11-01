import React, { useState, useEffect } from "react";
import { 
  LayoutDashboard, 
  Activity, 
  Network, 
  BrainCircuit, 
  Sparkles, 
  Calendar, 
  Clock, 
  Play, 
  Pause,
  AlertCircle
} from "lucide-react";

import { OverviewPage } from "./components/OverviewPage";
import { RiskMonitoringPage } from "./components/RiskMonitoringPage";
import { SupplyChainMapPage } from "./components/SupplyChainMapPage";
import { AIInsightsPage } from "./components/AIInsightsPage";
import { RecommendationsPage } from "./components/RecommendationsPage";

export default function App() {
  const [activeTab, setActiveTab] = useState("overview"); // "overview" | "monitoring" | "map" | "insights" | "recommendations"
  const [selectedDate, setSelectedDate] = useState("2025-08-15");
  const [selectedEntityId, setSelectedEntityId] = useState("SUP001");
  const [monitoringCategory, setMonitoringCategory] = useState("supplier");
  const [isPlaying, setIsPlaying] = useState(false);
  const [allData, setAllData] = useState(null);
  const [loading, setLoading] = useState(true);

  // 3 Valid Historical & Disruption Scenarios
  const scenarioOptions = [
    { label: "Scenario 1: Normal Operations (Apr 15)", value: "2025-04-15" },
    { label: "Scenario 2: Typhoon & Supply Starvation (Aug 15)", value: "2025-08-15" },
    { label: "Scenario 3: Retail Stockout Surge (Oct 24)", value: "2025-10-24" }
  ];

  // Load integrated data from backend or local fallback cache
  async function loadControlTowerData() {
    setLoading(true);
    try {
      const res = await fetch("/control_tower_data.json");
      if (res.ok) {
        const json = await res.json();
        setAllData(json);
      } else {
        throw new Error("Local json unavailable");
      }
    } catch (e) {
      console.warn("Using inline fallback structure:", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadControlTowerData();
  }, []);

  // Demo playback loop across the 3 scenarios
  useEffect(() => {
    let timer = null;
    if (isPlaying) {
      let idx = 0;
      timer = setInterval(() => {
        idx = (idx + 1) % scenarioOptions.length;
        setSelectedDate(scenarioOptions[idx].value);
      }, 4500);
    } else {
      clearInterval(timer);
    }
    return () => clearInterval(timer);
  }, [isPlaying]);

  const currentScenarioData = allData?.scenario_data?.[selectedDate] || null;

  function handleNavigateTab(tabName, params = {}) {
    setActiveTab(tabName);
    if (params.category) setMonitoringCategory(params.category);
    if (params.entityId) setSelectedEntityId(params.entityId);
  }

  const navItems = [
    { id: "overview", label: "1. Overview", icon: <LayoutDashboard size={16} /> },
    { id: "monitoring", label: "2. Risk Monitoring", icon: <Activity size={16} /> },
    { id: "map", label: "3. Supply Chain Map", icon: <Network size={16} /> },
    { id: "insights", label: "4. AI Insights", icon: <BrainCircuit size={16} /> },
    { id: "recommendations", label: "5. Recommendations", icon: <Sparkles size={16} /> }
  ];

  return (
    <div style={{
      display: "flex",
      minHeight: "100vh",
      backgroundColor: "#0b1329", // Dark Navy
      color: "#f8fafc",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    }}>
      {/* 1. LEFT SIDEBAR NAVIGATION */}
      <aside style={{
        width: "250px",
        backgroundColor: "#0f172a",
        borderRight: "1px solid #1e293b",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        flexShrink: 0
      }}>
        <div>
          {/* Dashboard Title & Subtitle */}
          <div style={{ padding: "20px 18px", borderBottom: "1px solid #1e293b" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
              <div style={{
                backgroundColor: "#0284c7",
                borderRadius: "6px",
                width: "28px",
                height: "28px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#ffffff"
              }}>
                <Network size={18} />
              </div>
              <h1 style={{ fontSize: "15px", fontWeight: "800", margin: 0, color: "#f8fafc", letterSpacing: "0.2px" }}>
                Supply Chain Control Tower
              </h1>
            </div>
            <p style={{ fontSize: "11px", color: "#94a3b8", margin: "4px 0 0 0", lineHeight: "1.4" }}>
              Monitor risks. Predict disruptions. Make smarter decisions.
            </p>
          </div>

          {/* Navigation Links */}
          <nav style={{ padding: "16px 12px", display: "flex", flexDirection: "column", gap: "6px" }}>
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    width: "100%",
                    padding: "10px 14px",
                    borderRadius: "6px",
                    border: "none",
                    backgroundColor: isActive ? "#0284c7" : "transparent",
                    color: isActive ? "#ffffff" : "#94a3b8",
                    fontSize: "13px",
                    fontWeight: isActive ? "700" : "500",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "all 0.12s ease"
                  }}
                >
                  <span style={{ color: isActive ? "#ffffff" : "#38bdf8" }}>{item.icon}</span>
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer Info */}
        <div style={{ padding: "16px", borderTop: "1px solid #1e293b", fontSize: "11px", color: "#64748b" }}>
          <div>Prediction Horizon: <span style={{ color: "#38bdf8", fontWeight: "600" }}>7 Days</span></div>
          <div style={{ marginTop: "4px" }}>Multi-Target CatBoost + EIF</div>
          <div style={{ marginTop: "2px" }}>27 Monitored Physical Assets</div>
        </div>
      </aside>

      {/* 2. MAIN CONTENT AREA */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0, overflowY: "auto" }}>
        {/* Top Header Bar */}
        <header style={{
          backgroundColor: "#0f172a",
          borderBottom: "1px solid #1e293b",
          padding: "12px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexShrink: 0
        }}>
          <div>
            <div style={{ fontSize: "13px", fontWeight: "700", color: "#f8fafc" }}>
              {navItems.find(n => n.id === activeTab)?.label}
            </div>
            <div style={{ fontSize: "11px", color: "#94a3b8" }}>
              Active Scenario: <span style={{ color: "#38bdf8", fontWeight: "600" }}>
                {scenarioOptions.find(s => s.value === selectedDate)?.label}
              </span>
            </div>
          </div>

          {/* Scenario Selector & Demo Playback */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              backgroundColor: "#1e293b",
              padding: "4px 10px",
              borderRadius: "6px",
              border: "1px solid #334155"
            }}>
              <Calendar size={13} color="#94a3b8" />
              <select
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                style={{
                  backgroundColor: "transparent",
                  color: "#38bdf8",
                  border: "none",
                  fontSize: "12px",
                  fontWeight: "700",
                  cursor: "pointer",
                  outline: "none"
                }}
              >
                {scenarioOptions.map(opt => (
                  <option key={opt.value} value={opt.value} style={{ backgroundColor: "#0f172a", color: "#f8fafc" }}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={() => setIsPlaying(!isPlaying)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "5px",
                padding: "6px 12px",
                borderRadius: "6px",
                border: "1px solid #334155",
                backgroundColor: isPlaying ? "#0284c7" : "#1e293b",
                color: "#ffffff",
                fontSize: "11px",
                fontWeight: "700",
                cursor: "pointer"
              }}
            >
              {isPlaying ? <Pause size={12} /> : <Play size={12} />}
              {isPlaying ? "Pause Demo" : "Play Scenarios"}
            </button>
          </div>
        </header>

        {/* Page Content Body */}
        <main style={{ padding: "20px 24px", flex: 1 }}>
          {loading ? (
            <div style={{ textAlign: "center", padding: "60px", color: "#94a3b8" }}>
              Loading Supply Chain Control Tower...
            </div>
          ) : (
            <>
              {activeTab === "overview" && (
                <OverviewPage 
                  data={currentScenarioData}
                  onSelectEntity={setSelectedEntityId}
                  onNavigateTab={handleNavigateTab}
                />
              )}

              {activeTab === "monitoring" && (
                <RiskMonitoringPage 
                  data={currentScenarioData}
                  initialCategory={monitoringCategory}
                  onSelectEntity={setSelectedEntityId}
                  onNavigateTab={handleNavigateTab}
                />
              )}

              {activeTab === "map" && (
                <SupplyChainMapPage 
                  data={currentScenarioData}
                  selectedEntityId={selectedEntityId}
                  onSelectEntity={setSelectedEntityId}
                  onNavigateTab={handleNavigateTab}
                />
              )}

              {activeTab === "insights" && (
                <AIInsightsPage 
                  data={currentScenarioData}
                  selectedEntityId={selectedEntityId}
                  onSelectEntity={setSelectedEntityId}
                  onNavigateTab={handleNavigateTab}
                />
              )}

              {activeTab === "recommendations" && (
                <RecommendationsPage 
                  data={currentScenarioData}
                  onSelectEntity={setSelectedEntityId}
                  onNavigateTab={handleNavigateTab}
                />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
