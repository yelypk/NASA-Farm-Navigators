import Phaser from 'phaser'
import { GameState } from './state'
import RegionScene from './scenes/RegionScene'
import FarmScene from './scenes/FarmScene'

const apiInput = document.getElementById('apiBase')
if (apiInput) apiInput.addEventListener('change', ()=> { GameState.apiBase = apiInput.value.trim() })

const config = {
  type: Phaser.AUTO,
  parent: 'app',
  width: 512,
  height: 544,
  backgroundColor: '#0b0d0f',
  pixelArt: true,
  scene: [RegionScene, FarmScene]
}
new Phaser.Game(config)
