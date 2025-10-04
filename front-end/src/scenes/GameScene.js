import { fetchTiles, simulateTurn } from "../api/client.js";

export default class GameScene extends Phaser.Scene {
  constructor() { super("GameScene"); }

  init(data) {
    this.region = data.region; this.years = data.years; this.yearIdx = 0;
    this.runId = Math.random().toString(36).slice(2);
    this.layerName = "ndvi";
    this.irrigate = new Set();
  }

  async create() {
    await this.loadYear();
    document.getElementById("btn-ndvi").onclick = () => this.drawLayer("ndvi");
    document.getElementById("btn-soil").onclick = () => this.drawLayer("soil_moisture");
    document.getElementById("btn-precip").onclick = () => this.drawLayer("precip");
    document.getElementById("btn-temp").onclick = () => this.drawLayer("temp");
    document.getElementById("btn-wind").onclick = () => this.drawLayer("wind");
    document.getElementById("btn-irrigate").onclick = () => this.pickRandomIrrigation();
    document.getElementById("btn-next").onclick = () => this.nextTurn();

    this.input.on("pointerdown", (p) => {
      const {x,y} = p.position;
      const cell = this.xyToCell(x, y);
      if (cell !== null) {
        if (this.irrigate.has(cell)) this.irrigate.delete(cell); else this.irrigate.add(cell);
        this.drawOverlay();
      }
    });
  }

  async loadYear() {
    const year = this.years[this.yearIdx];
    this.tiles = await fetchTiles(this.region, year);
    this.drawLayer(this.layerName);
    this.drawOverlay();
    this.add.text(12, 12, `${this.region} • ${year}`, { fontFamily: "monospace", fontSize: 16, color: "#9fc"});
  }

  drawLayer(name) {
    this.layerName = name;
    if (this.graphics) this.graphics.clear();
    const { w, h } = this.tiles;
    const data = this.tiles[name];
    const g = this.add.graphics();
    const cellSize = Math.floor(Math.min(this.scale.width, this.scale.height) / Math.max(w, h));
    g.clear();
    for (let i=0; i<data.length; i++) {
      const v = data[i];
      const col = Math.floor(v * 255);
      const x = (i % w) * cellSize;
      const y = Math.floor(i / w) * cellSize + 48;
      g.fillStyle((col<<16) | (col<<8) | col, 1);
      g.fillRect(x, y, cellSize-1, cellSize-1);
    }
    this.graphics = g;
  }

  drawOverlay() {
    if (this.overlay) this.overlay.clear();
    const { w, h } = this.tiles;
    const cellSize = Math.floor(Math.min(this.scale.width, this.scale.height) / Math.max(w, h));
    const g = this.add.graphics();
    g.lineStyle(1, 0x66ccff, 1);
    for (const idx of this.irrigate) {
      const x = (idx % w) * cellSize;
      const y = Math.floor(idx / w) * cellSize + 48;
      g.strokeRect(x, y, cellSize-1, cellSize-1);
    }
    this.overlay = g;
  }

  xyToCell(x, y) {
    const { w, h } = this.tiles; const top = 48;
    const cellSize = Math.floor(Math.min(this.scale.width, this.scale.height) / Math.max(w, h));
    if (y < top) return null;
    const cx = Math.floor(x / cellSize); const cy = Math.floor((y - top) / cellSize);
    if (cx < 0 || cy < 0 || cx >= w || cy >= h) return null;
    return cy * w + cx;
  }

  async nextTurn() {
    const year = this.years[this.yearIdx];
    const res = await simulateTurn(this.runId, this.region, year, {
      water: { irrigate_cells: Array.from(this.irrigate) },
      soil: { cover_crop: "no", fertilizer: "no" }
    });
    for (const c of res.deltas.cells) {
      if (this.tiles.ndvi[c.idx] !== undefined) this.tiles.ndvi[c.idx] += c.ndviΔ;
    }
    this.drawLayer(this.layerName);
    this.drawOverlay();

    if (this.yearIdx < this.years.length - 1) {
      this.yearIdx += 1; this.irrigate.clear(); await this.loadYear();
    } else {
      this.scene.start("ReportScene", { runId: this.runId });
    }
  }

  pickRandomIrrigation() {
    this.irrigate.clear();
    const n = 50; const { w, h } = this.tiles;
    while (this.irrigate.size < n) this.irrigate.add(Math.floor(Math.random() * w * h));
    this.drawOverlay();
  }
}
