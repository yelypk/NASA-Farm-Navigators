const API = (import.meta.env.VITE_API_BASE || 'http://localhost:8080').replace(/\/$/, '')

export async function newGame(region='california'){
  const res = await fetch(`${API}/game/new`, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({region})
  })
  return await res.json()
}

export async function getState(id){
  const res = await fetch(`${API}/game/${id}/state`)
  return await res.json()
}

export async function postPlan(id, cells){
  const res = await fetch(`${API}/game/${id}/plan`, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({cells})
  })
  return await res.json()
}

export async function tick(id){
  const res = await fetch(`${API}/game/${id}/tick`, {method:'POST'})
  return await res.json()
}

export function rasterUrl(id, layer='ndvi'){
  return `${API}/game/${id}/raster?layer=${layer}`
}
