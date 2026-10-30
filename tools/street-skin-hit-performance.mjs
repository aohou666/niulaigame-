import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out='art-migration/versions/0.88.0';const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:600,height:1000}}),errors=[],failures=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failures.push(r.url());});
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await page.waitForFunction(()=>window.StreetBody?.snapshot().installed);
 const result=await page.evaluate(async()=>{
  const stage=egret.MainContext.instance.stage;for(let i=0;i<stage.numChildren;i++)stage.getChildAt(i).visible=false;
  const players=['hero_skin_002_01','hero_skin_002_01_ez'].map((model,i)=>{const p=new DBPlayer();p.x=i?500:220;p.y=700;stage.addChild(p);p.init(model,'hero_skin_002_01');return p;});
  const start=performance.now();while(!players.every(p=>p.isReady&&p._streetBody?.cache.ready)&&performance.now()-start<20000)await new Promise(r=>setTimeout(r,10));if(!players.every(p=>p._streetBody?.cache.ready))throw Error('Atlas load timeout');
  for(const p of players)p.trigger('shouji',null,0);
  const deltas=[],longTasks=[],observed=players.map(()=>new Set());let last=performance.now(),done=false;
  const observer=new PerformanceObserver(list=>{for(const entry of list.getEntries())longTasks.push(entry.duration);});observer.observe({entryTypes:['longtask']});
  function frame(time){deltas.push(time-last);last=time;players.forEach((p,i)=>{if(p._streetBody?.bitmap.visible)observed[i].add(p._streetBody.frame);});if(!done)requestAnimationFrame(frame);}requestAnimationFrame(frame);
  await new Promise(r=>setTimeout(r,15000));done=true;observer.disconnect();
  const sorted=deltas.slice(1).sort((a,b)=>a-b),quantile=p=>sorted[Math.floor((sorted.length-1)*p)],active=StreetBody.snapshot();
  for(const p of players){p.destroy();if(p.parent)p.parent.removeChild(p);}return {sampleMs:15000,frames:sorted.length,p50:quantile(.5),p95:quantile(.95),over50ms:sorted.filter(t=>t>50).length,over100ms:sorted.filter(t=>t>100).length,longTasks,heapUsedBytes:performance.memory?.usedJSHeapSize,distinctFrames:observed.map(set=>set.size),active,after:StreetBody.snapshot()};
 });
 const report={pass:result.p95<34&&result.distinctFrames.every(n=>n===21)&&errors.length===0&&failures.length===0,scope:'15s headless Chrome on this Windows PC, two genuine ordinary/EZ native skin hit loops with shared atlas. Warm rendering only, not full battle AI, APK/mobile or universal no-stutter proof.',...result,errors,failures};
 await fs.writeFile(out+'/skin-hit-performance.json',JSON.stringify(report,null,2));assert(report.pass);assert.equal(result.after.caches.length,0);assert.equal(result.after.active.length,0);assert.equal(result.active.caches.length,1);assert.equal(result.active.caches[0].users,2);
 console.log(JSON.stringify({pass:true,p95:result.p95,over100ms:result.over100ms,distinctFrames:result.distinctFrames,sharedAtlases:result.active.caches.length}));
}finally{await browser.close();}
