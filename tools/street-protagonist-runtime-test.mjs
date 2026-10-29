import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
await fs.mkdir('art-migration/versions/0.27.0',{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:480,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await page.waitForFunction(()=>window.StreetArt?.audit.installed);await page.waitForTimeout(1000);
 const report=await page.evaluate(async()=>{
  const rows=StreetArtData.resources.filter(r=>r.targetKey.startsWith('street_captain_')),checks=[];
  for(const r of rows){const t=await RES.getResAsync(r.originalKey),direct=await RES.getResAsync(r.targetKey);checks.push({key:r.originalKey,same:t===direct,dimensions:[t.textureWidth,t.textureHeight],expected:r.size});}
  const nodes=[];function walk(n){if(!n.visible)return;if(n.source==='_hero_m_json.wujiang_img_renwu')nodes.push({source:n.source,same:n.texture===RES.getRes('street_captain__hero_m_json_wujiang_img_renwu'),bounds:n.getTransformedBounds(egret.MainContext.instance.stage)});for(let i=0;i<(n.numChildren||0);i++)walk(n.getChildAt(i));}walk(egret.MainContext.instance.stage);
  return {checks,visibleHeader:nodes,audit:StreetArt.audit};
 });
 for(const r of report.checks){assert.equal(r.same,true,r.key);assert.deepEqual(r.dimensions,r.expected,r.key);}assert(report.visibleHeader.length>0);assert(report.visibleHeader.every(r=>r.same));assert.equal(errors.length,0);assert.equal(report.audit.errors.length,0);
 await page.screenshot({path:'outputs/street-reskin/protagonist-heroes-live.png'});await page.mouse.click(444,153);await page.waitForTimeout(1500);await page.screenshot({path:'outputs/street-reskin/protagonist-properties-live.png'});
 await fs.writeFile('art-migration/versions/0.27.0/protagonist-runtime.json',JSON.stringify({pass:true,errors,...report},null,2));console.log(JSON.stringify({pass:true,bindings:report.checks.length,visibleHeader:report.visibleHeader}));
}finally{await browser.close();}
