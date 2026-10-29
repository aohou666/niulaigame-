import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const browser=await chromium.launch({channel:'chrome',headless:true});let page;
try{
 page=await browser.newPage({viewport:{width:480,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8791/index_bh_lite3zbtest_andr.html?mode=demo',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.StreetBody&&StreetBody.snapshot().active.some(p=>p.visible&&p.action==='gongji'&&p.nativeFrame>=11&&p.nativeFrame<20),null,{timeout:90000});
 const active=await page.evaluate(()=>StreetBody.snapshot());await page.screenshot({path:'outputs/street-reskin/body-battle-live.png'});
 assert.equal(errors.length,0);assert(active.active.some(p=>p.visible&&!p.nativeVisible));
 await page.waitForFunction(()=>StreetBody.snapshot().actions.jineng>4,null,{timeout:90000});
 await fs.writeFile('art-migration/versions/0.25.0/body-battle.json',JSON.stringify({pass:true,saveIsolation:'outputs/street-reskin/effect-test-save.json port8791',active,after:await page.evaluate(()=>StreetBody.snapshot()),errors},null,2));console.log(JSON.stringify({pass:true,active:active.active,errors}));
}catch(e){await page?.screenshot({path:'outputs/street-reskin/body-battle-failure.png'}).catch(()=>{});throw e;}finally{await browser.close();}
