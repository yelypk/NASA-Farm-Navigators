import Phaser from 'phaser'
import { newGame, getState, postPlan, tick, rasterUrl } from './api.js'

let GAME_ID = null
let GAME_META = { year: 2014, season: 'spring' }

class FarmScene extends Phaser.Scene{
  constructor(){ super('farm') }
  preload(){}
  async create(){
    this.size = 32
    this.cellPix = 16
    this.origin = {x: 16, y: 16}
    this.graphics = this.add.graphics()
    this.plan = {} // cellIdx -> {crop, irrigation, drainage}
    this.cropCycle = ['fallow','wheat','maize','cotton','alfalfa','millet']
    this.input.on('pointerdown', (p)=>this.handleClick(p))
    await this.refresh()
  }
  async refresh(){
    const img = this.add.image(0,0, 'ndvi'); if(img) img.destroy()
    const tx = await this.texturize(rasterUrl(GAME_ID,'ndvi'))
    const spr = this.add.image(this.origin.x, this.origin.y, tx).setOrigin(0,0).setScale(1)
    this.drawGrid()
    await this.updateInfo()
  }
  async updateInfo(){
    const st = await getState(GAME_ID)
    GAME_META = st
    document.getElementById('info').textContent = `Y ${st.year} · ${st.season} · NDVI ${st.kpis.avg_ndvi.toFixed(2)} · $ ${st.finance.cash.toFixed(0)}`
  }
  drawGrid(){
    const n=this.size, s=this.cellPix
    this.graphics.clear()
    this.graphics.lineStyle(1, 0xDDDDDD, 1.0)
    for(let i=0;i<=n;i++){
      this.graphics.lineBetween(this.origin.x, this.origin.y+i*s, this.origin.x+n*s, this.origin.y+i*s)
      this.graphics.lineBetween(this.origin.x+i*s, this.origin.y, this.origin.x+i*s, this.origin.y+n*s)
    }
  }
  async texturize(url){
    const key = 'ndvi-'+Math.random()
    const img = await new Promise((resolve)=>{
      const im = new Image(); im.crossOrigin = "anonymous"
      im.onload = ()=> resolve(im)
      im.src = url
    })
    const tx = this.textures.createCanvas(key, img.width, img.height)
    const ctx = tx.getContext('2d')
    ctx.drawImage(img,0,0)
    tx.refresh()
    return key
  }
  idxFromPointer(p){
    const s = this.cellPix, n=this.size
    const x = Math.floor((p.x - this.origin.x)/s)
    const y = Math.floor((p.y - this.origin.y)/s)
    if(x<0||y<0||x>=n||y>=n) return -1
    return y*n + x
  }
  async handleClick(p){
    const idx = this.idxFromPointer(p); if(idx<0) return
    const e = this.input.activePointer
    const key = String(idx)
    if(!this.plan[key]) this.plan[key] = {crop: 'fallow', irrigation:false, drainage:false}
    if(e.leftButtonDown()){
      // cycle crop
      const cur = this.plan[key].crop
      const i = this.cropCycle.indexOf(cur)
      this.plan[key].crop = this.cropCycle[(i+1)%this.cropCycle.length]
    }else if(e.rightButtonDown() && e.shiftKey){
      this.plan[key].drainage = !this.plan[key].drainage
    }else if(e.rightButtonDown()){
      this.plan[key].irrigation = !this.plan[key].irrigation
    }
    await postPlan(GAME_ID, {[key]: this.plan[key]})
    await this.refresh()
  }
}

async function boot(){
  document.getElementById('new').onclick = async ()=>{
    const region = document.getElementById('region').value
    const st = await newGame(region)
    GAME_ID = st.id
    await game.scene.keys['farm'].refresh()
  }
  document.getElementById('tick').onclick = async ()=>{
    await tick(GAME_ID)
    await game.scene.keys['farm'].refresh()
  }

  const config = {
    type: Phaser.AUTO,
    parent: 'app',
    width: 640,
    height: 640,
    backgroundColor: '#ffffff',
    scene: [FarmScene],
  }
  window.game = new Phaser.Game(config)
}
boot()
