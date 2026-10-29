import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(v=>v.startsWith('--version='))?.slice(10)||'0.29.0';await fs.mkdir('art-migration/versions/'+version,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:480,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await page.waitForFunction(()=>window.StreetArt?.audit.installed);await page.waitForTimeout(1000);
 const report=await page.evaluate(async()=>{
  const checks=[],adapter=new AssetAdapter(),changes=AssetAdapter.getSrcChangeConfig()||{},sheetMap=AssetAdapter.getSpiteSheetMap(),expected={};
  for(const r of StreetArtData.resources){
   const texture=await RES.getResAsync(r.originalKey),target=await RES.getResAsync(r.targetKey),actualName=sheetMap[changes[r.originalKey]||r.originalKey]||changes[r.originalKey]||r.originalKey;const adapted=await new Promise(resolve=>adapter.getAsset(r.originalKey,resolve,null)),actual=await RES.getResAsync(actualName);expected[r.originalKey]=actual;for(const alias of r.extraAliases||[])expected[alias]=RES.getRes(alias);
   checks.push({key:r.originalKey,sameDirect:texture===target,dimensions:[texture.textureWidth,texture.textureHeight],expected:r.size,adapterUsesMappedResource:adapted===actual,actualName,aliases:(r.extraAliases||[]).map(key=>({key,same:RES.getRes(key)===target}))});
  }
  const visible=[];function walk(n){if(!n.visible)return;if(typeof n.source==='string'&&expected[n.source]&&n.texture)visible.push({source:n.source,same:n.texture===expected[n.source],bounds:n.getTransformedBounds(egret.MainContext.instance.stage)});for(let i=0;i<(n.numChildren||0);i++)walk(n.getChildAt(i));}walk(egret.MainContext.instance.stage);return {checks,visible,audit:StreetArt.audit};
 });
 for(const r of report.checks){assert(r.sameDirect&&r.adapterUsesMappedResource,r.key);assert.deepEqual(r.dimensions,r.expected,r.key);assert(r.aliases.every(a=>a.same),r.key);}assert(report.visible.length>0);assert(report.visible.every(v=>v.same),JSON.stringify(report.visible.filter(v=>!v.same)));assert.equal(errors.length,0);assert.equal(report.audit.errors.length,0);
 await page.screenshot({path:'outputs/street-reskin/resources-heroes-live.png'});await fs.writeFile('art-migration/versions/'+version+'/resource-runtime.json',JSON.stringify({pass:true,errors,...report},null,2));console.log(JSON.stringify({pass:true,bindings:report.checks.length,visible:report.visible.length}));
}finally{await browser.close();}
