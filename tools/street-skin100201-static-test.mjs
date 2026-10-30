import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out='art-migration/versions/'+(process.argv.find(x=>x.startsWith('--version='))?.split('=')[1]||'0.68.0');await fs.mkdir(out,{recursive:true});
const b=await chromium.launch({channel:'chrome',headless:true});
try{
 const p=await b.newPage({viewport:{width:480,height:900}}),errors=[],failed=[];p.on('pageerror',e=>errors.push(e.message));p.on('requestfailed',r=>failed.push({url:r.url(),failure:r.failure()}));p.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()});});
 await p.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await p.waitForFunction(()=>window.CharacterArt?.audit.installed&&window.HeroDermaListItem);
 const result=await p.evaluate(async()=>{
  const cfg=config.HeroDermaLO.Get(100201),base=config.HeroLO.Get(41010002),fields=['avatar','avatar2','halfPic','dermaPic'],expected=[[111,111],[97,98],[221,130],[135,82]],stage=egret.MainContext.instance.stage;
  for(let i=0;i<stage.numChildren;i++)stage.getChildAt(i).visible=false;
  const bg=new egret.Shape();bg.graphics.beginFill(0x52646a);bg.graphics.drawRect(0,0,stage.stageWidth,stage.stageHeight);bg.graphics.endFill();stage.addChild(bg);
  const rows=[];
  for(let i=0;i<fields.length;i++){
   const field=fields[i],name=cfg[field]+'_png',texture=await RES.getResAsync(name),binding=CharacterArtData.heroes['2'].bindings[Object.keys(CharacterArtData.heroes['2'].bindings).find(k=>CharacterArtData.heroes['2'].bindings[k].name===name)];
   const img=new eui.Image(name);img.x=45;img.y=80+i*160;stage.addChild(img);img.validateNow();
   rows.push({field,name,skinCode:binding?.skinCode,url:binding?.url,size:[texture.textureWidth,texture.textureHeight],expected:expected[i],actualTexture:img.texture===texture,source:img.source});
  }
  const host=new eui.Component();host.skinName=HeroDermaListItem;host.x=330;host.y=80;stage.addChild(host);host.validateNow();host.img_di.source=cfg.dermaPic+'_png';host.img_on.visible=false;host.img_red.visible=false;await new Promise(r=>setTimeout(r,700));host.validateNow();
  const card={source:host.img_di.source,textureCorrect:host.img_di.texture===RES.getRes(cfg.dermaPic+'_png'),size:[host.img_di.texture?.textureWidth,host.img_di.texture?.textureHeight]};
  return {rows,card,baseAvatarPreserved:!base.avatar.includes('skin100201'),scope:'Four static bindings and actual HeroDermaListItem skin component; equip, body animations and battle not validated'};
 });
 for(const r of result.rows){assert.equal(r.skinCode,100201);assert(r.url.includes('/skins/100201/'));assert.deepEqual(r.size,r.expected);assert(r.actualTexture);}
 assert(result.baseAvatarPreserved);assert(result.card.textureCorrect);assert.deepEqual(result.card.size,[135,82]);assert.equal(errors.length,0);assert.equal(failed.length,0);
 await p.screenshot({path:out+'/skin100201-static-native.png'});await fs.writeFile(out+'/skin100201-static-native.json',JSON.stringify({pass:true,...result,errors,failed},null,2));console.log(JSON.stringify({pass:true,bindings:result.rows.length,nativeCard:true}));
}finally{await b.close();}
