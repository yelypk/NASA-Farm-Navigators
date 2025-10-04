import { GameState } from '../state'

// Можно задать базовый URL через .env: VITE_API_BASE=https://your-api
const envBase = import.meta.env.VITE_API_BASE || 'http://nasa-farm-navigators-production.up.railway.app'

// На проде по умолчанию используем тот же домен, где открыт фронт.
// Поле в HUD (GameState.apiBase) имеет наивысший приоритет.
export function apiBase() {
  const ui = (GameState.apiBase && GameState.apiBase.trim()) || ''
  const sameOrigin = (typeof window !== 'undefined' ? window.location.origin : '')
  return ui || envBase || sameOrigin
}

async function jsonFetch(url, options = {}) {
  const r = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function ensureSave(scenario = 'CA_SanJoaquin_West') {
  if (GameState.saveId) return GameState.saveId
  const out = await jsonFetch(`${apiBase()}/game/new`, {
    method: 'POST',
    body: JSON.stringify({ scenario })
  })
  GameState.saveId = out.save_id || out.saveId
  return GameState.saveId
}

export function regionPngUrl(layer = 'ndvi', season = 0) {
  return `${apiBase()}/region/${GameState.saveId}/layer?layer=${layer}&season=${season}&_=${Date.now()}`
}

export function farmPngUrl(layer = 'soil') {
  return `${apiBase()}/farm/${GameState.saveId}/raster?layer=${layer}&_=${Date.now()}`
}

export async function setPlan({ irrigation = 0.0, cover = false, mulch = false }) {
  const payload = {
    crops: Array.from({ length: 40 }, () => Array.from({ length: 40 }, () => 'fallow')),
    irrigation_rate: irrigation,
    practices: { cover_crop: cover ? 1 : 0, mulch: mulch ? 1 : 0 }
  }
  return jsonFetch(`${apiBase()}/farm/${GameState.saveId}/plan`, {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export async function tick() {
  return jsonFetch(`${apiBase()}/tick/${GameState.saveId}`, { method: 'POST' })
}

export async function farmState() {
  return jsonFetch(`${apiBase()}/farm/${GameState.saveId}/state`)
}
