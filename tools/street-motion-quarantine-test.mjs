import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const browser=await chromium.launch({channel:'chrome',headless:true});
const report={pass:false,errors:[],rows:[]};
try {
 const page=await browser.newPage({viewport:{width:480,height:900}});
 page.on('pageerror',e=>report.errors.push(e.message));
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');
 await page.waitForFunction(()=>window.StreetBody?.snapshot().installed);
 const configs=await page.evaluate(()=>StreetBodyData.characters.filter(c=>c.qualityQuarantineActions?.length));
 assert.equal(configs.length,32);
 for(const cfg of configs){
  const row=await page.evaluate(async cfg=>{
   const container=new egret.DisplayObjectContainer();egret.MainContext.instance.stage.addChild(container);
   const players=cfg.models.map(name=>{const p=new DBPlayer();container.addChild(p);p.init(name,name.replace(/_ez$/,''));return p;});
   await new Promise((resolve,reject)=>{const start=Date.now(),timer=setInterval(()=>{if(players.every(p=>p.isReady&&p._streetBody?.cache.ready)){clearInterval(timer);resolve();}else if(Date.now()-start>25000){clearInterval(timer);reject(Error('load timeout '+cfg.id));}},25);});
   const checks=[];
   for(const p of players)for(const action of cfg.qualityQuarantineActions){
    const seq=cfg.modelActionOverrides?.[p._dbName]?.[action]||cfg.actions[action];
    for(let n=0;n<seq.frameMap.length;n++){
     p.gotoAndStopByFrame(action,n);p._armature.armature.advanceTime(0);StreetBody.render(p);
     checks.push({model:p._dbName,action,n,bodyVisible:p._streetBody.bitmap.visible,nativeVisible:p._armature.visible,total:p._armature.animation.lastAnimationState.totalTime,expected:seq.frameMap.length/seq.fps});
    }
   }
   const events=[];
   if(cfg.id===5)for(const p of players)for(const action of cfg.qualityQuarantineActions){
    const seq=cfg.modelActionOverrides?.[p._dbName]?.[action]||cfg.actions[action],native=[];let calls=0;
    const listener=e=>native.push(e.eventObject.name);p._armature.addEventListener(dragonBones.EventObject.FRAME_EVENT,listener,null);
    await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('callback timeout')),seq.frameMap.length/seq.fps*1000+2000);p.trigger(action,()=>{calls++;clearTimeout(timer);resolve();},1);});
    p._armature.removeEventListener(dragonBones.EventObject.FRAME_EVENT,listener,null);
    events.push({model:p._dbName,action,calls,events:native.filter(n=>['pia','zd'].includes(n)),expected:(seq.nativeEvents||[]).map(e=>e.name)});
   }
   for(const p of players)p.destroy();container.parent.removeChild(container);
   return {heroId:cfg.id,checks,events,after:StreetBody.snapshot()};
  },cfg);
  for(const c of row.checks){assert(!c.bodyVisible&&c.nativeVisible,JSON.stringify(c));assert(Math.abs(c.total-c.expected)<.0001);}
  for(const e of row.events){assert.equal(e.calls,1);assert.deepEqual(e.events,e.expected);}
  assert.equal(row.after.caches.length,0);assert.equal(row.after.errors.length,0);
  report.rows.push({heroId:row.heroId,frameChecks:row.checks.length,events:row.events,cacheReleased:true});
  console.log(JSON.stringify(report.rows.at(-1)));
 }
 assert.equal(report.errors.length,0);report.pass=true;
} finally {
 await fs.mkdir('art-migration/versions/0.48.0',{recursive:true});
 await fs.writeFile('art-migration/versions/0.48.0/motion-quarantine-runtime.json',JSON.stringify(report,null,2));
 await browser.close();
}
