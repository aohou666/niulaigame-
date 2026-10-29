import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out='art-migration/versions/0.59.0';
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
try {
 const page=await browser.newPage({viewport:{width:480,height:900}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');
 await page.waitForFunction(()=>window.StreetArt?.audit.installed&&window.NightDemonPvpViewSkin);
 await page.evaluate(()=>{
  const host=new eui.Component();host.skinName=NightDemonPvpViewSkin;
  egret.MainContext.instance.stage.addChild(host);host.validateNow();
  let n=host.btn_get;while(n&&n!==host){n.visible=true;n.alpha=1;n=n.parent;}
  window.__claimFixture={host,button:host.btn_get};
 });
 const checks=[];
 for(const enabled of [true,false]){
  await page.evaluate(enabled=>{const b=__claimFixture.button;b.visible=true;b.enabled=enabled;b.icon='phb_btn_lingqu'+(enabled?1:0)+'_png';b.validateNow();},enabled);
  await page.waitForTimeout(500);
  const r=await page.evaluate(enabled=>{const b=__claimFixture.button,t=RES.getRes(enabled?'street_rank_claim_enabled_png':'street_rank_claim_disabled_png');const found=[];function walk(n){if(n.texture)found.push(n.texture===t);for(let i=0;i<(n.numChildren||0);i++)walk(n.getChildAt(i));}walk(b);return{enabled:b.enabled,size:[b.width,b.height],replacementTextureFound:found.includes(true),bounds:b.getTransformedBounds(egret.MainContext.instance.stage)};},enabled);
  checks.push(r);assert.equal(r.enabled,enabled);assert.deepEqual(r.size,[79,81]);assert(r.replacementTextureFound);
  await page.screenshot({path:out+'/claim-'+(enabled?'enabled':'disabled')+'.png'});
 }
 assert.equal(errors.length,0);
 await fs.writeFile(out+'/claim-native-skin.json',JSON.stringify({pass:true,scope:'Actual NightDemonPvpViewSkin component fixture; no reward transaction or full activity flow tested',errors,checks},null,2));
 console.log(JSON.stringify({pass:true,checks}));
} finally {await browser.close();}
