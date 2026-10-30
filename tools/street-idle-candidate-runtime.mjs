import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const folder=process.argv[2];assert(folder,'candidate-pack directory required');
const candidate=JSON.parse(await fs.readFile(path.join(folder,'candidate.json'),'utf8'));
assert(!candidate.skinCode,'Independent skin candidates require their own runtime fixture; do not replace the base hero');
const live=process.argv.includes('--live');
const id=candidate.heroId,raw=process.argv.includes('--raw'),formation=process.argv.includes('--formation'),label=(live?'live-':'')+(raw?'raw':'atlas')+(formation?'-formation':'');
const idleText=await fs.readFile('local_game/character-idle-data.js','utf8');
const atlasText=await fs.readFile('local_game/character-idle-atlas-data.js','utf8');
const parse=s=>JSON.parse(s.slice(s.indexOf('=')+1).trim().replace(/;$/,''));
const idle=parse(idleText),atlas=parse(atlasText),cfg=idle.heroes[id];
Object.assign(cfg,{frameCount:candidate.frameCount,width:512,height:512,crop:candidate.crop,
  bodyHeight:candidate.crop[3],fps:24,baseUrl:'candidate-idle/',files:candidate.fallback.map(f=>f.file)});
const profiles=structuredClone(candidate.profiles);
for(const pack of Object.values(profiles))for(const page of pack.pages)page.url='candidate-idle/'+page.file;
atlas.heroes[id]={profiles,frameCount:candidate.frameCount,crop:candidate.crop,sourceSequenceSha256:candidate.sourceSignature};
cfg.atlas=raw?null:atlas.heroes[id];
if(raw)delete atlas.heroes[id];
const browser=await chromium.launch({channel:'chrome',headless:true});
const errors=[],failures=[],samples=[];
try{
 const page=await browser.newPage({viewport:{width:480,height:900}});
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failures.push({url:r.url(),status:r.status()});});
 if(!live)await page.route('**/character-idle-data.js*',r=>r.fulfill({contentType:'application/javascript',body:idleText.slice(0,idleText.indexOf('=')+1)+JSON.stringify(idle)+';'}));
 if(!live)await page.route('**/character-idle-atlas-data.js*',r=>r.fulfill({contentType:'application/javascript',body:atlasText.slice(0,atlasText.indexOf('=')+1)+JSON.stringify(atlas)+';'}));
 await page.route('**/candidate-idle/*.webp',r=>r.fulfill({contentType:'image/webp',path:path.join(folder,path.basename(new URL(r.request().url()).pathname))}));
 await page.route('**/candidate-idle/*.png',r=>r.fulfill({contentType:'image/png',path:path.join(folder,path.basename(new URL(r.request().url()).pathname))}));
 await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');
 await page.waitForFunction(()=>window.CharacterArt?.audit.installed);
 await page.evaluate(({id,formation})=>{const h=game.GameMVC.heroPy.heroBag.getItems().find(h=>Number(h.config.subType)===id);if(formation){const view=new game.FormationModelComponent();view.x=200;view.y=300;egret.MainContext.instance.stage.addChild(view);view.validateNow();view.update({heroInfo:h,isTool:true});window.__candidateFormation=view;}else game.AppFacade.getInstance().showSubView(game.HeroMediator.N,game.HeroMediator.SV.NEW_HERO_MAIN_INFO,{uuid:h.uuid});},{id,formation});
 await page.waitForFunction(id=>window.CharacterIdle?.snapshot().active.some(p=>p.hero===id&&p.visible&&p.textureSize),id);
 for(let n=0;n<160;n++){
  const s=await page.evaluate(id=>CharacterIdle.snapshot().active.find(p=>p.hero===id&&p.visible),id);
  assert(s);assert.equal(s.cache.atlas,!raw);assert.equal(s.frames,candidate.frameCount);samples.push(s);
  if(n===10||n===150)await page.screenshot({path:path.join(folder,`native-${label}-detail-${n}.png`)});
  await page.waitForTimeout(50);
 }
 const wraps=samples.filter((s,i)=>i&&s.frame<samples[i-1].frame).length;
 assert(wraps>=1,'No actual loop wrap observed');assert.equal(errors.length,0);assert.equal(failures.length,0);
 assert(samples.every(s=>s.fit.drawHeight<=(formation?146:271)&&s.fit.drawWidth<=(formation?121:421)));
 assert(samples.every(s=>s.fit.mode===(formation?'formation':'detail')));
 const report={pass:true,hero:id,mode:label,liveRuntimeFiles:live,scope:formation?'Native FormationModelComponent fixture; not full formation screen/save flow':'Native detail view; read-only candidate routes; runtime files unchanged',wraps,errors,failures,samples};
 await fs.writeFile(path.join(folder,`native-${label}-runtime.json`),JSON.stringify(report,null,2));
 console.log(JSON.stringify({pass:true,hero:id,wraps,samples:samples.length}));
}finally{await browser.close();}
