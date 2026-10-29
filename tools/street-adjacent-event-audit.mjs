import fs from 'node:fs/promises';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out='outputs/street-reskin/hero002-adjacent-events';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
try {
 const page=await browser.newPage({viewport:{width:720,height:900}});
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');
 await page.waitForFunction(()=>window.StreetBody?.snapshot().installed);
 const result=await page.evaluate(async()=>{
  const cfg=StreetBodyData.characters.find(c=>c.id===2);cfg.qualityQuarantineActions=['gongji'];
  const stage=egret.MainContext.instance.stage,rows=[];
  for(const model of cfg.models){
   const p=new DBPlayer();stage.addChild(p);p.init(model,model.replace(/_ez$/,''));
   await new Promise((resolve,reject)=>{const started=Date.now(),t=setInterval(()=>{if(p.isReady&&p._streetBody?.cache.ready){clearInterval(t);resolve();}else if(Date.now()-started>20000){clearInterval(t);reject(Error('Load timeout'));}},20);});
   const frames=[];
   for(let n=0;n<32;n++){
    p.gotoAndStopByFrame('gongji',n);p._armature.armature.advanceTime(0);StreetBody.render(p);
    frames.push({frame:n,bones:p._armature.armature.getBones().map(b=>({name:b.name,x:b.global.x,y:b.global.y,rotation:b.global.rotation,skew:b.global.skew}))});
   }
   const events=[],callbacks=[];p._armature.addEventListener(dragonBones.EventObject.FRAME_EVENT,e=>events.push({name:e.eventObject.name,time:e.eventObject.time}),null);
   await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Completion timeout')),3000);p._armature.once(dragonBones.EventObject.COMPLETE,()=>{clearTimeout(timer);resolve();},null);p.trigger('gongji',()=>callbacks.push({key:p.keyFrame,time:performance.now()}),1,['pia','zd'],true,true);});
   rows.push({model,frames,events,callbacks});p.destroy();
  }
  return{rows,scope:'Native bone trajectory and real callback observation; does not prove number of intended visual strikes by itself'};
 });
 await fs.writeFile(out+'/native-audit.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result.rows.map(r=>({model:r.model,frames:r.frames.length,events:r.events,callbacks:r.callbacks}))));
}finally{await browser.close();}
