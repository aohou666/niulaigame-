import fs from 'node:fs/promises';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const action=process.argv.find(v=>v.startsWith('--action='))?.slice(9)||'gongji';
const counts={gongji:32,shouji:18,paobu:10};if(!counts[action])throw Error('Unsupported audited action');
const model=process.argv.includes('--ez')?'hero_002_01_ez':'hero_002_01';
const out='outputs/street-reskin/hero002-native-frames'+(process.argv.includes('--ez')?'-ez':'')+(action==='gongji'?'':'-'+action);await fs.mkdir(out,{recursive:true});const b=await chromium.launch({channel:'chrome',headless:true});
try{
 const p=await b.newPage({viewport:{width:600,height:800}});await p.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await p.waitForFunction(()=>window.StreetBody?.snapshot().installed);
 await p.evaluate(async ({model,action})=>{
  StreetBodyData.characters.find(c=>c.id===2).qualityQuarantineActions=[action];
  const stage=egret.MainContext.instance.stage;for(let i=0;i<stage.numChildren;i++)stage.getChildAt(i).visible=false;
  const background=new egret.Shape();background.graphics.beginFill(0x52646a);background.graphics.drawRect(0,0,stage.stageWidth,stage.stageHeight);background.graphics.endFill();stage.addChild(background);
  const actor=new DBPlayer();stage.addChild(actor);actor.init(model,model.replace(/_ez$/,''));
  await new Promise((resolve,reject)=>{const start=Date.now(),t=setInterval(()=>{if(actor.isReady&&actor._streetBody?.cache.ready){clearInterval(t);resolve();}else if(Date.now()-start>20000){clearInterval(t);reject(Error('load timeout'));}},20);});
  actor.gotoAndStopByFrame(action,0);actor._armature.armature.advanceTime(0);StreetBody.render(actor);
  const bounds=actor.getBounds();actor.scaleX=actor.scaleY=Math.min(stage.stageWidth*.55/bounds.width,stage.stageHeight*.55/bounds.height);actor.x=stage.stageWidth*.5;actor.y=stage.stageHeight*.72;window.__nativeAuditActor=actor;
  document.querySelectorAll('body > :not(.egret-player):not(script):not(style)').forEach(e=>{if(!e.querySelector('canvas'))e.style.visibility='hidden';});
 },{model,action});
 for(let n=0;n<counts[action];n++){
  await p.evaluate(({n,action})=>{const a=__nativeAuditActor;a.gotoAndStopByFrame(action,n);a._armature.armature.advanceTime(0);StreetBody.render(a);},{n,action});
  await p.waitForTimeout(40);await p.screenshot({path:out+'/'+String(n).padStart(2,'0')+'.png'});
 }
 console.log(JSON.stringify({model,action,frames:counts[action],scope:'original native art only'}));
}finally{await b.close();}
