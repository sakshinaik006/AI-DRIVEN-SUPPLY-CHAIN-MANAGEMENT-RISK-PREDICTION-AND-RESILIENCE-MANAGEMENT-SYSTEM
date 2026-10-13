import React, { useState, useEffect } from "react";
import { RiskCard } from "./components/RiskCard";
import { ShapBarChart } from "./components/ShapBarChart";
import { NetworkScore } from "./components/NetworkScore";
import { ActionsPanel } from "./components/ActionsPanel";

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [source, setSource] = useState("api");
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        // Attempt to connect to FastAPI endpoint (Member 2)
        const res = await fetch("http://localhost:8000/api/risks", { signal: AbortSignal.timeout(2000) });
        if (!res.ok) throw new Error("API returned non-200");
        const json = await res.json();
        setData(json);
        setSource("Live FastAPI Backend");
      } catch (err) {
        // Fall back to static JSON in public/api_fallback.json
        try {
          const fallbackRes = await fetch("/api_fallback.json");
          const fallbackJson = await fallbackRes.json();
          setData(fallbackJson);
          setSource("Static Fallback (frontend/public/api_fallback.json)");
        } catch (fbErr) {
          setError("Failed to load dashboard data from API and static fallback.");
        }
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", fontFamily: "sans-serif" }}>
        <h3>Loading Supply Chain Resilience Dashboard...</h3>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "40px", color: "#dc2626", fontFamily: "sans-serif" }}>
        <h2>Dashboard Error</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: "1200px",
      margin: "0 auto",
      padding: "24px 20px",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
      backgroundColor: "#f8fafc",
      minHeight: "100vh"
    }}>
      {/* Header */}
      <header style={{ marginBottom: "24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", flexWrap: "wrap" }}>
          <h1 style={{ fontSize: "24px", fontWeight: "800", color: "#0f172a", margin: 0 }}>
            Smartphone Supply Chain Risk & Resilience Dashboard
          </h1>
          <span style={{ fontSize: "12px", color: "#64748b", marginTop: "4px" }}>
            Data source: <strong style={{ color: "#2563eb" }}>{source}</strong>
          </span>
        </div>
        <p style={{ fontSize: "14px", color: "#64748b", margin: "6px 0 0 0" }}>
          Predicting 7-day ahead supplier, manufacturing, stockout, and transport risks with TreeSHAP explainability.
        </p>
      </header>

      {/* Top 4 Risk Cards */}
      <section style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        gap: "16px",
        marginBottom: "24px"
      }}>
        {data?.risks?.map((risk, index) => (
          <RiskCard key={index} item={risk} />
        ))}
      </section>

      {/* Network Score & Actions */}
      <section style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
        gap: "20px",
        marginBottom: "24px"
      }}>
        <NetworkScore
          score={data?.network_score}
          level={data?.network_level}
          weights={data?.weights_assumption}
        />
        <ActionsPanel
          actions={data?.actions}
          reasons={data?.reasons}
        />
      </section>

      {/* SHAP Chart & Model Explainability */}
      <section style={{
        backgroundColor: "#ffffff",
        padding: "20px",
        borderRadius: "8px",
        border: "1px solid #e2e8f0",
        boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
      }}>
        <h3 style={{ margin: "0 0 6px 0", fontSize: "16px", color: "#1e293b" }}>
          Feature Attribution & Risk Drivers (TreeSHAP)
        </h3>
        <p style={{ margin: "0 0 16px 0", fontSize: "13px", color: "#64748b" }}>
          Positive values (red) elevate failure probability; negative values (green) reduce risk.
        </p>
        <ShapBarChart features={data?.shap_features} />
      </section>
    </div>
  );
}
