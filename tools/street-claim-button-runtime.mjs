import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(v=>v.startsWith('--version='))?.slice(10)||'0.59.0';
const out='art-migration/versions/'+version;
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
 const duel=await page.evaluate(async()=>{
  const h=__claimFixture.host,b=h.btn_pvp;let n=b;while(n){n.visible=true;n.alpha=1;n=n.parent;}b.validateNow();
  await new Promise(r=>setTimeout(r,500));const target=RES.getRes('street_neighborhood_duel_png'),found=[];
  function walk(n){if(n.source==='fhqp_btn_duizhan_png')found.push({source:n.source,replacement:!!target&&n.texture===target,size:n.texture?[n.texture.textureWidth,n.texture.textureHeight]:null});for(let i=0;i<(n.numChildren||0);i++)walk(n.getChildAt(i));}walk(b);
  return {part:'btn_pvp',found,bounds:b.getTransformedBounds(egret.MainContext.instance.stage)};
 });
 assert(duel.found.some(r=>r.replacement&&r.size[0]===292&&r.size[1]===87),'Native PvP button must show new duel texture');
 await page.screenshot({path:out+'/duel-native.png'});
 await fs.writeFile(out+'/duel-native.json',JSON.stringify({pass:true,scope:'Native skin component only; not matchmaking transaction',duel},null,2));
 const campaign=await page.evaluate(async()=>{
  const h=__claimFixture.host,b=h.btn_pve;let n=b;while(n){n.visible=true;n.alpha=1;n=n.parent;}b.validateNow();
  await new Promise(r=>setTimeout(r,500));const target=RES.getRes('street_neighborhood_campaign_png'),found=[];
  function walk(n){if(n.source==='fhqp_btn_zhanyi_png')found.push({source:n.source,replacement:!!target&&n.texture===target,size:n.texture?[n.texture.textureWidth,n.texture.textureHeight]:null});for(let i=0;i<(n.numChildren||0);i++)walk(n.getChildAt(i));}walk(b);
  return {part:'btn_pve',found,bounds:b.getTransformedBounds(egret.MainContext.instance.stage)};
 });
 assert(campaign.found.some(r=>r.replacement&&r.size[0]===292&&r.size[1]===87),'Native PvE button must show new campaign texture');
 await page.screenshot({path:out+'/campaign-native.png'});
 await fs.writeFile(out+'/campaign-native.json',JSON.stringify({pass:true,scope:'Native skin component only; not matchmaking transaction',campaign},null,2));
 assert.equal(errors.length,0);
 const scene=await page.evaluate(()=>{
  const h=__claimFixture.host;
  return ['img_bg','img_title'].map(part=>{const n=h[part],r=StreetArtData.resources.find(r=>r.originalKey===n.source);return{part,source:n.source,replacementBound:!!r&&n.texture===RES.getRes(r.targetKey),visible:n.visible,bounds:n.getTransformedBounds(egret.MainContext.instance.stage)};});
 });
 assert(scene.every(r=>r.replacementBound&&r.visible),'Lobby background/title must actually use their replacements');
 await fs.writeFile(out+'/claim-native-skin.json',JSON.stringify({pass:true,scope:'Actual NightDemonPvpViewSkin component fixture; no reward transaction or full activity flow tested',errors,checks,scene},null,2));
 console.log(JSON.stringify({pass:true,checks}));
} finally {await browser.close();}
