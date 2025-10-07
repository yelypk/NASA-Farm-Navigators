// frontend/src/main.js
import Phaser from "phaser";
import RegionScene from "./scenes/RegionScene";

function boot() {
  const parent = document.getElementById("app") || document.body;
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    width: window.innerWidth,
    height: window.innerHeight,
    parent,
    backgroundColor: "#0b0d10",
    scene: [RegionScene],
  });
  window.addEventListener("resize", () =>
    game.scale.resize(window.innerWidth, window.innerHeight)
  );
}

// простая подсветка ошибок прямо на странице
window.addEventListener("error", (e) => {
  const box = document.createElement("pre");
  box.style.cssText = "position:fixed;left:8px;bottom:8px;max-width:60vw;max-height:40vh;overflow:auto;background:#200;color:#faa;padding:8px;border:1px solid #a66;z-index:99999;font-size:12px";
  box.textContent = `JS error: ${e.message}\n${e.filename}:${e.lineno}`;
  document.body.appendChild(box);
});

boot();

