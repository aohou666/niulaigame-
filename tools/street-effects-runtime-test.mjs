import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out=path.resolve('outputs/street-reskin/effect-preview');await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:480,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.StreetEffects&&StreetEffects.snapshot().installed,null,{timeout:90000});
 await page.evaluate(async()=>{
  const container=new egret.DisplayObjectContainer(),bg=new egret.Shape();bg.graphics.beginFill(0);bg.graphics.drawRect(0,0,512,512);bg.graphics.endFill();container.addChild(bg);
  const player=new DBPlayer();player.x=256;player.y=330;container.addChild(player);egret.MainContext.instance.stage.addChild(container);player.init('common_skill_caocao_02_1');window.__effectTest={container,player};
  await new Promise((resolve,reject)=>{const began=Date.now(),timer=setInterval(()=>{if(player.isReady&&player._streetEffect&&player._streetEffect.cache.ready){clearInterval(timer);resolve();}else if(Date.now()-began>20000){clearInterval(timer);reject(Error('replacement effect did not become ready'));}},25);});
 });
 for(const frame of [0,5,10,20,35,52]){
  const result=await page.evaluate(frame=>{
   const {container,player}=window.__effectTest;player.gotoAndStopByFrame('common_skill_caocao_02_1',frame);player._armature.armature.advanceTime(0);StreetEffects.render(player);
   const texture=new egret.RenderTexture();texture.drawToTexture(container,new egret.Rectangle(0,0,512,512));const data=texture.toDataURL('image/png').split(',')[1];texture.dispose();
   return {data,nativeVisible:player._armature.visible,frame:player._streetEffect.frame,expected:frame};
  },frame);
  assert.equal(result.nativeVisible,false);assert.equal(result.frame,frame);
  await fs.writeFile(path.join(out,`replacement-${frame}.png`),Buffer.from(result.data,'base64'));
 }
 const timing=await page.evaluate(async()=>{
  const player=window.__effectTest.player,events=[];
  for(let trial=0;trial<2;trial++){
   const start=performance.now();let calls=0;
   await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('native completion did not fire')),6000);player.trigger('common_skill_caocao_02_1',()=>{calls++;clearTimeout(timeout);resolve();},1);});
   await new Promise(r=>setTimeout(r,50));events.push({trial,completionCallbacks:calls,elapsedMs:performance.now()-start});
  }
  const before=StreetEffects.snapshot();player.destroy();window.__effectTest.container.parent.removeChild(window.__effectTest.container);
  return {events,before,after:StreetEffects.snapshot()};
 });
 for(const r of timing.events){assert.equal(r.completionCallbacks,1);assert(r.elapsedMs>1800&&r.elapsedMs<4000);}
 assert.equal(timing.after.active.length,0);assert.equal(timing.after.caches.length,0);assert.equal(errors.length,0);
 const report={pass:true,errors,timing,sourceFrames:53,sourceFps:24,sourceTimelineChanged:false};
 const version=path.resolve('art-migration/versions/0.24.0');await fs.mkdir(version,{recursive:true});await fs.writeFile(path.join(version,'effect-runtime.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({pass:true,events:timing.events,framesPresented:timing.before.framesPresented,cachesAfterDestroy:timing.after.caches.length}));
}finally{await browser.close();}
