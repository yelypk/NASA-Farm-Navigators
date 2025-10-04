import { fetchSummary } from "../api/client.js";

export default class ReportScene extends Phaser.Scene {
  constructor() { super("ReportScene"); }
  async init(data) { this.runId = data.runId; }
  async create() {
    const s = await fetchSummary(this.runId);
    this.add.text(60, 60, "Run Summary", { fontFamily: "monospace", fontSize: 28, color: "#f7f7f7"});
    this.add.text(60, 110, `Eco total: ${s.score.eco.toFixed(2)}`, { fontFamily: "monospace", fontSize: 18 });
    this.add.text(60, 140, s.analysis_text, { fontFamily: "monospace", fontSize: 16, wordWrap: { width: 600 }});
    this.add.text(60, 200, "⟲ Back to Menu", { fontFamily: "monospace", fontSize: 18, backgroundColor: "#223", padding: 8 })
      .setInteractive({ useHandCursor: true })
      .on("pointerup", () => this.scene.start("MenuScene"));
  }
}
