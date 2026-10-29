import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const effect=process.argv[2]||'common_skill_caocao_02_1',frames=Number(process.argv[3]||53);
const out=path.resolve('outputs/street-reskin/effect-reference',effect);await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:512,height:768}});
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.CharacterIdle&&CharacterIdle.snapshot().installed,null,{timeout:90000});
 await page.evaluate(async name=>{
  const stage=egret.MainContext.instance.stage,container=new egret.DisplayObjectContainer();
  const bg=new egret.Shape();bg.graphics.beginFill(0);bg.graphics.drawRect(0,0,512,512);bg.graphics.endFill();container.addChild(bg);
  const player=new DBPlayer();player.x=256;player.y=330;container.addChild(player);stage.addChild(container);
  player.init(name);await new Promise((resolve,reject)=>{const t=Date.now(),poll=setInterval(()=>{if(player.isReady){clearInterval(poll);resolve();}else if(Date.now()-t>20000){clearInterval(poll);reject(Error('effect did not load'));}},50);});
  window.__streetExport={container,player};
 },effect);
 for(let i=0;i<frames;i++){
  const data=await page.evaluate(({effect,i})=>{
   const {container,player}=window.__streetExport;player.gotoAndStopByFrame(effect,i);
   player._armature.armature.advanceTime(0);
   const t=new egret.RenderTexture();t.drawToTexture(container,new egret.Rectangle(0,0,512,512));
   const data=t.toDataURL('image/png');t.dispose();return data.split(',')[1];
  },{effect,i});
  await fs.writeFile(path.join(out,`frame_${String(i).padStart(4,'0')}.png`),Buffer.from(data,'base64'));
 }
 console.log(JSON.stringify({effect,frames,out}));
}finally{await browser.close();}
