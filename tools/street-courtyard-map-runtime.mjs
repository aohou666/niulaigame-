import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(x=>x.startsWith('--version='))?.slice(10)||'0.54.0',out='art-migration/versions/'+version;
await fs.mkdir(out,{recursive:true});
const savePath='outputs/street-reskin/stress/8794-save.json',original=await fs.readFile(savePath);
const browser=await chromium.launch({channel:'chrome',headless:true});
let report={pass:false,fixture:'Native default fight theme selects existing dk_01_bg_01 arena; no model/position/gameplay change.'};
try {
 const page=await browser.newPage({viewport:{width:480,height:900}}),errors=[],failed=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()?.errorText}));
 await page.addInitScript(()=>{
  let value;
  Object.defineProperty(window,'FIGHT_CONST',{configurable:true,get(){return value;},set(v){if(v?.DEF_THEME)v.DEF_THEME.bg='dk_01_bg_01';value=v;}});
 });
 await page.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=demo');
 await page.waitForFunction(()=>window.StreetArt?.audit.installed&&window.OfflineLastBattlePayload);
 await page.waitForFunction(()=>{
  const target=RES.getRes('street_cabbage_courtyard_battle_jpg');if(!target)return false;
  function find(n){if(!n.visible)return false;if(n.texture===target)return true;for(let i=0;i<(n.numChildren||0);i++)if(find(n.getChildAt(i)))return true;return false;}
  return find(egret.MainContext.instance.stage);
 },null,{timeout:30000});
 // A map can already exist beneath the loading cover. Require actual fighting
 // before a screenshot is accepted as a visual review of the scene.
 await page.waitForFunction(()=>window.StreetBody?.snapshot().active.some(p=>p.visible&&['gongji','jineng'].includes(p.action)&&p.nativeFrame>3),null,{timeout:60000});
 await page.waitForTimeout(300);
 const result=await page.evaluate(()=>{
  const target=RES.getRes('street_cabbage_courtyard_battle_jpg'),visible=[];
  function walk(n){if(!n.visible)return;if(n.texture===target)visible.push({type:n.constructor?.name,source:n.source,bounds:n.getTransformedBounds(egret.MainContext.instance.stage)});for(let i=0;i<(n.numChildren||0);i++)walk(n.getChildAt(i));}
  walk(egret.MainContext.instance.stage);
  return {theme:FIGHT_CONST.DEF_THEME.bg,sameAlias:RES.getRes('dk_01_bg_01_jpg')===target,size:[target.textureWidth,target.textureHeight],visible,body:StreetBody.snapshot(),artErrors:StreetArt.audit.errors};
 });
 await page.screenshot({path:out+'/courtyard-native-battle.png'});
 assert.equal(result.theme,'dk_01_bg_01');assert(result.sameAlias);assert.deepEqual(result.size,[960,1560]);assert(result.visible.length>0);assert.equal(errors.length,0);assert.equal(failed.length,0);assert.equal(result.artErrors.length,0);
 report={...report,pass:true,...result,errors,failed};console.log(JSON.stringify({pass:true,visible:result.visible.length}));
} catch(e){report.error=e.stack;throw e;}
finally {await browser.close();await fs.writeFile(savePath,original);await fs.writeFile(out+'/courtyard-runtime.json',JSON.stringify(report,null,2));}
