// frontend/src/scenes/RegionScene.js
import Phaser from "phaser";
import { fetchRegionPng } from "../api/layers";
import { applyLUTToImage } from "../lib/lut";

const REGION = "CA_SanJoaquin_West";
let season = 0;
let currentLayer = "ndvi"; // ndvi|rain|dry|temp

export default class RegionScene extends Phaser.Scene {
  constructor(){ super("RegionScene"); }

  preload() {
    // подложка-«спутник» (необязательно). Если файла нет — просто не рисуем.
    this.load.image("satellite-underlay", "assets/satellite/CA_SanJoaquin_West.png");
    this.load.on("loaderror", (_, file) => {
      if (file?.key === "satellite-underlay") {
        console.warn("No satellite underlay image found. Skipping.");
      }
    });
  }

  async create(){
    const w = this.scale.width, h = this.scale.height;

    // Спутниковая подложка (если загрузилась)
    if (this.textures.exists("satellite-underlay")) {
      this.add.image(0,0,"satellite-underlay").setOrigin(0,0).setAlpha(0.6);
    }

    // Контейнер для диагностик
    this.status = this.add.text(12, 12, "loading…", { fontFamily: "monospace", fontSize: 14, color: "#ccc" }).setDepth(1000);

    await this.loadAndShowLayer().catch(err => {
      console.error(err);
      this.status.setText("EO layer failed, showing placeholder (check backend/data/*)");
      this.drawPlaceholder(w, h);
    });

    // хоткеи
    this.input.keyboard.on("keydown-R", ()=> this.switchLayer("rain"));
    this.input.keyboard.on("keydown-N", ()=> this.switchLayer("ndvi"));
    this.input.keyboard.on("keydown-D", ()=> this.switchLayer("dry"));
    this.input.keyboard.on("keydown-T", ()=> this.switchLayer("temp"));
    this.input.keyboard.on("keydown-PLUS", ()=> this.changeSeason(+1));
    this.input.keyboard.on("keydown-MINUS", ()=> this.changeSeason(-1));
  }

  drawPlaceholder(w, h) {
    const g = this.add.graphics();
    for (let y=0; y<h; y+=32){
      for (let x=0; x<w; x+=32){
        const v = (x/w)*0.7 + (y/h)*0.3;
        const c = Phaser.Display.Color.Interpolate.ColorWithColor(
          new Phaser.Display.Color(30,60,30),
          new Phaser.Display.Color(0,180,0),
          100, Math.floor(v*100)
        );
        g.fillStyle(Phaser.Display.Color.GetColor(c.r,c.g,c.b), 1);
        g.fillRect(x,y,32,32);
      }
    }
  }

  async loadAndShowLayer(){
    this.status.setText(`loading ${currentLayer}@${season}…`);
    const img = await fetchRegionPng(REGION, currentLayer, season); // может кинуть, если 404 от бэка
    const canvas = applyLUTToImage(img, currentLayer);
    const texKey = `layer-${currentLayer}-${season}`;
    if (this.textures.exists(texKey)) this.textures.remove(texKey);
    this.textures.addImage(texKey, canvas);
    if (this.layerSprite) this.layerSprite.destroy();
    this.layerSprite = this.add.image(0,0, texKey).setOrigin(0,0);
    // растянем под вьюпорт
    this.layerSprite.setDisplaySize(this.scale.width, this.scale.height);
    this.status.setText(`${currentLayer}@${season}`);
  }

  async switchLayer(name){ currentLayer = name; await this.loadAndShowLayer().catch(()=>{}); }
  async changeSeason(d){ season = Math.max(0, season + d); await this.loadAndShowLayer().catch(()=>{}); }
}
