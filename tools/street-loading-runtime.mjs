import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(x=>x.startsWith('--version='))?.slice(10)||'0.55.0',out='art-migration/versions/'+version;
const progressStates=process.argv.includes('--progress-states');
await fs.mkdir(out,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true});
const errors=[],failed=[],responses=[],held=[],report={pass:false,fixture:'Hold native localdata download briefly for capture; no synthetic loading view, gameplay or save mutation. Not a performance measurement.'};
try {
 const page=await browser.newPage({viewport:{width:480,height:900}});
 page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()?.errorText}));page.on('response',r=>responses.push(r.url()));
 await page.route('**/resource/localdata/*.bin*',async route=>{held.push(route.request().url());await new Promise(r=>setTimeout(r,progressStates?8000:2500));await route.continue();});
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');
 await page.waitForFunction(()=>{
  if(!window.RES?.config?.config?.fileSystem||!window.egret)return false;const target=RES.getRes('street_courier_shutter_loading_jpg');if(!target)return false;
  function walk(n){if(!n.visible)return false;if(n.texture===target)return true;for(let i=0;i<(n.numChildren||0);i++)if(walk(n.getChildAt(i)))return true;return false;}
  return walk(egret.MainContext.instance.stage);
 },null,{timeout:20000});
 report.loading=await page.evaluate(()=>{
  const target=RES.getRes('street_courier_shutter_loading_jpg'),visible=[];
  function walk(n){if(!n.visible)return;if(n.texture===target)visible.push({source:n.source,bounds:n.getTransformedBounds(egret.MainContext.instance.stage)});for(let i=0;i<(n.numChildren||0);i++)walk(n.getChildAt(i));}
  walk(egret.MainContext.instance.stage);return {sameAlias:RES.getRes('login13_bg_jpg')===target,size:[target.textureWidth,target.textureHeight],visible,art:JSON.parse(JSON.stringify(StreetArt.audit))};
 });
 await page.screenshot({path:out+'/native-loading.png'});
 if(progressStates){
  await page.waitForFunction(()=>{
   function find(n){if(n instanceof eui.ProgressBar&&n.thumb?.texture===RES.getRes('street_loading_denglu_img_jindutiao_png'))return n;for(let i=0;i<(n.numChildren||0);i++){const p=find(n.getChildAt(i));if(p)return p;}return null;}
   const bar=find(egret.MainContext.instance.stage);if(!bar)return false;window.__streetProgressFixture={bar,value:bar.value,maximum:bar.maximum,slideDuration:bar.slideDuration,owner:bar.parent};return true;
  });
  await page.evaluate(()=>{const f=__streetProgressFixture;f.owner.stopProgress?.();f.bar.slideDuration=0;f.bar.maximum=100;});
  report.progressStates=[];
  for(const percent of [0,25,50,100]){
   const state=await page.evaluate(percent=>{const b=__streetProgressFixture.bar;b.value=percent;b.validateNow();return {percent,value:b.value,maximum:b.maximum,fill:[b.thumb.x,b.thumb.y,b.thumb.width,b.thumb.height],clip:b.thumb.scrollRect&&{x:b.thumb.scrollRect.x,y:b.thumb.scrollRect.y,width:b.thumb.scrollRect.width,height:b.thumb.scrollRect.height}};},percent);
   assert.equal(state.value,percent);assert.deepEqual(state.fill,[206,17,546,23]);assert(state.clip&&Math.abs(state.clip.width-546*percent/100)<=1,JSON.stringify(state));
   report.progressStates.push(state);await page.screenshot({path:out+'/loading-progress-'+percent+'.png'});
  }
  await page.evaluate(()=>{const f=__streetProgressFixture;f.bar.maximum=f.maximum;f.bar.value=f.value;f.bar.slideDuration=f.slideDuration;f.owner.startProgress?.();delete window.__streetProgressFixture;});
 }
 await page.waitForFunction(()=>window.CharacterReskinAudit&&window.StreetArt.audit.installed,null,{timeout:60000});
 report.finalArt=await page.evaluate(()=>StreetArt.audit);
 assert(report.loading.sameAlias&&report.loading.visible.length>0);assert.deepEqual(report.loading.size,[960,1560]);assert(report.loading.art.earlyConfigInstalls>0);assert.equal(report.finalArt.errors.length,0);
 report.originalLoadingResponses=responses.filter(u=>u.includes('/loading/login13_bg_'));assert.equal(report.originalLoadingResponses.length,0,'Original loading image fetched before replacement');
 assert.equal(errors.length,0);assert.equal(failed.length,0);report.pass=true;console.log(JSON.stringify({pass:true,earlyConfigInstalls:report.loading.art.earlyConfigInstalls,originalResponses:0}));
} catch(e){report.error=e.stack;throw e;}
finally{report.errors=errors;report.failed=failed;report.held=held;report.responses=responses;await browser.close();await fs.writeFile(out+'/loading-runtime.json',JSON.stringify(report,null,2));}
