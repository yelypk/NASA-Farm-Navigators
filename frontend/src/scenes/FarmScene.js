import Phaser from 'phaser'
import { ensureSave, farmPngUrl, setPlan, farmState, tick } from '../api/client'

export default class FarmScene extends Phaser.Scene {
  constructor(){ super('FarmScene') }
  preload(){}
  async create(){
    await ensureSave()
    this.cameras.main.setBackgroundColor('#0b0d0f')
    this.createOverlay()
    await this.loadLayer('soil')
    this.add.text(10, 522, 'Farm: [A/D] irrigation  [C] cover  [M] mulch  [R] run  [ESC] back', { fontSize:'14px', color:'#bfbfbf' })
    this.input.keyboard.on('keydown-ESC', ()=> this.scene.start('RegionScene'))
    this.input.keyboard.on('keydown-R', ()=> this.btnRun.click())
    this.input.keyboard.on('keydown-A', ()=> { this.irr.value = Math.max(0, parseFloat(this.irr.value)-0.1).toFixed(1) })
    this.input.keyboard.on('keydown-D', ()=> { this.irr.value = Math.min(1, parseFloat(this.irr.value)+0.1).toFixed(1) })
    this.input.keyboard.on('keydown-C', ()=> { this.cover.checked = !this.cover.checked })
    this.input.keyboard.on('keydown-M', ()=> { this.mulch.checked = !this.mulch.checked })
  }
  async loadLayer(layer){
    const url = farmPngUrl(layer)
    const key = `farm_${layer}_${Date.now()}`
    const blob = await fetch(url).then(r=>r.blob())
    const bmp = await createImageBitmap(blob)
    if (this.textures.exists(key)) this.textures.remove(key)
    this.textures.addBitmap(key, bmp)
    if (this.mapSprite) this.mapSprite.destroy()
    this.mapSprite = this.add.image(256, 256, key).setOrigin(0.5).setScale(1)
  }
  createOverlay(){
    const panel = document.createElement('div')
    panel.style.position='fixed'
    panel.style.top='58px'
    panel.style.right='10px'
    panel.style.background='#161a1d'
    panel.style.border='1px solid #2a2f34'
    panel.style.borderRadius='8px'
    panel.style.padding='10px'
    panel.style.color='#e6e6e6'
    panel.style.font='14px system-ui'
    panel.innerHTML = `
      <div style="margin-bottom:6px"><b>Farm Plan</b></div>
      <div style="margin-bottom:6px">Irrigation: <input id="irr" type="number" min="0" max="1" step="0.1" value="0.0" style="width:5rem"></div>
      <div style="margin-bottom:6px"><label><input id="cover" type="checkbox"> Cover crop</label></div>
      <div style="margin-bottom:6px"><label><input id="mulch" type="checkbox"> Mulch</label></div>
      <div style="display:flex; gap:8px">
        <button id="btnApply">Apply Plan</button>
        <button id="btnRun">Run Season</button>
        <button id="btnBack">Back</button>
      </div>
      <div id="stats" style="margin-top:8px; opacity:0.85"></div>
    `
    document.body.appendChild(panel)
    this.panel = panel
    this.irr = panel.querySelector('#irr')
    this.cover = panel.querySelector('#cover')
    this.mulch = panel.querySelector('#mulch')
    this.btnApply = panel.querySelector('#btnApply')
    this.btnRun = panel.querySelector('#btnRun')
    this.btnBack = panel.querySelector('#btnBack')
    this.stats = panel.querySelector('#stats')
    this.btnApply.onclick = async () => {
      await setPlan({ irrigation: parseFloat(this.irr.value), cover: this.cover.checked, mulch: this.mulch.checked })
      await this.loadLayer('ndvi_sim')
      const st = await farmState()
      this.stats.innerText = `Soil: ${st.soil_mean.toFixed(2)}  Aquifer: ${st.aquifer.toFixed(2)}  Cash: ${st.cash.toFixed(0)}  α=${st.alpha.toFixed(2)}`
    }
    this.btnRun.onclick = async () => {
      await this.btnApply.onclick()
      const out = await tick()
      await this.loadLayer('soil')
      this.stats.innerText += `\nTick → t=${out.t_next}, NDVI_sim=${out.ndvi_sim.toFixed(2)}`
    }
    this.btnBack.onclick = () => this.scene.start('RegionScene')
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => { panel.remove() })
  }
}
