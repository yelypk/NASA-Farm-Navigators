import Phaser from 'phaser'
import { GameState } from '../state'
import { ensureSave, regionPngUrl, tick } from '../api/client'

export default class RegionScene extends Phaser.Scene {
  constructor(){ super('RegionScene') }
  preload(){}
  async create(){
    await ensureSave()
    this.cameras.main.setBackgroundColor('#0b0d0f')
    const layerSel = document.getElementById('layerSelect')
    const seasonInput = document.getElementById('seasonInput')
    const btnLoad = document.getElementById('btnLoad')
    const btnTick = document.getElementById('btnTick')
    const btnFarm = document.getElementById('btnFarm')
    layerSel.value = GameState.layer
    seasonInput.value = GameState.season
    const loadLayerTex = async () => {
      const url = regionPngUrl(layerSel.value, parseInt(seasonInput.value,10))
      const key = `region_${layerSel.value}_${seasonInput.value}`
      const blob = await fetch(url).then(r=>r.blob())
      const bmp = await createImageBitmap(blob)
      if (this.textures.exists(key)) this.textures.remove(key)
      this.textures.addBitmap(key, bmp)
      if (this.mapSprite) this.mapSprite.destroy()
      this.mapSprite = this.add.image(256, 256, key).setOrigin(0.5).setScale(1).setInteractive()
      GameState.layer = layerSel.value
      GameState.season = parseInt(seasonInput.value,10)
    }
    btnLoad.onclick = loadLayerTex
    btnTick.onclick = async () => {
      const out = await tick()
      seasonInput.value = out.t_next
      await loadLayerTex()
    }
    btnFarm.onclick = () => this.scene.start('FarmScene')
    await loadLayerTex()
    this.input.keyboard.on('keydown-ONE', ()=>{ layerSel.value='ndvi'; btnLoad.click() })
    this.input.keyboard.on('keydown-TWO', ()=>{ layerSel.value='rain'; btnLoad.click() })
    this.input.keyboard.on('keydown-THREE', ()=>{ layerSel.value='soil'; btnLoad.click() })
    this.input.keyboard.on('keydown-FOUR', ()=>{ layerSel.value='temp'; btnLoad.click() })
    this.input.keyboard.on('keydown-FIVE', ()=>{ layerSel.value='landuse'; btnLoad.click() })
    this.input.keyboard.on('keydown-SPACE', ()=> btnTick.click())
    this.add.text(10, 522, '1:NDVI  2:RAIN  3:SOIL  4:TEMP  5:LANDUSE   SPACE: Tick   F: Farm', { fontSize:'14px', color:'#bfbfbf' })
    this.input.keyboard.on('keydown-F', ()=> btnFarm.click())
  }
}
