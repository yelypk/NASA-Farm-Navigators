import { listRegions } from "../api/client.js";

export default class MenuScene extends Phaser.Scene {
  constructor() { super("MenuScene"); }
  async create() {
    const regions = await listRegions();
    const r = regions[0] || { id: "california", name: "California (Toy)", years: [2010,2011,2012] };
    this.add.text(40, 40, "Farm Navigators", { fontFamily: "monospace", fontSize: 28, color: "#cfe3ff"});
    this.add.text(40, 90, `Region: ${r.name || r.id}`, { fontFamily: "monospace", fontSize: 18 });
    this.add.text(40, 120, `Years: ${r.years[0]} ... ${r.years[r.years.length-1]}`, { fontFamily: "monospace", fontSize: 14, color:"#9ac"});
    const btn = this.add.text(40, 160, "Start ▶", { fontFamily: "monospace", fontSize: 24, backgroundColor: "#223", padding: 8 })
      .setInteractive({ useHandCursor: true })
      .on("pointerup", () => this.scene.start("GameScene", { region: r.id, years: r.years }));
  }
}
