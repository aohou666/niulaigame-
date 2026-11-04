import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const folder='art-migration/generation/skin100201-native-body107-packed-trial-v2';
const endurance=process.argv.includes('--endurance');
const production=process.argv.includes('--production');
const skillScenario=process.argv.includes('--skill-scenario');
const banner=process.argv.includes('--banner');
const active15=process.argv.includes('--active15');
const active16=process.argv.includes('--active16');assert(!active16||active15,'Use --active16 with --active15');
const focusedFX=process.argv.includes('--focus-fx');
const bannerCandidate=banner?JSON.parse(await fs.readFile('art-migration/generation/skin100201-skill-banner-native-v1/candidate.json','utf8')):null;
const out=active16?folder+(focusedFX?'/native-battle-active31-focused':'/native-battle-active31-candidate'):active15?folder+'/native-battle-active15-candidate':(production?'art-migration/versions/0.97.0':folder)+(banner?'/native-battle-skill-banner':skillScenario?'/native-battle-skill-scenario':endurance?'/native-battle-endurance':'/native-battle');await fs.mkdir(out,{recursive:true});
const entries=JSON.parse(await fs.readFile((production?'art-migration/generation/skin100201-native-body-production-v1':folder)+'/candidate-containers.json','utf8'));
if(active15)entries.push(...JSON.parse(await fs.readFile('art-migration/generation/skin100201-active15-native-v3/candidate-containers.json','utf8')));
if(active16)entries.push(...JSON.parse(await fs.readFile('art-migration/generation/skin100201-active16-native-v2/candidate-containers.json','utf8')));
const savePath='outputs/street-reskin/stress/8794-save.json',mainPath='pc_server_data/offline-replica-save.json';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const before=await fs.readFile(savePath),mainBefore=sha(await fs.readFile(mainPath));
const save=JSON.parse(before),hero=save.heroes.find(h=>h.code===41010002);assert(hero);hero.dermaCode=0;
if(endurance){const attrs=JSON.parse(hero.attr);attrs['2']=Number(attrs['2'])*100;hero.attr=JSON.stringify(attrs);}
save.formation=[{uuid:hero.uuid,pos:1}];save.progress.stage=10;save.progress.battles=0;save.progress.wins=0;
save.battleConfig={scenario:'wei',difficulty:'hell',enemyCount:8,enemySubTypes:[1,3,5,7,9,11,15,17],enemyRaces:[1,2,3,4,5,6]};save.battleEntities=[];delete save.pendingBattle;
if(skillScenario){save.progress.stage=1;save.battleConfig.difficulty='normal';}
if(focusedFX)Object.assign(save.battleConfig,{enemyCount:2,enemySubTypes:[14,32],beautyCode:-1,petCode:-1});
if(banner){const attrs=JSON.parse(hero.attr);attrs['1']=Number(attrs['1'])*10;attrs['2']=Number(attrs['2'])*100;hero.attr=JSON.stringify(attrs);}
const browser=await chromium.launch({channel:'chrome',headless:true});let activePage;let report={pass:false,productionConfiguration:production,scope:'Real equip transaction and unedited original BattleAI playback using new native107+40 candidate; no manual animation trigger.',endurance,skillScenario,banner,fixtureAttributeMultipliers:banner?{'1':10,'2':100}:endurance?{'2':100}:{}};
report.fixtureBattleConfig=save.battleConfig;report.focusedFX=focusedFX;
try{
 await fs.writeFile(savePath,JSON.stringify(save,null,2));const page=activePage=await browser.newPage({viewport:{width:600,height:1000}}),errors=[],failures=[],oldRaster=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failures.push(r.url());});page.on('requestfailed',r=>failures.push(r.url()));page.on('request',r=>{if(/\/skins\/100201\/(idle-|actions\/)/.test(r.url()))oldRaster.push(r.url());});
 if(!production||active15)for(const name of ['street-art-data.js','character-idle-data.js','street-body-data.js'])await page.route('**/'+name+'*',async route=>{
  const text=await fs.readFile('local_game/'+name,'utf8'),prefix=text.slice(0,text.indexOf('=')+1),data=JSON.parse(text.slice(text.indexOf('=')+1).trim().replace(/;$/,''));
  if(name==='street-art-data.js'){data.containers=[...data.containers.filter(e=>!entries.some(r=>r.originalKey===e.originalKey)),...entries];if(banner)data.resources=[...data.resources.filter(e=>!bannerCandidate.resources.some(r=>r.originalKey===e.originalKey)),...bannerCandidate.resources];}else delete data.skins['100201'];
  await route.fulfill({contentType:'text/javascript',body:prefix+JSON.stringify(data)+';'});
 });
 await page.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=heroes');await page.waitForFunction(()=>window.game?.GameMVC?.heroThingPy?.AllDermaInfo&&game.GameMVC.heroPy?.heroBag?.getItems().some(h=>h.config.subType===2));
 report.equip=await page.evaluate(()=>{const h=game.GameMVC.heroPy.heroBag.getItems().find(h=>h.config.subType===2),py=game.GameMVC.heroThingPy;let calls=0,results=0;py._offlineSelectedDermaCode=100201;py.HeroDermaPutOn('offline-derma-100201',h.uuid,()=>calls++,()=>results++);return {uuid:h.uuid,dermaCode:h.dermaCode,calls,results};});
 assert.equal(report.equip.dermaCode,100201);assert.equal(report.equip.calls,1);assert.equal(report.equip.results,1);
 for(let i=0;i<100;i++){if(JSON.parse(await fs.readFile(savePath,'utf8')).heroes.find(h=>h.uuid===hero.uuid)?.dermaCode===100201)break;await new Promise(r=>setTimeout(r,20));}
 assert.equal(JSON.parse(await fs.readFile(savePath,'utf8')).heroes.find(h=>h.uuid===hero.uuid).dermaCode,100201);
 await page.addInitScript(()=>{
  window.__nativeBattle={samples:[],triggers:[],events:[],players:[],captures:{}};
  const timer=setInterval(()=>{
   if(!window.StreetBody?.snapshot().installed||!window.DBPlayer)return;clearInterval(timer);
   const init=DBPlayer.prototype.init,trigger=DBPlayer.prototype.trigger;
   DBPlayer.prototype.init=function(){const result=init.apply(this,arguments);if(/^hero_skin_002_01(_ez)?$/.test(String(arguments[0]))&&!this.__nativeTrialTick){__nativeBattle.players.push(this);this.__nativeTrialTick=()=>{
    const arm=this._armature;if(!arm)return;
    if(this.__nativeTrialArm!==arm){this.__nativeTrialArm=arm;arm.addEventListener(dragonBones.EventObject.FRAME_EVENT,e=>__nativeBattle.events.push({name:e.eventObject.name,action:arm.animation.lastAnimationState?.name,frame:Math.floor((arm.animation.lastAnimationState?.currentTime||0)*30+.0001)}),this);}
    if(!this.stage||!this.visible||!arm.visible||__nativeBattle.samples.length>=6000)return;
    const state=arm.animation.lastAnimationState,slots=arm.armature.getSlots();
    const row={at:performance.now(),model:this._dbName,action:state?.name,frame:Math.floor((state?.currentTime||0)*30+.0001),raster:!!(this._streetBody||this._characterIdleState),nativeVisible:arm.visible,body:slots.filter(s=>!s.childArmature&&s.visible&&s.displayIndex>=0&&s.display?.visible).map(s=>s._textureData?.name).filter(Boolean),fx:slots.filter(s=>s.childArmature&&s.visible&&s.displayIndex>=0&&s.display?.visible).map(s=>s.childArmature.armatureData.name)};
    __nativeBattle.samples.push(row);
    if(row.action&&row.frame>=5&&!__nativeBattle.captures[row.action]){const stage=egret.MainContext.instance.stage,t=new egret.RenderTexture();t.drawToTexture(stage,new egret.Rectangle(0,0,stage.stageWidth,stage.stageHeight),1);__nativeBattle.captures[row.action]=t.toDataURL('image/png').split(',')[1];t.dispose();}
   };this.addEventListener(egret.Event.ENTER_FRAME,this.__nativeTrialTick,this);}return result;};
   DBPlayer.prototype.trigger=function(action){if(/^hero_skin_002_01(_ez)?$/.test(String(this._dbName)))__nativeBattle.triggers.push({action,at:performance.now(),model:this._dbName});return trigger.apply(this,arguments);};
  },10);
 });
 if(active15)await page.addInitScript(includeSlam=>{
  window.__active15Trace={samples:[],models:[],png:null,slamPNG:null};
  const timer=setInterval(()=>{
   if(!window.StreetBody?.snapshot().installed||!window.DBPlayer)return;clearInterval(timer);
   const init=DBPlayer.prototype.init;
   DBPlayer.prototype.init=function(){const result=init.apply(this,arguments);if((/^common_newskill_simayi_01_1(_ez)?$/.test(String(arguments[0]))||includeSlam&&/^common_newskill_simayi_01_2(_ez)?$/.test(String(arguments[0])))&&!this.__active15Tick){__active15Trace.models.push(String(arguments[0]));this.__active15Tick=()=>{
    const arm=this._armature;if(!this.stage||!this.visible||!arm?.visible||__active15Trace.samples.length>=2000)return;
    const textures=arm.armature.getSlots().filter(s=>s.displayIndex>=0&&s.visible&&s._textureData&&((arm._batchEnabled&&arm.$renderNode?.drawData?.includes(s._renderDisplay?.$renderNode)&&s._renderDisplay.$renderNode.alpha>0)||(!arm._batchEnabled&&s.display?.visible&&s.display.alpha>0))).map(s=>s._textureData.name);
    const row={model:this._dbName,frame:Math.floor((arm.animation.lastAnimationState?.currentTime||0)*24),textures};__active15Trace.samples.push(row);
    if(row.frame>=4&&textures.length>1&&!__active15Trace.png){const stage=egret.MainContext.instance.stage,t=new egret.RenderTexture();t.drawToTexture(stage,new egret.Rectangle(0,0,stage.stageWidth,stage.stageHeight),1);__active15Trace.png=t.toDataURL('image/png').split(',')[1];t.dispose();}
    if(/^common_newskill_simayi_01_2(_ez)?$/.test(this._dbName)&&row.frame>=4&&textures.length&&!__active15Trace.slamPNG){const stage=egret.MainContext.instance.stage,t=new egret.RenderTexture();t.drawToTexture(stage,new egret.Rectangle(0,0,stage.stageWidth,stage.stageHeight),1);__active15Trace.slamPNG=t.toDataURL('image/png').split(',')[1];t.dispose();}
   };this.addEventListener(egret.Event.ENTER_FRAME,this.__active15Tick,this);}return result;};
  },10);
 },active16);
 await page.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=demo');await page.waitForFunction(()=>window.OfflineLastBattlePayload);
 report.payload=await page.evaluate(()=>({engine:OfflineLastBattlePayload.offlineCombatEngine,allies:OfflineLastBattlePayload.teams[0].entities.map(e=>({code:e.code,dermaCode:e.dermaCode,anger:e.anger,skillIds:e.skillIds})),rounds:OfflineLastBattlePayload.battleInfo.rounds.length,attacks:OfflineLastBattlePayload.battleInfo.rounds.flatMap(r=>(r.seqAttack||[]).map(a=>({entityId:a.entityId,skillId:a.skillId})))}));
 assert.equal(report.payload.engine.mode,'original-battle-ai');assert.equal(report.payload.allies.find(e=>e.code===41010002)?.dermaCode,100201);
 await page.waitForFunction(()=>__nativeBattle.samples.some(r=>r.action==='gongji'&&r.frame>=18),null,{timeout:60000});
 if(endurance||skillScenario){await fs.writeFile(out+'/payload.json',JSON.stringify(report.payload,null,2));await page.waitForFunction(()=>__nativeBattle.samples.some(r=>r.action==='jineng'&&r.frame>=15),null,{timeout:45000});}
 else await page.waitForTimeout(12000);
 if(active15){
  await page.waitForFunction(()=>__active15Trace.samples.some(r=>r.frame>=8&&r.textures.length),null,{timeout:15000});await page.waitForTimeout(3000);
  if(active16)await page.waitForFunction(()=>__active15Trace.slamPNG,null,{timeout:15000});
  report.active15=await page.evaluate(()=>__active15Trace);assert(report.active15.png);await fs.writeFile(out+'/active15.png',Buffer.from(report.active15.png,'base64'));delete report.active15.png;
  if(active16){assert(report.active15.slamPNG);await fs.writeFile(out+'/active16.png',Buffer.from(report.active15.slamPNG,'base64'));}delete report.active15.slamPNG;
  report.active15.distinctTextures=[...new Set(report.active15.samples.flatMap(r=>r.textures))];assert(report.active15.distinctTextures.length>1);
  report.active15.parts=Object.fromEntries([...new Set(report.active15.samples.map(r=>r.model))].map(model=>{const rows=report.active15.samples.filter(r=>r.model===model);return [model,{samples:rows.length,distinctTextures:[...new Set(rows.flatMap(r=>r.textures))]}];}));
  report.sharedFXCandidateOverrides=true;report.productionConfiguration=false;
 }
 const trace=await page.evaluate(()=>({samples:__nativeBattle.samples,triggers:__nativeBattle.triggers,events:__nativeBattle.events,captures:__nativeBattle.captures}));
 for(const [action,png] of Object.entries(trace.captures))await fs.writeFile(out+'/'+action+'.png',Buffer.from(png,'base64'));delete trace.captures;Object.assign(report,trace);
 report.digests=await page.evaluate(async entries=>{const rows=[];for(const e of entries){const info=RES.getResourceInfo(e.targetKey),response=await fetch(new URL((info.root||'')+info.url,location.href)),bytes=await response.arrayBuffer();rows.push({key:e.originalKey,sha256:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(n=>n.toString(16).padStart(2,'0')).join('')});}return rows;},entries);
 for(const e of entries)assert.equal(report.digests.find(r=>r.key===e.originalKey).sha256,e.targetSha256);
 if(banner){report.bannerResourceDigests=await page.evaluate(async resources=>{const rows=[];for(const r of resources){const texture=RES.getRes(r.originalKey),target=RES.getRes(r.targetKey),info=RES.getResourceInfo(r.targetKey),bytes=await(await fetch(new URL((info.root||'')+info.url,location.href))).arrayBuffer();rows.push({key:r.originalKey,aliasMatches:!!texture&&texture===target,size:texture?[texture.textureWidth,texture.textureHeight]:null,sha256:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(n=>n.toString(16).padStart(2,'0')).join('')});}return rows;},bannerCandidate.resources);for(const r of bannerCandidate.resources){const row=report.bannerResourceDigests.find(x=>x.key===r.originalKey);assert(row.aliasMatches);assert.deepEqual(row.size,r.size);assert.equal(row.sha256,r.targetSha256);}}
 assert(report.samples.length>20);assert(report.samples.every(r=>!r.raster&&r.nativeVisible&&r.body.length>0));assert(report.events.some(e=>e.name==='zd'&&Math.abs(e.frame-18)<=1));assert(report.samples.some(r=>r.fx.length>0));assert.equal(oldRaster.length,0);assert.equal(errors.length,0);assert.equal(failures.length,0);
 report.errors=errors;report.failures=failures;report.oldRaster=oldRaster;report.actions=[...new Set(report.samples.map(r=>r.action))];report.pass=true;
}catch(e){report.error=e.stack;if(activePage)report.diagnostic=await activePage.evaluate(()=>({samples:window.__nativeBattle?.samples||[],triggers:window.__nativeBattle?.triggers||[],events:window.__nativeBattle?.events||[]})).catch(error=>({error:String(error)}));throw e;}finally{
 await browser.close();await fs.writeFile(savePath,before);report.isolatedSaveRestored=(await fs.readFile(savePath)).equals(before);report.mainSaveUnchanged=sha(await fs.readFile(mainPath))===mainBefore;await fs.writeFile(out+'/runtime.json',JSON.stringify(report,null,2));assert(report.isolatedSaveRestored&&report.mainSaveUnchanged);
}
console.log(JSON.stringify({pass:report.pass,actions:report.actions,samples:report.samples?.length,mainSaveUnchanged:report.mainSaveUnchanged}));
