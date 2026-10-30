import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const folder='art-migration/generation/skin100201-native-body107-packed-trial-v2',entries=JSON.parse(await fs.readFile(folder+'/candidate-containers.json','utf8'));
const browser=await chromium.launch({channel:'chrome',headless:true});let report={pass:false,productionIntegrated:false,scope:'Warm native normal+EZ two actors, all five action loops, 20 seconds on this PC headless Chrome only; no mobile or universal lag-free claim.'};
try{const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const name of ['street-art-data.js','character-idle-data.js','street-body-data.js'])await page.route('**/'+name+'*',async route=>{const text=await fs.readFile('local_game/'+name,'utf8'),prefix=text.slice(0,text.indexOf('=')+1),data=JSON.parse(text.slice(text.indexOf('=')+1).trim().replace(/;$/,''));if(name==='street-art-data.js')data.containers=[...data.containers.filter(e=>!entries.some(r=>r.originalKey===e.originalKey)),...entries];else delete data.skins['100201'];await route.fulfill({contentType:'text/javascript',body:prefix+JSON.stringify(data)+';'});});
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await page.waitForFunction(()=>window.StreetBody?.snapshot().installed&&CharacterIdle.snapshot().installed);
 report.runtime=await page.evaluate(async()=>{
  const stage=egret.MainContext.instance.stage;for(let i=0;i<stage.numChildren;i++)stage.getChildAt(i).visible=false;
  const players=['hero_skin_002_01','hero_skin_002_01_ez'].map((model,i)=>{const a=new DBPlayer();a.x=i?450:160;a.y=600;a.scaleX=a.scaleY=i?.65:.325;stage.addChild(a);a.init(model,'hero_skin_002_01');return a;});
  const began=performance.now();while(!players.every(a=>a.isReady)&&performance.now()-began<15000)await new Promise(r=>setTimeout(r,10));if(!players.every(a=>a.isReady&&!a._streetBody&&!a._characterIdleState))throw Error('Expected native-only actors');
  const actions=['gongji','jineng','shouji','paobu','daiji'];let stopped=false;const completions=[[],[]];players.forEach((a,i)=>{let index=0;function play(){if(stopped)return;const action=actions[index++%actions.length];a.trigger(action,()=>{completions[i].push(action);play();},1);}play();});
  const observed=players.map(()=>new Set()),times=[],longTasks=[];let done=false,last=performance.now();const observer=new PerformanceObserver(list=>longTasks.push(...list.getEntries().map(e=>e.duration)));observer.observe({entryTypes:['longtask']});
  function frame(time){times.push(time-last);last=time;players.forEach((a,i)=>{const s=a._armature?.animation.lastAnimationState;if(s)observed[i].add(s.name+':'+Math.floor(s.currentTime*30));});if(!done)requestAnimationFrame(frame);}requestAnimationFrame(frame);
  await new Promise(r=>setTimeout(r,20000));done=true;stopped=true;observer.disconnect();const sorted=times.slice(1).sort((a,b)=>a-b);
  const beforeDestroy=players.map(a=>({nativeVisible:a._armature?.visible,raster:!!(a._streetBody||a._characterIdleState),onStage:!!a.stage}));
  for(const a of players){a.destroy();if(a.parent)a.parent.removeChild(a);}
  await new Promise(r=>requestAnimationFrame(r));
  return {sampleMs:20000,p95:sorted[Math.floor((sorted.length-1)*.95)],p50:sorted[Math.floor((sorted.length-1)*.5)],over100ms:sorted.filter(x=>x>100).length,longTasks,completions,distinctNativeStates:observed.map(s=>s.size),beforeDestroy,afterDestroy:players.map(a=>({onStage:!!a.stage,armature:!!a._armature})),body:StreetBody.snapshot(),idle:CharacterIdle.snapshot()};
 });
 assert(report.runtime.p95<34);assert(report.runtime.completions.every(list=>['gongji','jineng','shouji','paobu','daiji'].every(a=>list.includes(a))));assert(report.runtime.afterDestroy.every(a=>!a.onStage&&!a.armature));assert.equal(errors.length,0);report.errors=errors;report.pass=true;
}finally{await browser.close();await fs.writeFile(folder+'/native-performance.json',JSON.stringify(report,null,2));}
console.log(JSON.stringify({pass:report.pass,p95:report.runtime?.p95,distinctNativeStates:report.runtime?.distinctNativeStates}));
