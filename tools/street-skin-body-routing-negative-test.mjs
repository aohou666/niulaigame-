import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out='art-migration/versions/0.88.0',mode=process.argv.includes('--duplicate')?'duplicate':process.argv.includes('--wrong-id')?'wrong-id':'missing-armature';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage(),errors=[],failures=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failures.push(r.url());});
 await page.route('**/street-body-data.js*',async route=>{const s=await fs.readFile('local_game/street-body-data.js','utf8'),data=JSON.parse(s.slice(s.indexOf('=')+1).trim().replace(/;$/,'')),cfg=data.skins['100201'];
  if(mode==='duplicate')data.skins['100202']={...cfg,id:100202,skinCode:100202};else if(mode==='wrong-id')cfg.id=2;else delete cfg.armature;
  await route.fulfill({contentType:'text/javascript',body:'window.StreetBodyData='+JSON.stringify(data)+';'});
 });
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await page.waitForFunction(()=>window.StreetBody?.snapshot().installed);
 const rows=await page.evaluate(async()=>{
  const rows=[];for(const model of ['hero_skin_002_01','hero_skin_002_01_ez']){const p=new DBPlayer();egret.MainContext.instance.stage.addChild(p);p.init(model,'hero_skin_002_01');const start=Date.now();while(!p.isReady&&Date.now()-start<10000)await new Promise(r=>setTimeout(r,10));if(!p.isReady)throw Error('Native model not ready');p.trigger('shouji',null,1);await new Promise(r=>setTimeout(r,100));rows.push({model,body:!!p._streetBody,native:p._armature.visible});p.destroy();if(p.parent)p.parent.removeChild(p);}
  const base=new DBPlayer();egret.MainContext.instance.stage.addChild(base);base.init('hero_002_01','hero_002_01');const start=Date.now();while(!base._streetBody?.cache.ready&&Date.now()-start<10000)await new Promise(r=>setTimeout(r,10));if(!base._streetBody?.cache.ready)throw Error('Base body not ready');base.gotoAndStopByFrame('gongji',12);base._armature.armature.advanceTime(0);StreetBody.render(base);rows.push({baseHero:base._streetBody.cfg.id,body:base._streetBody.bitmap.visible,native:base._armature.visible});base.destroy();if(base.parent)base.parent.removeChild(base);return rows;
 });
 for(const r of rows.slice(0,2))assert(!r.body&&r.native);assert.equal(rows[2].baseHero,2);assert(rows[2].body&&!rows[2].native);
 const after=await page.evaluate(()=>StreetBody.snapshot());assert.equal(after.errors.length,mode==='duplicate'?2:1);assert.equal(after.caches.length,0);assert.equal(after.active.length,0);assert.equal(errors.length,0);assert.equal(failures.length,0);
 await fs.writeFile(out+'/skin-body-negative-'+mode+'.json',JSON.stringify({pass:true,mode,scope:'Browser-only invalid-config fixture; native hit preserved and base2 atlas not poisoned. No source asset/config publication.',rows,after,errors,failures},null,2));console.log(JSON.stringify({pass:true,mode}));
}finally{await browser.close();}
