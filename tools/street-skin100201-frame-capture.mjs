import fs from 'node:fs/promises';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const action=process.argv.find(v=>v.startsWith('--action='))?.slice(9)||'gongji';
const counts={gongji:45,jineng:46,shouji:21,daiji:198,paobu:16,effect_1:19,effect_2:19,effect_3:39};if(!counts[action])throw Error('Unsupported audited action');
const model=process.argv.includes('--ez')?'hero_skin_002_01_ez':'hero_skin_002_01';
const out=process.argv.find(v=>v.startsWith('--output='))?.slice(9)||'outputs/street-reskin/skin100201-native-frames'+(process.argv.includes('--ez')?'-ez':'')+(action==='gongji'?'':'-'+action);await fs.mkdir(out,{recursive:true});const b=await chromium.launch({channel:'chrome',headless:true});
try{
 const p=await b.newPage({viewport:{width:600,height:800}});await p.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await p.waitForFunction(()=>window.StreetBody?.snapshot().installed);
 await p.evaluate(async ({model,action,count})=>{
  StreetBodyData.characters.find(c=>c.id===2).qualityQuarantineActions=[action];
  const stage=egret.MainContext.instance.stage;for(let i=0;i<stage.numChildren;i++)stage.getChildAt(i).visible=false;
  const background=new egret.Shape();background.graphics.beginFill(0x52646a);background.graphics.drawRect(0,0,stage.stageWidth,stage.stageHeight);background.graphics.endFill();stage.addChild(background);
  const actor=new DBPlayer();stage.addChild(actor);actor.init(model,action.startsWith('effect_')?action:model.replace(/_ez$/,''));
  await new Promise((resolve,reject)=>{const start=Date.now(),t=setInterval(()=>{if(actor.isReady){clearInterval(t);resolve();}else if(Date.now()-start>20000){clearInterval(t);reject(Error('load timeout'));}},20);});
  actor._armature.animation.gotoAndStopByFrame(action,0);actor._armature.armature.advanceTime(0);StreetBody.render(actor);
  let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;for(let i=0;i<count;i++){actor._armature.animation.gotoAndStopByFrame(action,i);actor._armature.armature.advanceTime(0);const r=actor.getBounds();minX=Math.min(minX,r.x);minY=Math.min(minY,r.y);maxX=Math.max(maxX,r.x+r.width);maxY=Math.max(maxY,r.y+r.height);}const scale=Math.min(stage.stageWidth*.6/(maxX-minX),stage.stageHeight*.6/(maxY-minY));actor.scaleX=actor.scaleY=scale;actor.x=stage.stageWidth*.5-(minX+maxX)*.5*scale;actor.y=stage.stageHeight*.5-(minY+maxY)*.5*scale;window.__nativeAuditActor=actor;window.__captureFit={bounds:{minX,minY,maxX,maxY},scale,x:actor.x,y:actor.y,count};
  document.querySelectorAll('body > :not(.egret-player):not(script):not(style)').forEach(e=>{if(!e.querySelector('canvas'))e.style.visibility='hidden';});
 },{model,action,count:counts[action]});
 for(let n=0;n<counts[action];n++){
  await p.evaluate(({n,action})=>{const a=__nativeAuditActor;a._armature.animation.gotoAndStopByFrame(action,n);a._armature.armature.advanceTime(0);StreetBody.render(a);},{n,action});
  await p.waitForTimeout(40);await p.screenshot({path:out+'/'+String(n).padStart(2,'0')+'.png'});
 }
 await fs.writeFile(out+'/capture-fit.json',JSON.stringify(await p.evaluate(()=>__captureFit),null,2));
 console.log(JSON.stringify({model,action,frames:counts[action],scope:'original native art only'}));
}finally{await b.close();}
