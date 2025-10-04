const API = "http://localhost:8000";

export async function listRegions() {
  const r = await fetch(`${API}/regions`);
  return r.json();
}

export async function fetchTiles(region, year) {
  const r = await fetch(`${API}/regions/${region}/year/${year}`);
  return r.json();
}

export async function simulateTurn(runId, region, year, decisions) {
  const r = await fetch(`${API}/simulate/turn`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId, region_id: region, year, decisions })
  });
  return r.json();
}

export async function fetchSummary(runId) {
  const r = await fetch(`${API}/summary/${runId}`);
  return r.json();
}
