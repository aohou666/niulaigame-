import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(v=>v.startsWith('--version='))?.slice(10)||'0.28.0',ids=process.argv.filter(v=>/^\d+$/.test(v)).map(Number);await fs.mkdir('art-migration/versions/'+version,{recursive:true});await fs.mkdir('outputs/street-reskin/body-roster',{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:480,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await page.waitForFunction(()=>window.StreetBody?.snapshot().installed);
 const configs=await page.evaluate(ids=>StreetBodyData.characters.filter(c=>!ids.length||ids.includes(c.id)),ids),reports=[];
 for(const cfg of configs){
  await page.evaluate(async cfg=>{
   const container=new egret.DisplayObjectContainer(),bg=new egret.Shape();bg.graphics.beginFill(0x52646a);bg.graphics.drawRect(0,0,512,512);bg.graphics.endFill();container.addChild(bg);egret.MainContext.instance.stage.addChild(container);
   const players=cfg.models.map((name,i)=>{const p=new DBPlayer();p.x=i?350:160;p.y=330;container.addChild(p);p.init(name,name.replace(/_ez$/,''));return p;});window.__bodyRoster={container,players};
   await new Promise((resolve,reject)=>{const start=Date.now(),timer=setInterval(()=>{if(players.every(p=>p.isReady&&p._streetBody?.cache.ready)){clearInterval(timer);resolve();}else if(Date.now()-start>25000){clearInterval(timer);reject(Error('body not ready '+cfg.id+' '+JSON.stringify({players:players.map(p=>({name:p._dbName,ready:p.isReady})),body:StreetBody.snapshot()})));}},25);});
  },cfg);
  const frames=await page.evaluate(cfg=>{
   const {container,players}=window.__bodyRoster,checks=[],clocks=[];
   for(const action of Object.keys(cfg.actions))for(let n=0;n<cfg.actions[action].frameMap.length;n++)for(const p of players){p.gotoAndStopByFrame(action,n);p._armature.armature.advanceTime(0);StreetBody.render(p);const s=p._streetBody;checks.push({action,n,model:p._dbName,visible:s.bitmap.visible,native:p._armature.visible,frame:s.frame,expected:cfg.actions[action].frameMap[n],size:[s.bitmap.width,s.bitmap.height]});}
   for(const p of players)for(const action of Object.keys(cfg.actions)){p.gotoAndStopByFrame(action,0);p._armature.armature.advanceTime(0);clocks.push({model:p._dbName,action,totalTime:p._armature.animation.lastAnimationState.totalTime,expected:cfg.actions[action].frameMap.length/cfg.actions[action].fps});}
   for(const p of players){const seq=cfg.actions.gongji;p.gotoAndStopByFrame('gongji',seq.nativeImpactFrame??Math.floor(seq.frameMap.length/2));p._armature.armature.advanceTime(0);StreetBody.render(p);}
   const t=new egret.RenderTexture();t.drawToTexture(container,new egret.Rectangle(0,0,512,512));const screenshot=t.toDataURL('image/png').split(',')[1];t.dispose();return {checks,clocks,screenshot};
  },cfg);
  for(const r of frames.checks){assert(r.visible&&!r.native,JSON.stringify(r));assert.equal(r.frame,r.expected,JSON.stringify(r));assert(r.size.every(v=>v>0&&v<300));}
  for(const c of frames.clocks)assert(Math.abs(c.totalTime-c.expected)<.0001,JSON.stringify(c));
  await fs.writeFile(`outputs/street-reskin/body-roster/hero${cfg.id}.png`,Buffer.from(frames.screenshot,'base64'));
  const timing=await page.evaluate(async cfg=>{
   const {container,players}=window.__bodyRoster,events=[];
   for(const p of players)for(const action of ['gongji','jineng','gongji']){
    const seq=cfg.actions[action],expected=seq.frameMap.length/seq.fps*1000,native=[];let calls=0;const start=performance.now(),listener=e=>native.push({name:e.eventObject.name,elapsedMs:performance.now()-start});p._armature.addEventListener(dragonBones.EventObject.FRAME_EVENT,listener,null);
    await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('completion timeout '+p._dbName+' '+action)),expected+2000);p.trigger(action,()=>{calls++;clearTimeout(timeout);resolve();},1);});p._armature.removeEventListener(dragonBones.EventObject.FRAME_EVENT,listener,null);events.push({model:p._dbName,action,expected,calls,elapsedMs:performance.now()-start,native,expectedEvents:seq.nativeEvents||[]});
   }
   for(const p of players)p.trigger('daiji',null,0);await new Promise(r=>setTimeout(r,120));const idle=players.map(p=>({body:p._streetBody.bitmap.visible,native:p._armature.visible,idle:p._characterIdleState.bitmap.visible}));const shared={sameCache:players[0]._streetBody.cache===players[1]._streetBody.cache,users:players[0]._streetBody.cache.users};
   for(const p of players)p.destroy();container.parent.removeChild(container);return {events,idle,shared,after:StreetBody.snapshot()};
  },cfg);
  for(const e of timing.events){assert.equal(e.calls,1);assert(Math.abs(e.elapsedMs-e.expected)<180,JSON.stringify(e));for(const event of e.expectedEvents){const hits=e.native.filter(n=>n.name===event.name);assert.equal(hits.length,1,JSON.stringify(e));assert(Math.abs(hits[0].elapsedMs-event.frame0/cfg.actions[e.action].fps*1000)<100,JSON.stringify(e));}}
  assert(timing.idle.every(r=>!r.body&&!r.native&&r.idle));assert(timing.shared.sameCache&&timing.shared.users===2);assert.equal(timing.after.caches.length,0);assert.equal(timing.after.errors.length,0);
  const report={hero:cfg.id,pass:true,frameChecks:frames.checks.length,clocks:frames.clocks,timing};reports.push(report);console.log(JSON.stringify({hero:cfg.id,pass:true,frameChecks:report.frameChecks}));
 }
 assert.equal(errors.length,0);await fs.writeFile('art-migration/versions/'+version+'/body-roster.json',JSON.stringify({pass:true,errors,reports},null,2));
}finally{await browser.close();}
