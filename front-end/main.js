import Phaser from "phaser";
import BootScene from "./src/scenes/BootScene.js";
import MenuScene from "./src/scenes/MenuScene.js";
import GameScene from "./src/scenes/GameScene.js";
import UIScene from "./src/scenes/UIScene.js";
import ReportScene from "./src/scenes/ReportScene.js";

const config = {
  type: Phaser.AUTO,
  width: window.innerWidth,
  height: window.innerHeight,
  parent: "game",
  backgroundColor: "#0e1116",
  pixelArt: true,
  scene: [BootScene, MenuScene, GameScene, UIScene, ReportScene]
};

new Phaser.Game(config);
