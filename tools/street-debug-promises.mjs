import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:480,height:900}}),cdp=await page.context().newCDPSession(page),events=[];
 await cdp.send('Debugger.enable');await cdp.send('Debugger.setPauseOnExceptions',{state:'uncaught'});
 cdp.on('Debugger.paused',async e=>{events.push({reason:e.reason,data:e.data,frames:e.callFrames.map(f=>({name:f.functionName,url:f.url,location:f.location})).slice(0,10)});await cdp.send('Debugger.resume');});
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes&heroaudit=1',{waitUntil:'domcontentloaded'});
 await page.waitForTimeout(7000);
 await fs.writeFile('outputs/street-reskin/promise-debug.json',JSON.stringify(events,null,2));console.log(JSON.stringify(events.slice(0,2)));
}finally{await browser.close();}
