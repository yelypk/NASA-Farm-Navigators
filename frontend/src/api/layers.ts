// frontend/src/api/layers.ts
const API = (import.meta.env.VITE_API_BASE ?? window.location.origin).replace(/\/$/, "");

export async function fetchRegionPng(regionId: string, layer: string, season: number): Promise<HTMLImageElement> {
  const url = `${API}/region/${regionId}/layer?layer=${layer}&season=${season}`;
  const blob = await fetch(url).then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status} for ${url}`);
    return r.blob();
  });

  const bitmap = await createImageBitmap(blob);
  const c = document.createElement("canvas");
  c.width = bitmap.width; c.height = bitmap.height;
  const ctx = c.getContext("2d")!;
  ctx.drawImage(bitmap, 0, 0);

  const img = new Image();
  img.src = c.toDataURL("image/png");
  return new Promise<HTMLImageElement>(res => (img.onload = () => res(img)));
}
