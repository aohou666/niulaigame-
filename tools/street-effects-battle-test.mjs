import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const browser=await chromium.launch({channel:'chrome',headless:true});let page;
try{
 page=await browser.newPage({viewport:{width:480,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8791/index_bh_lite3zbtest_andr.html?mode=demo',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.StreetEffects&&StreetEffects.snapshot().framesPresented>8&&StreetEffects.snapshot().active.some(p=>p.ready&&p.frame>=4&&p.frame<40),null,{timeout:90000});
 const active=await page.evaluate(()=>StreetEffects.snapshot());await page.screenshot({path:'outputs/street-reskin/effect-battle-live.png'});
 assert.equal(errors.length,0);assert(active.active.some(p=>!p.nativeVisible));
 await page.waitForTimeout(3000);
 const after=await page.evaluate(()=>StreetEffects.snapshot());
 await fs.writeFile('art-migration/versions/0.24.0/effect-battle.json',JSON.stringify({pass:true,saveIsolation:'outputs/street-reskin/effect-test-save.json at port 8791',active,after,errors},null,2));
 console.log(JSON.stringify({pass:true,active:active.active,errors}));
}catch(e){
 await page?.screenshot({path:'outputs/street-reskin/effect-battle-failure.png'}).catch(()=>{});
 const state=await page?.evaluate(()=>({effects:window.StreetEffects&&StreetEffects.snapshot(),url:location.href})).catch(()=>null);
 await fs.writeFile('art-migration/versions/0.24.0/effect-battle-failure.json',JSON.stringify({pass:false,error:e.message,state},null,2));throw e;
}finally{await browser.close();}
