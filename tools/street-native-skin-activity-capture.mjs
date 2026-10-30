import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const folder='art-migration/generation/skin100201-native-body107-packed-trial-v2';
const out='art-migration/generation/skin100201-native-activity-preview-v1';
await fs.mkdir(out+'/frames',{recursive:true});
const entries=JSON.parse(await fs.readFile(folder+'/candidate-containers.json','utf8'));
const browser=await chromium.launch({channel:'chrome',headless:true});
const report={pass:false,productionIntegrated:false,scope:'Staged native skill animation preview, not actual BattleAI footage. Original 19 exposures/38 frames at24fps protocol; full native motion validated separately.',frames:[]};
try{
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const name of ['street-body-data.js','character-idle-data.js','street-art-data.js'])await page.route('**/'+name+'*',async route=>{
  const text=await fs.readFile('local_game/'+name,'utf8'),prefix=text.slice(0,text.indexOf('=')+1),data=JSON.parse(text.slice(text.indexOf('=')+1).trim().replace(/;$/,''));
  if(name==='street-art-data.js')data.containers=[...data.containers.filter(e=>!entries.some(r=>r.originalKey===e.originalKey)),...entries];else data.skins={};
  await route.fulfill({contentType:'text/javascript',body:prefix+JSON.stringify(data)+';'});
 });
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');
 await page.waitForFunction(()=>window.DBPlayer&&StreetBody.snapshot().installed&&CharacterIdle.snapshot().installed);
 report.setup=await page.evaluate(async()=>{
  const box=new egret.DisplayObjectContainer();egret.MainContext.instance.stage.addChild(box);const a=new DBPlayer();box.addChild(a);a.init('hero_skin_002_01','hero_skin_002_01');const start=performance.now();while(!a.isReady&&performance.now()-start<15000)await new Promise(r=>setTimeout(r,10));
  if(!a.isReady||a._streetBody||a._characterIdleState)throw Error('Native-only preview failed');
  let left=Infinity,top=Infinity,right=-Infinity,bottom=-Infinity;
  for(let i=0;i<46;i++){a._armature.animation.reset();a._armature.animation.gotoAndPlayByFrame('jineng',i,1);a._armature.armature.advanceTime(1e-7);a._armature.animation.stop();const r=a.getBounds();left=Math.min(left,r.x);top=Math.min(top,r.y);right=Math.max(right,r.right);bottom=Math.max(bottom,r.bottom);}
  // Stable framing over the entire original skill, with room for child effects.
  const scale=Math.min(190/(right-left),224/(bottom-top));a.scaleX=a.scaleY=scale;a.x=103-(left+right)*scale/2;a.y=126-(top+bottom)*scale/2;
  a._armature.animation.reset();a._armature.animation.gotoAndPlayByFrame('jineng',0,1);a._armature.armature.advanceTime(1e-7);a._armature.animation.stop();window.__activityActor=a;window.__activityBox=box;
  return {model:a._dbName,action:'jineng',nativeFrames:46,nativeFPS:30,bounds:{left,top,right,bottom},scale};
 });
 for(let i=0;i<19;i++){
  const result=await page.evaluate(i=>{
   const a=__activityActor;const sourceFrame=Math.min(45,Math.floor(i*46/19));
   a._armature.animation.reset();a._armature.animation.gotoAndPlayByFrame('jineng',sourceFrame,1);a._armature.armature.advanceTime(1e-7);a._armature.animation.stop();
   const texture=new egret.RenderTexture();texture.drawToTexture(__activityBox,new egret.Rectangle(0,0,206,257),1);const png=texture.toDataURL('image/png').split(',')[1];texture.dispose();
   return {i,sourceFrame,png};
  },i);
  const bytes=Buffer.from(result.png,'base64');delete result.png;
  result.path=out+'/frames/'+String(i).padStart(2,'0')+'.png';result.sha256=crypto.createHash('sha256').update(bytes).digest('hex');await fs.writeFile(result.path,bytes);report.frames.push(result);
 }
 assert.equal(new Set(report.frames.map(r=>r.sha256)).size,19);assert.equal(errors.length,0);report.errors=errors;report.containerSources=entries.map(e=>({path:e.targetPath,sha256:e.targetSha256}));report.pass=true;
}finally{await browser.close();await fs.writeFile(out+'/capture.json',JSON.stringify(report,null,2));}
console.log(JSON.stringify({pass:report.pass,frames:report.frames.length,out}));
