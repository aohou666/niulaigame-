import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'),version=process.argv.find(v=>v.startsWith('--version='))?.slice(10)||'0.32.0';
const browser=await chromium.launch({channel:'chrome',headless:true});try{
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await page.waitForFunction(()=>window.OfflineHitEvents?.audit.installed&&StreetBody.snapshot().installed);
 const result=await page.evaluate(async()=>{
  const reports=[];
  for(const model of ['hero_082_03','hero_082_03_ez'])for(const action of ['gongji','jineng']){
   const p=new DBPlayer();p.x=200;p.y=300;egret.MainContext.instance.stage.addChild(p);p.init(model,model.replace(/_ez$/,''));await new Promise(resolve=>{const timer=setInterval(()=>{if(p.isReady&&p._streetBody?.cache.ready){clearInterval(timer);resolve();}},10);});
   const native=[],callbacks=[],start=performance.now(),listener=e=>native.push({name:e.eventObject.name,time:e.eventObject.time});p.armature.addEventListener(dragonBones.EventObject.FRAME_EVENT,listener,null);
   await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('native completion timeout')),4000);p.armature.once(dragonBones.EventObject.COMPLETE,()=>{clearTimeout(timeout);resolve();},null);p.trigger(action,()=>callbacks.push({elapsed:performance.now()-start,keyFrame:p.keyFrame}),1,['pia'],true,true);});
   reports.push({model,action,native,callbacks,expectedImpactMs:(action==='gongji'?28:31)/30*1000});p.destroy();
  }
  return {reports,audit:OfflineHitEvents.audit,body:StreetBody.snapshot()};
 });
 for(const r of result.reports){assert.equal(r.native.filter(e=>e.name==='pia').length,2);assert.equal(r.native[0].time,0);assert.equal(r.callbacks.length,1);assert.equal(r.callbacks[0].keyFrame,'pia');assert(Math.abs(r.callbacks[0].elapsed-r.expectedImpactMs)<110,JSON.stringify(r));}assert.equal(errors.length,0);assert.equal(result.body.caches.length,0);assert.equal(result.body.errors.length,0);assert.equal(result.audit.ignoredStartupMarkers.length,4);
 await fs.mkdir('art-migration/versions/'+version,{recursive:true});await fs.writeFile('art-migration/versions/'+version+'/paired-hit-runtime.json',JSON.stringify({pass:true,errors,...result},null,2));console.log(JSON.stringify({pass:true,cases:result.reports.length,ignoredMarkers:result.audit.ignoredStartupMarkers.length}));
}finally{await browser.close();}
