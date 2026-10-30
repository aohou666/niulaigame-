import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const original=process.argv.includes('--original'),production=process.argv.includes('--production'),label=process.argv.find(x=>x.startsWith('--label='))?.slice(8)||(original?'original':production?'production':'candidate'),out='art-migration/versions/'+(process.argv.find(x=>x.startsWith('--version='))?.slice(10)||'0.89.0');
const effect=process.argv.find(x=>x.startsWith('--effect='))?.slice(9)||'effect_1';
const candidate=process.argv.find(x=>x.startsWith('--candidate='))?.slice(12)||'art-migration/generation/skin100201-effect1-native-packed-v1/candidate-containers.json';const entries=JSON.parse(await fs.readFile(candidate,'utf8'));await fs.mkdir(out,{recursive:true});
const b=await chromium.launch({channel:'chrome',headless:true});let report={pass:false,label,scope:'Native packed '+effect+': ten independently drawn texture regions on original19-frame30fps timeline, ordinary/EZ; not complete skin/body replacement.'};
try{
 const p=await b.newPage({viewport:{width:720,height:1280}}),errors=[],failures=[],requests=[];await p.addInitScript(e=>window.__packedEffect=e,effect);p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)failures.push(r.url());});p.on('request',r=>requests.push(r.url()));
 if(!production)await p.route('**/street-art-data.js*',async route=>{const text=await fs.readFile('local_game/street-art-data.js','utf8'),data=JSON.parse(text.slice(text.indexOf('=')+1).trim().replace(/;$/,''));data.containers=original?[]:entries;await route.fulfill({contentType:'text/javascript',body:'window.StreetArtData='+JSON.stringify(data)+';'});});
 await p.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await p.waitForFunction(()=>window.StreetArt?.audit.installed&&window.CharacterIdle?.snapshot().installed);
 report.requests=requests;report.artAudit=await p.evaluate(()=>StreetArt.audit);
 report.resourceDigests=await p.evaluate(async ({entries,original})=>{
  const rows=[];for(const entry of entries){const data=await RES.getResAsync(entry.originalKey),info=RES.getResourceInfo(original?entry.originalKey:entry.targetKey);if(!data)throw Error('Native bundle processor returned empty');if(!original&&data!==RES.getRes(entry.targetKey))throw Error('Original binary key did not resolve to replacement');const response=await fetch(new URL((info.root||'')+info.url,location.href));if(!response.ok)throw Error('Bundle fetch '+response.status);const bytes=await response.arrayBuffer(),digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(n=>n.toString(16).padStart(2,'0')).join('');rows.push({key:entry.originalKey,resolved:info.name,url:info.url,digest,bytes:bytes.byteLength,parsedType:data.constructor.name});}return rows;
 },{entries,original});
 for(let i=0;i<entries.length;i++)assert.equal(report.resourceDigests[i].digest,original?entries[i].originalSha256:entries[i].targetSha256);
 await p.evaluate(async()=>{
  const stage=egret.MainContext.instance.stage;for(let i=0;i<stage.numChildren;i++)stage.getChildAt(i).visible=false;const box=new egret.DisplayObjectContainer(),bg=new egret.Shape();bg.graphics.beginFill(0x52646a);bg.graphics.drawRect(0,0,720,1280);bg.graphics.endFill();box.addChild(bg);stage.addChild(box);
  const actors=['hero_skin_002_01','hero_skin_002_01_ez'].map((name,i)=>{const a=new DBPlayer();a.x=i?500:220;a.y=650;a.scaleX=a.scaleY=i?2:1;box.addChild(a);a.init(name,window.__packedEffect);return a;});window.__packedFX={box,actors};
  const start=Date.now();while(!actors.every(a=>a.isReady)&&Date.now()-start<15000)await new Promise(r=>setTimeout(r,10));if(!actors.every(a=>a.isReady))throw Error('Packed effect load timeout');
 });
 report.slotDebug=await p.evaluate(()=>__packedFX.actors[0]._armature.armature.getSlots().slice(0,2).map(s=>({name:s.name,displayIndex:s.displayIndex,privateIndex:s._displayIndex,hasDisplay:!!s.display,keys:Object.keys(s).filter(k=>/isplay|exture|visible/.test(k))})));
 const frames=[];report.frames=frames;
 for(let frame=0;frame<19;frame++){
  const data=await p.evaluate(frame=>{
   const rows=[];for(const a of __packedFX.actors){a._armature.animation.gotoAndPlayByFrame(window.__packedEffect,frame,1);a._armature.armature.advanceTime(1e-7);a._armature.animation.stop(window.__packedEffect);rows.push({model:a._dbName,currentTime:a._armature.animation.lastAnimationState.currentTime,duration:a._armature.animation.lastAnimationState.totalTime,active:a._armature.armature.getSlots().filter(s=>s.displayIndex>=0).map(s=>({slot:s.name,displayIndex:s.displayIndex,texture:s._textureData?.name})),body:!!a._streetBody,idle:!!a._characterIdleState,nativeVisible:a._armature.visible});}
   const t=new egret.RenderTexture();t.drawToTexture(__packedFX.box,new egret.Rectangle(80,390,560,330),2);const png=t.toDataURL('image/png').split(',')[1];t.dispose();return {rows,png};
  },frame);
  for(const row of data.rows){assert(Math.abs(row.duration-19/30)<1e-6);assert(Math.abs(row.currentTime-frame/30)<1e-6);assert(!row.body&&!row.idle&&row.nativeVisible);/* Preserve authored blank frames too; candidate must match original slot schedule. */}
  frames.push({frame,rows:data.rows});await fs.writeFile(out+`/packed-fx-${label}-${String(frame).padStart(2,'0')}.png`,Buffer.from(data.png,'base64'));
 }
 for(const model of ['hero_skin_002_01','hero_skin_002_01_ez'])assert.equal(new Set(frames.flatMap(f=>f.rows.filter(r=>r.model===model).flatMap(r=>r.active.map(s=>s.texture)))).size,10,'All ten texture regions must be visited');
 const live=await p.evaluate(async()=>{
  const rows=[];for(const a of __packedFX.actors){const samples=[],events=[];let callbacks=0,completes=0;const start=performance.now(),sample=()=>samples.push({time:performance.now()-start,frame:Math.floor(a._armature.animation.lastAnimationState.currentTime*30+.0001),active:a._armature.armature.getSlots().filter(s=>s.displayIndex>=0).map(s=>s._textureData?.name)}),event=e=>events.push(e.eventObject.name),complete=()=>completes++;
   a.addEventListener(egret.Event.ENTER_FRAME,sample,null);a._armature.addEventListener(dragonBones.EventObject.FRAME_EVENT,event,null);a._armature.addEventListener(dragonBones.EventObject.COMPLETE,complete,null);
   await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('FX live completion timeout')),4000);a.trigger(window.__packedEffect,()=>{callbacks++;clearTimeout(timeout);resolve();},2);});
   a.removeEventListener(egret.Event.ENTER_FRAME,sample,null);a._armature.removeEventListener(dragonBones.EventObject.FRAME_EVENT,event,null);a._armature.removeEventListener(dragonBones.EventObject.COMPLETE,complete,null);rows.push({model:a._dbName,elapsed:performance.now()-start,callbacks,completes,events,samples,distinctTextures:new Set(samples.flatMap(r=>r.active)).size});
  }return rows;
 });
 for(const row of live){assert.equal(row.callbacks,1);assert.equal(row.completes,1);assert.equal(row.events.length,0);assert.equal(row.distinctTextures,10);assert(Math.abs(row.elapsed-38/30*1000)<150);}
 const parentPlayback=await p.evaluate(async()=>{
  const rows=[];for(const a of __packedFX.actors){a.init(a._dbName,'hero_skin_002_01');const start=Date.now();while(!a.isReady&&Date.now()-start<10000)await new Promise(r=>setTimeout(r,10));if(!a.isReady)throw Error('Parent armature not ready');
   for(const action of ['gongji','jineng','paobu']){const samples=[],tick=()=>{for(const slot of a._armature.armature.getSlots()){const child=slot.childArmature;if(child?.armatureData.name===window.__packedEffect&&slot.displayIndex>=0&&slot.display?.visible&&slot.display.alpha>0&&(slot._colorTransform?.alphaMultiplier??1)>0&&a._armature.visible){const active=child.getSlots().filter(s=>s.displayIndex>=0).map(s=>s._textureData?.name);if(active.length)samples.push({time:performance.now(),parentAction:action,slot:slot.name,active});}}};a.addEventListener(egret.Event.ENTER_FRAME,tick,null);await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('Parent animation completion timeout')),4000);a.trigger(action,()=>{clearTimeout(timeout);resolve();},1);});a.removeEventListener(egret.Event.ENTER_FRAME,tick,null);rows.push({model:a._dbName,action,samples});}
  }return rows;
 });
 for(const model of ['hero_skin_002_01','hero_skin_002_01_ez'])assert(parentPlayback.some(r=>r.model===model&&r.samples.length>0),'Native main action must display child effect_1');
 report={...report,frames,live,parentPlayback,errors,failures,requests:requests.filter(r=>/hero_skin_002_01|native-fx/.test(r))};assert.equal(errors.length,0);assert.equal(failures.length,0);
 if(!original){const baseline=JSON.parse(await fs.readFile((process.argv.find(x=>x.startsWith('--baseline='))?.slice(11)||out+'/packed-fx-original.json'),'utf8'));assert.deepEqual(frames,baseline.frames,'Native frame/slot schedule must remain exact');}
 report.effect=effect;report.pass=true;report.manualReview='pending';
 await p.evaluate(()=>{for(const a of __packedFX.actors){a.destroy();if(a.parent)a.parent.removeChild(a);}if(__packedFX.box.parent)__packedFX.box.parent.removeChild(__packedFX.box);});
 console.log(JSON.stringify({pass:true,label,pausedFrames:frames.length,models:2,liveTextures:live.map(r=>r.distinctTextures)}));
}catch(e){report.error=e.stack;throw e;}finally{await b.close();await fs.writeFile(out+'/packed-fx-'+label+'.json',JSON.stringify(report,null,2));}
