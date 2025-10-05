const API_BASE = import.meta?.env?.VITE_API_BASE || window.location.origin;

async function j(method, url, body) {
  const res = await fetch(`${API_BASE}${url}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return await res.json();
  return await res.arrayBuffer();
}

export const api = {
  // Game
  newGame: (scenario) => j("POST", "/game/new", { scenario }),
  state: (id) => j("GET", `/game/${id}/state`),

  // Plans
  planCrops: (id, payload) => j("POST", `/farm/${id}/plan/crops`, payload),
  planLivestock: (id, payload) => j("POST", `/farm/${id}/plan/livestock`, payload),
  planDrainage: (id, payload) => j("POST", `/farm/${id}/plan/drainage`, payload),
  planPests: (id, payload) => j("POST", `/farm/${id}/plan/pests`, payload),
  planLegacy: (id, payload) => j("POST", `/farm/${id}/plan`, payload), // deprecated

  // Tick & events
  tick: (id) => j("POST", `/tick/${id}`),
  events: (id) => j("GET", `/events/${id}/season`),
  resolveEvent: (id, key, choice) => j("POST", `/events/${id}/${key}/resolve`, choice),

  // Layers (PNG as ArrayBuffer)
  regionLayer: async (id, layer, season) => j("GET", `/region/${id}/layer?layer=${layer}&season=${season}`),
  farmRaster: async (id, layer, season) => j("GET", `/farm/${id}/raster?layer=${layer}&season=${season}`),

  // Finance
  loan: (id, req) => j("POST", `/finance/${id}/loan`, req),
  insure: (id, req) => j("POST", `/finance/${id}/insure`, req),
  financeReport: (id, year) => j("GET", `/finance/${id}/report${year?`?year=${year}`:''}`),
};

// --- LUT utilities ---
// Apply a color LUT to a grayscale PNG (ArrayBuffer) and return ImageData
export async function applyLUT(arrayBuffer, palette = "viridis") {
  const blob = new Blob([arrayBuffer], { type: "image/png" });
  const img = await createImageBitmap(blob);
  const canvas = new OffscreenCanvas(img.width, img.height);
  const ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0);
  const imageData = ctx.getImageData(0, 0, img.width, img.height);
  const data = imageData.data;

  const lut = (name) => {
    if (name === "viridis") return viridisLUT();
    if (name === "magma") return magmaLUT();
    return viridisLUT();
  };
  const L = lut(palette);
  for (let i = 0; i < data.length; i += 4) {
    const v = data[i]; // R == G == B in grayscale
    const c = L[v];
    data[i] = c[0];
    data[i+1] = c[1];
    data[i+2] = c[2];
    // alpha stays as is
  }
  ctx.putImageData(imageData, 0, 0);
  return canvas.transferToImageBitmap();
}

// Simple 256-color viridis and magma approximations
function viridisLUT() {
  const out = new Array(256);
  for (let i = 0; i < 256; i++) {
    const t = i / 255;
    // polynomial approx
    const r = Math.round(68 + 190*t - 180*t*t);
    const g = Math.round(1 + 180*t);
    const b = Math.round(84 + 120*(1-t));
    out[i] = [clamp(r), clamp(g), clamp(b)];
  }
  return out;
}
function magmaLUT() {
  const out = new Array(256);
  for (let i = 0; i < 256; i++) {
    const t = i / 255;
    const r = Math.round(30 + 225*Math.pow(t, 0.9));
    const g = Math.round(5 + 60*Math.pow(t, 1.2));
    const b = Math.round(35 + 30*Math.pow(1-t, 2.0));
    out[i] = [clamp(r), clamp(g), clamp(b)];
  }
  return out;
}
function clamp(x){ return Math.max(0, Math.min(255, x|0)); }