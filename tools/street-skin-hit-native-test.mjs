import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(x=>x.startsWith('--version='))?.slice(10)||'0.88.0';
const out='art-migration/versions/'+version,source='art-migration/generation/skin100201-shouji-official21-v1/candidate.json';
const raw=await fs.readFile(source),cfg=JSON.parse(raw),candidateSha256=crypto.createHash('sha256').update(raw).digest('hex');
await fs.mkdir(out,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:720,height:1280}}),errors=[],failures=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failures.push(r.url());});page.on('requestfailed',r=>failures.push(r.url()));
 if(!process.argv.includes('--production'))await page.route('**/street-body-data.js*',async route=>{
  const text=await fs.readFile('local_game/street-body-data.js','utf8'),data=JSON.parse(text.slice(text.indexOf('=')+1).trim().replace(/;$/,''));
  data.skins={...data.skins,'100201':cfg};await route.fulfill({contentType:'text/javascript',body:'window.StreetBodyData='+JSON.stringify(data)+';'});
 });
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');
 await page.waitForFunction(()=>window.StreetBody?.snapshot().installed&&window.CharacterIdle?.snapshot().installed);
 const setup=await page.evaluate(async cfg=>{
  const stage=egret.MainContext.instance.stage;for(let i=0;i<stage.numChildren;i++)stage.getChildAt(i).visible=false;
  const container=new egret.DisplayObjectContainer(),bg=new egret.Shape();bg.graphics.beginFill(0x52646a);bg.graphics.drawRect(0,0,720,1280);bg.graphics.endFill();container.addChild(bg);stage.addChild(container);
  const players=cfg.models.map((model,i)=>{const p=new DBPlayer();p.x=i?520:220;p.y=700;container.addChild(p);p.init(model,cfg.armature);return p;});
  window.__skinHit={players,container};
  const start=Date.now();while(!players.every(p=>p.isReady&&p._streetBody?.cache.ready)&&Date.now()-start<20000)await new Promise(r=>setTimeout(r,20));
  if(!players.every(p=>p.isReady&&p._streetBody?.cache.ready))throw Error('Skin body not ready '+JSON.stringify(StreetBody.snapshot()));
  return players.map(p=>({model:p._dbName,id:p._streetBody.cfg.id,skinCode:p._streetBody.cfg.skinCode,armature:p._armature.armature.armatureData.name}));
 },cfg);
 for(const row of setup){assert.equal(row.id,100201);assert.equal(row.skinCode,100201);assert.equal(row.armature,cfg.armature);}
 const checks=[];
 for(let n=0;n<21;n++){
  const result=await page.evaluate(n=>{
   const {players,container}=__skinHit,rows=[];
   for(const p of players){p.gotoAndStopByFrame('shouji',n);p._armature.armature.advanceTime(0);StreetBody.render(p);const s=p._streetBody;rows.push({model:p._dbName,sourceFrame:s.frame,nativeFrame:s.nativeFrame,generated:s.bitmap.visible,native:p._armature.visible,duration:p._armature.animation.lastAnimationState.totalTime,bodyBounds:s.bitmap.getTransformedBounds(egret.MainContext.instance.stage)});}
   const texture=new egret.RenderTexture();texture.drawToTexture(container,new egret.Rectangle(130,540,480,190),2);const png=texture.toDataURL('image/png').split(',')[1];texture.dispose();return {rows,png};
  },n);
  for(const row of result.rows){assert.equal(row.sourceFrame,n);assert.equal(row.nativeFrame,n);assert(row.generated&&!row.native);assert(Math.abs(row.duration-.7)<1e-6);}
  checks.push(...result.rows);await fs.writeFile(out+`/skin-hit-frame-${String(n).padStart(2,'0')}.png`,Buffer.from(result.png,'base64'));
 }
 const live=await page.evaluate(async()=>{
  const rows=[];
  for(const p of __skinHit.players){
   const events=[],observed=[],start=performance.now();let complete=0,calls=0;
   const event=e=>events.push(e.eventObject.name),done=()=>complete++,tick=()=>{const s=p._streetBody;if(s&&s.bitmap.visible)observed.push({time:performance.now()-start,nativeFrame:s.nativeFrame,sourceFrame:s.frame});};
   p._armature.addEventListener(dragonBones.EventObject.FRAME_EVENT,event,null);p._armature.addEventListener(dragonBones.EventObject.COMPLETE,done,null);p.addEventListener(egret.Event.ENTER_FRAME,tick,null);
   await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('hit completion timeout')),3000);p.trigger('shouji',()=>{calls++;StreetBody.render(p);clearTimeout(timeout);resolve();},1);});
   p._armature.removeEventListener(dragonBones.EventObject.FRAME_EVENT,event,null);p._armature.removeEventListener(dragonBones.EventObject.COMPLETE,done,null);p.removeEventListener(egret.Event.ENTER_FRAME,tick,null);
   rows.push({model:p._dbName,elapsed:performance.now()-start,complete,calls,events,observed,distinctSourceFrames:new Set(observed.map(x=>x.sourceFrame)).size});
  }
  for(const p of __skinHit.players)p.trigger('daiji',null,0);await new Promise(r=>setTimeout(r,300));
  return {rows,idle:__skinHit.players.map(p=>({model:p._dbName,body:p._streetBody.bitmap.visible,idleId:p._characterIdleState?.cfg.id,idleVisible:!!p._characterIdleState?.bitmap.visible,nativeVisible:p._armature.visible}))};
 });
 for(const r of live.rows){assert.equal(r.complete,1);assert.equal(r.calls,1);assert.deepEqual(r.events,[]);assert(Math.abs(r.elapsed-700)<130,JSON.stringify(r));assert(r.distinctSourceFrames>=10);}
 for(const r of live.idle){assert(!r.body);assert.equal(r.idleId,100201);assert(r.idleVisible&&!r.nativeVisible);}
 const fallbacks=await page.evaluate(()=>{
  const rows=[];for(const p of __skinHit.players)for(const action of ['gongji','jineng','paobu']){p.gotoAndStopByFrame(action,0);p._armature.armature.advanceTime(0);StreetBody.render(p);rows.push({model:p._dbName,action,body:p._streetBody.bitmap.visible,native:p._armature.visible});}return rows;
 });
 for(const r of fallbacks)assert(!r.body&&r.native,'Unsupported body state must preserve original native: '+JSON.stringify(r));
 const effects=await page.evaluate(async()=>{
  const p=__skinHit.players[0],rows=[];
  for(const model of ['hero_skin_002_01','hero_skin_002_01_ez'])for(const action of ['effect_1','effect_2','effect_3']){
   p.init(model,action);const start=Date.now();while(!p.isReady&&Date.now()-start<10000)await new Promise(r=>setTimeout(r,10));
   if(!p.isReady)throw Error('Effect not ready');rows.push({model,action,body:!!p._streetBody,idle:!!p._characterIdleState,native:p._armature.visible});
  }
  p.init('hero_skin_002_01','hero_skin_002_01');const start=Date.now();while(!p._streetBody?.cache.ready&&Date.now()-start<10000)await new Promise(r=>setTimeout(r,10));
  const restored=p._streetBody?.cfg.skinCode;
  for(const actor of __skinHit.players){actor.destroy();if(actor.parent)actor.parent.removeChild(actor);}
  __skinHit.container.parent.removeChild(__skinHit.container);return {rows,restored,after:StreetBody.snapshot()};
 });
 for(const r of effects.rows)assert(!r.body&&!r.idle&&r.native);assert.equal(effects.restored,100201);assert.equal(effects.after.caches.length,0);assert.equal(effects.after.active.length,0);assert.equal(effects.after.errors.length,0);
 assert.equal(errors.length,0);assert.equal(failures.length,0);
 const report={pass:true,candidateSha256,mode:process.argv.includes('--production')?'production':'candidate-data-route',scope:'Genuine new21-frame skin100201 hit atlas in native ordinary/EZ DBPlayer; all42 paused mappings, live0.7s completion/no authored frame events, idle fallback, other native actions, six effect armatures and cache reuse/destroy. Not actual battle hit trigger or complete skin.',manualVideoReview:'pending',setup,checks,live,fallbacks,effects,errors,failures};
 await fs.writeFile(out+'/skin-hit-native-runtime'+(process.argv.includes('--production')?'-production':'')+'.json',JSON.stringify(report,null,2));
 console.log(JSON.stringify({pass:true,mappings:checks.length,live:live.rows.map(r=>({model:r.model,elapsed:r.elapsed,distinct:r.distinctSourceFrames})),effects:effects.rows.length}));
}finally{await browser.close();}
