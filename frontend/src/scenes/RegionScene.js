import Phaser from "phaser";
import { fetchRegionPng } from "../api/layers";
import { applyLUTToImage } from "../lib/lut";

const REGION = "CA_SanJoaquin_West";
let season = 0;
let currentLayer = "ndvi"; // "ndvi" | "rain" | "dry" | "temp"

export default class RegionScene extends Phaser.Scene {
  constructor(){ super("RegionScene"); }

  async create(){
    // 1) optional: satellite underlay (static image aligned to 200x200 grid)
    // Сгенерируй/положи файл public/assets/satellite/CA_SanJoaquin_West.png (2000x2000, например).
    this.add.image(0,0,"satellite-underlay")
      .setOrigin(0,0).setScale(1.0).setAlpha(0.6); // tweak alpha

    // 2) first load
    await this.loadAndShowLayer();
    // 3) UI — быстрые клавиши
    this.input.keyboard.on("keydown-R", ()=> this.switchLayer("rain"));
    this.input.keyboard.on("keydown-N", ()=> this.switchLayer("ndvi"));
    this.input.keyboard.on("keydown-D", ()=> this.switchLayer("dry"));
    this.input.keyboard.on("keydown-T", ()=> this.switchLayer("temp"));
    this.input.keyboard.on("keydown-PLUS", ()=> this.changeSeason(+1));
    this.input.keyboard.on("keydown-MINUS", ()=> this.changeSeason(-1));
  }

  async loadAndShowLayer(){
    const img = await fetchRegionPng(REGION, currentLayer, season);
    const canvas = applyLUTToImage(img, currentLayer);
    const texKey = `layer-${currentLayer}-${season}`;
    this.textures.remove(texKey); // idempotent
    this.textures.addImage(texKey, canvas);
    if (this.layerSprite) this.layerSprite.destroy();
    this.layerSprite = this.add.image(0,0, texKey).setOrigin(0,0).setScrollFactor(1);
    // масштабируй к вашей карте, если нужно: this.layerSprite.setScale(...)
  }

  async switchLayer(name){ currentLayer = name; await this.loadAndShowLayer(); }
  async changeSeason(d){ season = Math.max(0, season + d); await this.loadAndShowLayer(); }
}
