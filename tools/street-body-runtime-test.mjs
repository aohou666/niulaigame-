import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
await fs.mkdir('outputs/street-reskin/body-preview',{recursive:true});await fs.mkdir('art-migration/versions/0.25.0',{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:480,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.StreetBody&&StreetBody.snapshot().installed,null,{timeout:90000});
 await page.evaluate(async()=>{
  var container=new egret.DisplayObjectContainer(),bg=new egret.Shape();bg.graphics.beginFill(0x52646a);bg.graphics.drawRect(0,0,512,512);bg.graphics.endFill();container.addChild(bg);
  var player=new DBPlayer();player.x=256;player.y=330;container.addChild(player);egret.MainContext.instance.stage.addChild(container);player.init('hero_001_01');window.__bodyTest={container,player};
  await new Promise((resolve,reject)=>{var start=Date.now(),timer=setInterval(()=>{if(player.isReady&&player._streetBody?.cache.ready){clearInterval(timer);resolve();}else if(Date.now()-start>20000){clearInterval(timer);reject(Error('body did not become ready '+JSON.stringify(StreetBody.snapshot())));}},30);});
 });
 for(const action of ['gongji','jineng'])for(const frame of [0,6,12,20,30,40]){
  const r=await page.evaluate(({action,frame})=>{
   const {container,player}=window.__bodyTest;player.gotoAndStopByFrame(action,frame);player._armature.armature.advanceTime(0);StreetBody.render(player);
   const t=new egret.RenderTexture();t.drawToTexture(container,new egret.Rectangle(0,0,512,512));const data=t.toDataURL('image/png').split(',')[1];t.dispose();return {data,state:StreetBody.snapshot().active.find(p=>p.model==='hero_001_01')};
  },{action,frame});
  assert.equal(r.state.visible,true,JSON.stringify(r.state));assert.equal(r.state.nativeVisible,false);
  await fs.writeFile(`outputs/street-reskin/body-preview/${action}-${frame}.png`,Buffer.from(r.data,'base64'));
 }
 const timing=await page.evaluate(async()=>{
  const player=window.__bodyTest.player,events=[];
  for(const action of ['gongji','jineng','gongji']){
   var calls=0,pia=[];const listener=e=>{if(e.eventObject.name==='pia')pia.push({elapsedMs:performance.now()-start,sourceFrame:player._streetBody.frame});};
   player._armature.addEventListener(dragonBones.EventObject.FRAME_EVENT,listener,null);const start=performance.now();
   await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('native completion timeout '+action)),5000);player.trigger(action,()=>{calls++;clearTimeout(timeout);resolve();},1);});
   player._armature.removeEventListener(dragonBones.EventObject.FRAME_EVENT,listener,null);events.push({action,calls,pia,elapsedMs:performance.now()-start});
  }
  player.trigger('daiji',null,0);await new Promise(r=>setTimeout(r,100));const idle={bodyVisible:player._streetBody.bitmap.visible,nativeVisible:player._armature.visible,idleVisible:player._characterIdleState.bitmap.visible};
  const before=StreetBody.snapshot();player.destroy();window.__bodyTest.container.parent.removeChild(window.__bodyTest.container);return {events,idle,before,after:StreetBody.snapshot()};
 });
 for(const e of timing.events){assert.equal(e.calls,1);assert(e.elapsedMs>1100&&e.elapsedMs<2200);if(e.action==='gongji'){assert.equal(e.pia.length,1);assert(e.pia[0].elapsedMs>300&&e.pia[0].elapsedMs<550);}}
 assert.equal(timing.idle.bodyVisible,false);assert.equal(timing.idle.nativeVisible,false);assert.equal(timing.idle.idleVisible,true);assert.equal(timing.after.active.length,0);assert.equal(timing.after.caches.length,0);assert.equal(errors.length,0);
 await fs.writeFile('art-migration/versions/0.25.0/body-runtime.json',JSON.stringify({pass:true,errors,timing},null,2));console.log(JSON.stringify({pass:true,events:timing.events,idle:timing.idle}));
}finally{await browser.close();}
