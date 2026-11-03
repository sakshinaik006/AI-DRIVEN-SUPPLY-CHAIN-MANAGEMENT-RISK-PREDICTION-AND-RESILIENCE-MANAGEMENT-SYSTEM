import React, { useState, useEffect, useRef } from "react";
import { 
  LayoutDashboard, 
  BarChart3, 
  ShieldAlert, 
  ListChecks 
} from "lucide-react";

import { ExecutiveOverview } from "./components/ExecutiveOverview";
import { RiskAnalysis } from "./components/RiskAnalysis";
import { RiskFactorsResilience } from "./components/RiskFactorsResilience";
import { Recommendations } from "./components/Recommendations";
import { fetchControlTowerData } from "./services/api";

export default function App() {
  const [activeTab, setActiveTab] = useState("overview"); // "overview" | "analysis" | "factors" | "recommendations"
  const [selectedDate, setSelectedDate] = useState("2025-08-15");
  const [selectedEntityId, setSelectedEntityId] = useState("SUP001");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [dataPayload, setDataPayload] = useState(null);
  const [loading, setLoading] = useState(true);

  // 3 Valid Historical & Benchmark Observation Dates
  const dateOptions = [
    { label: "Normal Operations (15 Apr 2025)", value: "2025-04-15" },
    { label: "Typhoon & Supply Starvation (15 Aug 2025)", value: "2025-08-15" },
    { label: "Retail Stockout Peak (24 Oct 2025)", value: "2025-10-24" }
  ];

  useEffect(() => {
    async function initData() {
      setLoading(true);
      const data = await fetchControlTowerData();
      setDataPayload(data);
      setLoading(false);
    }
    initData();
  }, []);

  const mainContentRef = useRef(null);

  const scrollToTop = () => {
    if (mainContentRef.current) {
      mainContentRef.current.scrollTop = 0;
    }
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  };

  useEffect(() => {
    scrollToTop();
    const rafId = requestAnimationFrame(scrollToTop);
    const timer = setTimeout(scrollToTop, 20);
    return () => {
      cancelAnimationFrame(rafId);
      clearTimeout(timer);
    };
  }, [activeTab]);

  const scenarioData = dataPayload?.scenario_data?.[selectedDate] || null;

  function handleNavigateToRiskAnalysis(categoryKey = null, entityId = null) {
    setActiveTab("analysis");
    if (categoryKey) setSelectedCategory(categoryKey);
    if (entityId) setSelectedEntityId(entityId);
    scrollToTop();
  }

  function handleNavigateToFactors(entityId = null) {
    setActiveTab("factors");
    if (entityId) setSelectedEntityId(entityId);
    scrollToTop();
  }

  function handleNavigateToRecommendations(entityId = null) {
    setActiveTab("recommendations");
    if (entityId) setSelectedEntityId(entityId);
    scrollToTop();
  }

  const navItems = [
    { id: "overview", label: "Executive Overview", icon: <LayoutDashboard size={17} /> },
    { id: "analysis", label: "Risk Analysis", icon: <BarChart3 size={17} /> },
    { id: "factors", label: "Risk Factors & Resilience", icon: <ShieldAlert size={17} /> },
    { id: "recommendations", label: "Recommendations", icon: <ListChecks size={17} /> },
  ];

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        maxHeight: "100vh",
        overflow: "hidden",
        backgroundColor: "var(--bg-app)",
        color: "var(--text-primary)",
      }}
    >
      {/* COMPACT LEFT SIDEBAR */}
      <aside
        style={{
          width: "240px",
          minWidth: "240px",
          backgroundColor: "var(--bg-surface)",
          borderRight: "1px solid var(--border-light)",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        <div>
          {/* Brand header */}
          <div
            style={{
              padding: "20px 18px",
              borderBottom: "1px solid var(--border-light)",
            }}
          >
            <div style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.8px", color: "var(--accent-teal)" }}>
              Supply Chain Resilience
            </div>
            <div style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", marginTop: "2px" }}>
              Risk Control Tower
            </div>
          </div>

          {/* Navigation items */}
          <nav style={{ padding: "12px 10px", display: "flex", flexDirection: "column", gap: "4px" }}>
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    scrollToTop();
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    padding: "9px 12px",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "13px",
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? "var(--accent-teal)" : "var(--text-secondary)",
                    backgroundColor: isActive ? "var(--accent-teal-subtle)" : "transparent",
                    border: isActive ? "1px solid var(--accent-teal-border)" : "1px solid transparent",
                    textAlign: "left",
                    width: "100%",
                    transition: "all 0.15s ease",
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) e.currentTarget.style.backgroundColor = "var(--bg-subtle)";
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) e.currentTarget.style.backgroundColor = "transparent";
                  }}
                >
                  <span style={{ color: isActive ? "var(--accent-teal)" : "var(--text-muted)" }}>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Footer info in sidebar */}
        <div
          style={{
            padding: "16px",
            borderTop: "1px solid var(--border-light)",
            fontSize: "11px",
            color: "var(--text-muted)",
          }}
        >
          <div style={{ fontWeight: 600, color: "var(--text-secondary)" }}>
            Multi-Tier Smartphone Network
          </div>
          <div style={{ marginTop: "2px" }}>
            27 Entities • 7-Day Lookahead
          </div>
          <div style={{ marginTop: "6px", display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "6px", height: "6px", borderRadius: "50%", backgroundColor: "#16a34a" }} />
            <span style={{ color: "var(--text-secondary)", fontWeight: 500 }}>System Active</span>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main
        ref={mainContentRef}
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minWidth: 0,
          height: "100%",
          overflowY: "auto",
        }}
      >
        {/* Top bar */}
        <header
          style={{
            height: "54px",
            padding: "0 28px",
            backgroundColor: "var(--bg-surface)",
            borderBottom: "1px solid var(--border-light)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ fontSize: "13px", color: "var(--text-muted)" }}>
            Executive Dashboard /{" "}
            <span style={{ color: "var(--text-primary)", fontWeight: 500 }}>
              {navItems.find((n) => n.id === activeTab)?.label}
            </span>
          </div>
        </header>

        {/* Page Content */}
        <div style={{ padding: "24px 28px", maxWidth: "1200px", width: "100%", margin: "0 auto" }}>
          {loading ? (
            <div style={{ padding: "32px", color: "var(--text-muted)", fontSize: "13px" }}>
              Loading dashboard parameters...
            </div>
          ) : (
            <>
              {activeTab === "overview" && (
                <ExecutiveOverview
                  scenarioData={scenarioData}
                  selectedDate={selectedDate}
                  onSelectDate={setSelectedDate}
                  dateOptions={dateOptions}
                  onNavigateToRiskAnalysis={handleNavigateToRiskAnalysis}
                />
              )}

              {activeTab === "analysis" && (
                <RiskAnalysis
                  scenarioData={scenarioData}
                  selectedCategory={selectedCategory}
                  selectedEntityId={selectedEntityId}
                  onNavigateToFactors={handleNavigateToFactors}
                  onNavigateToRecommendations={handleNavigateToRecommendations}
                />
              )}

              {activeTab === "factors" && (
                <RiskFactorsResilience
                  scenarioData={scenarioData}
                  selectedEntityId={selectedEntityId}
                  onNavigateToRecommendations={handleNavigateToRecommendations}
                />
              )}

              {activeTab === "recommendations" && (
                <Recommendations
                  scenarioData={scenarioData}
                  selectedEntityId={selectedEntityId}
                />
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
