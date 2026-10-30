import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(x=>x.startsWith('--version='))?.slice(10)||'0.87.0',out='art-migration/versions/'+version;
await fs.mkdir(out,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:600,height:1000}}),errors=[],failures=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failures.push(r.url());});page.on('requestfailed',r=>failures.push(r.url()));
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');
 await page.waitForFunction(()=>window.StreetArt?.audit.installed&&window.skins?.SlgCityView);
 const result=await page.evaluate(async()=>{
  await RES.getResAsync('bycc_img_ditu_png');const target=RES.getRes('street_city_community_courtyard_png');
  const stage=egret.MainContext.instance.stage;
  const nativeSkin=new skins.SlgCityView();const image=nativeSkin.img_bg;
  const source=image.source,grid=image.scale9Grid;
  if(image.parent)image.parent.removeChild(image);
  for(let i=0;i<stage.numChildren;i++)stage.getChildAt(i).visible=false;
  const bg=new egret.Shape();bg.graphics.beginFill(0x26373c);bg.graphics.drawRect(0,0,stage.stageWidth,stage.stageHeight);bg.graphics.endFill();stage.addChild(bg);
  stage.addChild(image);image.horizontalCenter=0;image.x=(stage.stageWidth-960)/2;image.y=120;
  window.__cityMapImage=image;
  return {source,size:[target.textureWidth,target.textureHeight],aliasSame:RES.getRes('bycc_img_ditu_png')===target,grid:{x:grid.x,y:grid.y,width:grid.width,height:grid.height},artErrors:StreetArt.audit.errors,stage:{width:stage.stageWidth,height:stage.stageHeight}};
 });
 assert.equal(result.source,'bycc_img_ditu_png');assert(result.aliasSame);assert.deepEqual(result.size,[960,898]);assert.deepEqual(result.grid,{x:349,y:329,width:16,height:20});assert.equal(result.artErrors.length,0);
 await page.waitForTimeout(400);await page.screenshot({path:out+'/city-map-native-skin.png'});
 const rows=[];
 for(const [width,height] of [[960,898],[960,1098],[720,898]]){
  const row=await page.evaluate(({width,height})=>{const im=__cityMapImage;im.width=width;im.height=height;im.x=(egret.MainContext.instance.stage.stageWidth-width)/2;return {width:im.width,height:im.height,source:im.source,texture:[im.texture.textureWidth,im.texture.textureHeight],grid:im.scale9Grid};},{width,height});
  assert.equal(row.source,result.source);assert.deepEqual(row.texture,[960,898]);rows.push(row);await page.waitForTimeout(100);await page.screenshot({path:out+`/city-map-${width}x${height}.png`});
 }
 assert.equal(errors.length,0);assert.equal(failures.length,0);
 await fs.writeFile(out+'/city-map-runtime.json',JSON.stringify({pass:true,scope:'Actual native SlgCityView skin img_bg isolated and rendered, alias/dimensions/nine-slice checks. Does not assert city server gameplay or all city panel resources are reskinned.',...result,rows,errors,failures},null,2));
 console.log(JSON.stringify({pass:true,source:result.source,variants:rows.length}));
}finally{await browser.close();}
