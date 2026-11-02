/**
 * Service Layer: Unified API & Fallback Client
 * Communicates with FastAPI backend (http://localhost:8000)
 * Falls back gracefully to verified static data bundled in public/ if API server is offline.
 */

const API_BASE = "http://localhost:8000/api";

export async function fetchControlTowerData() {
  try {
    const res = await fetch("/control_tower_data.json");
    if (res.ok) {
      return await res.json();
    }
    throw new Error("Local control tower data not found");
  } catch (err) {
    console.warn("Could not load /control_tower_data.json, trying /api_fallback.json", err);
    const fallbackRes = await fetch("/api_fallback.json");
    return await fallbackRes.json();
  }
}

export async function fetchLiveRisks(date = null) {
  try {
    const url = date ? `${API_BASE}/risks?date=${date}` : `${API_BASE}/risks`;
    const res = await fetch(url, { signal: AbortSignal.timeout(1500) });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    // API server offline; fallback to static data
  }
  return null;
}

export async function fetchNetworkScore(date = null) {
  try {
    const url = date ? `${API_BASE}/network-score?date=${date}` : `${API_BASE}/network-score`;
    const res = await fetch(url, { signal: AbortSignal.timeout(1500) });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    // Offline
  }
  return null;
}

export async function fetchEntityReasons(entityId, riskType) {
  try {
    const res = await fetch(
      `${API_BASE}/reasons?entity_id=${encodeURIComponent(entityId)}&risk_type=${encodeURIComponent(riskType)}`,
      { signal: AbortSignal.timeout(1500) }
    );
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    // Offline
  }
  return null;
}

export async function fetchDemos() {
  try {
    const res = await fetch(`${API_BASE}/demos`, { signal: AbortSignal.timeout(1500) });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    // Offline
  }
  return null;
}
