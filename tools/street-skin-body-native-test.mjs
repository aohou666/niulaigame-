import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(x=>x.startsWith('--version='))?.slice(10)||'0.94.0';
const out='art-migration/versions/'+version,source=process.argv.find(x=>x.startsWith('--candidate='))?.slice(12)||'art-migration/generation/skin100201-gongji-official45-v1/candidate.json';
const raw=await fs.readFile(source),cfg=JSON.parse(raw),candidateSha256=crypto.createHash('sha256').update(raw).digest('hex');
const action=process.argv.find(x=>x.startsWith('--action='))?.slice(9)||'gongji',seq=cfg.actions[action],count=seq.frameMap.length,duration=count/seq.fps;
await fs.mkdir(out,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:720,height:1280}}),errors=[],failures=[];
 await page.addInitScript(action=>window.__bodyTestAction=action,action);
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
 const atlasProof=await page.evaluate(async()=>{const cfg=StreetBodyData.skins['100201'],r=await fetch(cfg.atlas),raw=await r.arrayBuffer();return {path:cfg.atlas,sha256:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw))).map(n=>n.toString(16).padStart(2,'0')).join('')};});assert.equal(atlasProof.sha256,cfg.atlasSha256);
 const checks=[];
 for(let n=0;n<count;n++){
  const result=await page.evaluate(n=>{
   const {players,container}=__skinHit,rows=[];
   for(const p of players){p.gotoAndStopByFrame(window.__bodyTestAction,n);p._armature.armature.advanceTime(0);StreetBody.render(p);const s=p._streetBody;rows.push({model:p._dbName,sourceFrame:s.frame,nativeFrame:s.nativeFrame,generated:s.bitmap.visible,native:p._armature.visible,nativeFXOnly:!!p._streetNativeFX&&p._armature.armature.getSlots().filter(slot=>slot.visible).length>0&&p._armature.armature.getSlots().filter(slot=>slot.visible).every(slot=>slot.childArmature&&p._streetNativeFX.names.includes(slot.childArmature.armatureData.name)),duration:p._armature.animation.lastAnimationState.totalTime,bodyBounds:s.bitmap.getTransformedBounds(egret.MainContext.instance.stage)});}
   const texture=new egret.RenderTexture();texture.drawToTexture(container,new egret.Rectangle(130,540,480,190),2);const png=texture.toDataURL('image/png').split(',')[1];texture.dispose();return {rows,png};
  },n);
  for(const row of result.rows){assert.equal(row.sourceFrame,seq.frameMap[n]);assert.equal(row.nativeFrame,n);assert(row.generated&&(!row.native||row.nativeFXOnly));assert(Math.abs(row.duration-duration)<1e-6);}
  checks.push(...result.rows);await fs.writeFile(out+`/skin-${action}-frame-${String(n).padStart(2,'0')}.png`,Buffer.from(result.png,'base64'));
 }
 const live=await page.evaluate(async()=>{
  const rows=[];
  for(const p of __skinHit.players){
   const events=[],observed=[],start=performance.now();let complete=0,calls=0;
   const event=e=>events.push({name:e.eventObject.name,frame:Math.floor(p._armature.animation.lastAnimationState.currentTime*30+.0001)}),done=()=>complete++,tick=()=>{const s=p._streetBody;if(s&&s.bitmap.visible)observed.push({time:performance.now()-start,nativeFrame:s.nativeFrame,sourceFrame:s.frame});};
   p._armature.addEventListener(dragonBones.EventObject.FRAME_EVENT,event,null);p._armature.addEventListener(dragonBones.EventObject.COMPLETE,done,null);p.addEventListener(egret.Event.ENTER_FRAME,tick,null);
   await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('hit completion timeout')),3000);p.trigger(window.__bodyTestAction,()=>{calls++;StreetBody.render(p);clearTimeout(timeout);resolve();},1);});
   p._armature.removeEventListener(dragonBones.EventObject.FRAME_EVENT,event,null);p._armature.removeEventListener(dragonBones.EventObject.COMPLETE,done,null);p.removeEventListener(egret.Event.ENTER_FRAME,tick,null);
   rows.push({model:p._dbName,elapsed:performance.now()-start,complete,calls,events,observed,distinctSourceFrames:new Set(observed.map(x=>x.sourceFrame)).size});
  }
  for(const p of __skinHit.players)p.trigger('daiji',null,0);await new Promise(r=>setTimeout(r,300));
  return {rows,idle:__skinHit.players.map(p=>({model:p._dbName,body:p._streetBody.bitmap.visible,idleId:p._characterIdleState?.cfg.id,idleVisible:!!p._characterIdleState?.bitmap.visible,nativeVisible:p._armature.visible,nativeFXOnly:!!p._streetNativeFX&&p._armature.armature.getSlots().filter(slot=>slot.visible).length>0&&p._armature.armature.getSlots().filter(slot=>slot.visible).every(slot=>slot.childArmature&&p._streetNativeFX.names.includes(slot.childArmature.armatureData.name))}))};
 });
 for(const r of live.rows){assert.equal(r.complete,1);assert.equal(r.calls,1);assert.deepEqual(r.events.map(e=>e.name),seq.nativeEvents.map(e=>e.name));for(let i=0;i<r.events.length;i++)assert(Math.abs(r.events[i].frame-seq.nativeEvents[i].frame0)<=1,'Native authored event moved');assert(Math.abs(r.elapsed-duration*1000)<130,JSON.stringify(r));assert(r.distinctSourceFrames===count,'Live playback skipped source frames: '+r.distinctSourceFrames+'/'+count);}
 for(const r of live.idle){assert(!r.body);assert.equal(r.idleId,100201);assert(r.idleVisible&&(!r.nativeVisible||r.nativeFXOnly));}
 const fallbacks=await page.evaluate(()=>{
  const rows=[];for(const p of __skinHit.players)for(const action of ['gongji','jineng','paobu'].filter(action=>!StreetBodyData.skins['100201'].actions[action])){p.gotoAndStopByFrame(action,0);p._armature.armature.advanceTime(0);StreetBody.render(p);rows.push({model:p._dbName,action,body:p._streetBody.bitmap.visible,native:p._armature.visible,fxOwner:!!p._streetNativeFX,bodySlotsVisible:p._armature.armature.getSlots().some(slot=>slot.visible&&!slot.childArmature)});}return rows;
 });
 for(const r of fallbacks)assert(!r.body&&r.native&&!r.fxOwner&&r.bodySlotsVisible,'Unsupported body state must preserve original native: '+JSON.stringify(r));
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
 const report={pass:true,action,atlasSha256:atlasProof.sha256,atlasProof,candidateSha256,mode:process.argv.includes('--production')?'production':'candidate-data-route',scope:'Native ordinary/EZ independent skin100201 '+action+'; all mapped frames, original authored timing/events, idle, unmapped native fallbacks, six FX armatures, reuse/destroy. Actual battle is separate; incomplete skin.',manualVideoReview:'pending',setup,checks,live,fallbacks,effects,errors,failures};
 await fs.writeFile(out+'/skin-'+action+'-native-runtime'+(process.argv.includes('--production')?'-production':'')+'.json',JSON.stringify(report,null,2));
 console.log(JSON.stringify({pass:true,action,mappings:checks.length,live:live.rows.map(r=>({model:r.model,elapsed:r.elapsed,distinct:r.distinctSourceFrames})),effects:effects.rows.length}));
}finally{await browser.close();}
