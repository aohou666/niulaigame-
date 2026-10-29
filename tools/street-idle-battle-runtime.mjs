import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const id=Number(process.argv[2]),version=process.argv[3];assert(id&&version);
const savePath='outputs/street-reskin/stress/8794-save.json',original=await fs.readFile(savePath,'utf8');
const save=JSON.parse(original),hero=save.heroes.find(h=>h.code===41010000+id);assert(hero);
save.formation=[{uuid:hero.uuid,pos:1}];save.progress.battles=0;save.progress.wins=0;save.progress.stage=1;
save.battleConfig={scenario:'wei',difficulty:'hell',enemyCount:8,enemySubTypes:[1,3,5,7,9,11,15,17]};
save.battleEntities=[];delete save.pendingBattle;
const b=await chromium.launch({channel:'chrome',headless:true});
try{
 await fs.writeFile(savePath,JSON.stringify(save,null,2));
 const page=await b.newPage({viewport:{width:480,height:900}}),errors=[],failures=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failures.push(r.url());});
 await page.addInitScript(()=>{window.__idleTrace=[];setInterval(()=>{if(window.CharacterIdle&&__idleTrace.length<4000)__idleTrace.push(CharacterIdle.snapshot());},25);});
 await page.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=demo');
 await page.waitForFunction(id=>window.CharacterIdle?.snapshot().active.some(p=>p.hero===id&&p.visible&&p.fit?.mode==='battle'),id,{timeout:60000});
 await page.waitForTimeout(8000);
 await page.screenshot({path:`art-migration/versions/${version}/idle-battle-${id}.png`});

 const trace=await page.evaluate(()=>__idleTrace),rows=trace.flatMap(t=>t.active).filter(p=>p.hero===id&&p.visible&&p.fit?.mode==='battle');
 await fs.writeFile(`art-migration/versions/${version}/idle-battle-${id}-samples.json`,JSON.stringify({rows,errors,failures},null,2));
 assert(rows.length>0);assert(rows.every(r=>r.frames===124&&r.cache.atlas));assert(rows.every(r=>r.fit.drawHeight<=r.fit.height+1&&r.fit.drawWidth<=r.fit.width+1&&r.renderBounds.height<=136&&r.renderBounds.width<=146));
 assert.equal(errors.length,0);assert.equal(failures.length,0);
 const result={pass:true,hero:id,scope:'Actual isolated native battle idle rendering, not approval of original attack/skill art',visibleSamples:rows.length,distinctFrames:new Set(rows.map(r=>r.frame)).size,errors,failures,rows};
 await fs.writeFile(`art-migration/versions/${version}/idle-battle-${id}.json`,JSON.stringify(result,null,2));console.log(JSON.stringify({pass:true,hero:id,visibleSamples:rows.length,distinctFrames:result.distinctFrames}));
}finally{await b.close();await fs.writeFile(savePath,original);}
