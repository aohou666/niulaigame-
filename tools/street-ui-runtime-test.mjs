import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(v=>v.startsWith('--version='))?.slice(10)||'0.26.0';await fs.mkdir('art-migration/versions/'+version,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:480,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.StreetArt&&StreetArt.audit.installed,null,{timeout:90000});
 const report=await page.evaluate(async()=>{
  const controls=StreetArtData.resources.filter(r=>r.targetKey.startsWith('street_ui_')),checks=[];
  for(const r of controls){const texture=await RES.getResAsync(r.originalKey);const direct=await RES.getResAsync(r.targetKey);checks.push({key:r.originalKey,sameTexture:texture===direct,dimensions:[texture.textureWidth,texture.textureHeight],expected:r.size});}
  const container=new egret.DisplayObjectContainer(),bg=new egret.Shape();bg.graphics.beginFill(0x43565a);bg.graphics.drawRect(0,0,720,900);bg.graphics.endFill();container.addChild(bg);
  const fontColor=0x493520;
  controls.forEach((r,i)=>{const x=(i%3)*240+20,y=Math.floor(i/3)*120+20,b=new egret.Bitmap(RES.getRes(r.originalKey));b.x=x;b.y=y;
   if(i<8){b.width=210;b.height=76;b.scale9Grid=new egret.Rectangle(32,22,r.size[0]-64,r.size[1]-44);const label=new egret.TextField();label.text='确认 · 街区';label.size=23;label.bold=true;label.textColor=fontColor;label.width=210;label.textAlign='center';label.x=x;label.y=y+24;container.addChild(b);container.addChild(label);}else container.addChild(b);
  });
  egret.MainContext.instance.stage.addChild(container);const texture=new egret.RenderTexture();texture.drawToTexture(container,new egret.Rectangle(0,0,720,900));const screenshot=texture.toDataURL('image/png').split(',')[1];texture.dispose();container.parent.removeChild(container);
  // Load the two common control-label sheets afterwards to catch overwritten aliases.
  for(const key of ['_btn_lb_m_json','_btn_yq_m_json'])await RES.getResAsync(key);
  for(const r of controls)checks.find(c=>c.key===r.originalKey).sameAfterSheet=RES.getRes(r.originalKey)===RES.getRes(r.targetKey);
  return {checks,screenshot,audit:StreetArt.audit};
 });
 for(const c of report.checks){assert.equal(c.sameTexture,true,c.key);assert.equal(c.sameAfterSheet,true,c.key);assert.deepEqual(c.dimensions,c.expected,c.key);}assert.equal(errors.length,0);assert.equal(report.audit.errors.length,0);
 await fs.writeFile('outputs/street-reskin/ui-runtime-controls.png',Buffer.from(report.screenshot,'base64'));delete report.screenshot;await page.screenshot({path:'outputs/street-reskin/ui-heroes-live.png'});await fs.writeFile('art-migration/versions/'+version+'/ui-runtime.json',JSON.stringify({pass:true,errors,...report},null,2));console.log(JSON.stringify({pass:true,controls:report.checks.length,errors}));
}finally{await browser.close();}
