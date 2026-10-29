import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out=path.resolve('outputs/street-reskin');await fs.mkdir(out,{recursive:true});
const mode=process.argv.find(v=>v.startsWith('--mode='))?.slice(7)||'heroes';
const suffix=mode==='heroes'?'':`-${mode}`;
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:480,height:900},deviceScaleFactor:1});
const errors=[],failed=[],logs=[],images=[];
const cdp=await page.context().newCDPSession(page);await cdp.send('Runtime.enable');
cdp.on('Runtime.exceptionThrown',e=>errors.push({cdp:e.exceptionDetails}));
page.on('pageerror',e=>errors.push({name:e.name,message:e.message,stack:e.stack}));
await page.addInitScript(()=>{window.__streetErrors=[];addEventListener('error',e=>window.__streetErrors.push({message:e.message,file:e.filename,line:e.lineno,column:e.colno,error:String(e.error)}));addEventListener('unhandledrejection',e=>window.__streetErrors.push({kind:'rejection',reason:String(e.reason),stack:e.reason&&e.reason.stack}));});
page.on('console',m=>{if(logs.length<150)logs.push({type:m.type(),text:m.text().slice(0,1000)});});
page.on('response',r=>{if(r.status()>=400)failed.push({status:r.status(),url:r.url()});if(/\.(png|jpg|webp)(\?|$)/i.test(r.url()))images.push(r.url());});
try {
 await page.goto(`http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=${mode}${mode==='heroes'?'&heroaudit=1':''}`,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.CharacterIdle&&CharacterIdle.snapshot().installed,{timeout:90000});
 await page.waitForTimeout(mode==='heroes'?2500:7000);
 const baseline=await page.evaluate(()=>({
  reskin:CharacterReskinAudit,art:window.CharacterArt&&CharacterArt.audit,idle:CharacterIdle.snapshot(),windowErrors:window.__streetErrors,missingRpc:window.OfflineMissingRpcAudit,
  heroes:Object.values(game.Config.pack.t_hero).map(r=>({code:r.code,subType:r.subType,name:r.name,avatar:r.avatar,avatar2:r.avatar2,halfPic:r.halfPic,model:r.model,pictureDraw:r.pictureDraw,normalSkill:r.normalSkill,actSkill:r.actSkill})),
  skins:Object.values(config.HeroDermaLO.Store).map(r=>r),
  owned:game.GameMVC.heroPy.heroBag.getItems().map(r=>({uuid:r.uuid,code:r.code,id:r.config.subType})),
  viewport:[innerWidth,innerHeight],url:location.href
 }));
 await fs.writeFile(path.join(out,`runtime-baseline${suffix}.json`),JSON.stringify(baseline,null,2));
 await page.screenshot({path:path.join(out,`runtime-${mode}.png`)});
 if(process.argv.includes('--all-heroes')) {
  await page.getByRole('button',{name:'逐项检查85个详情',exact:true}).click();
  await page.waitForFunction(()=>{const el=document.querySelector('#hero-regression-results');try{const r=JSON.parse(el.textContent);return r.checked>0&&r.total>0&&r.checked===r.total;}catch{return false;}},null,{timeout:300000});
  const result=await page.locator('#hero-regression-results').textContent();await fs.writeFile(path.join(out,'all-heroes-runtime.json'),result);
  const parsed=JSON.parse(result);console.log(JSON.stringify({allHeroes:{checked:parsed.checked,passed:parsed.passed,total:parsed.total,failures:parsed.results.filter(r=>!r.pass)}}));
  await fs.writeFile(path.join(out,'all-heroes-post-snapshot.json'),JSON.stringify(await page.evaluate(()=>CharacterIdle.snapshot()),null,2));
  await page.screenshot({path:path.join(out,'runtime-allheroes-last.png')});
 }
 if(process.argv.includes('--metrics')){
  const metrics=await page.evaluate(()=>new Promise(resolve=>{
   const intervals=[];let previous=performance.now(),began=previous;
   function tick(now){intervals.push(now-previous);previous=now;if(intervals.length<300&&now-began<15000){requestAnimationFrame(tick);return;}
    const sorted=intervals.slice(1).sort((a,b)=>a-b);resolve({samples:sorted.length,medianMs:sorted[Math.floor(sorted.length*.5)],p95Ms:sorted[Math.floor(sorted.length*.95)],maxMs:Math.max.apply(null,sorted),elapsedMs:now-began,idle:CharacterIdle.snapshot()});}
   requestAnimationFrame(tick);
  }));
  await fs.writeFile(path.join(out,`frame-metrics${suffix}.json`),JSON.stringify(metrics,null,2));
 }
 console.log(JSON.stringify({installed:baseline.idle.installed,owned:baseline.owned.length,errorCount:errors.length,failed}));
} catch(e){errors.push(e.stack);await page.screenshot({path:path.join(out,'runtime-failure.png')}).catch(()=>{});process.exitCode=1;}
finally{await fs.writeFile(path.join(out,`browser-log${suffix}.json`),JSON.stringify({errors,failed,logs,images},null,2));await browser.close();}
