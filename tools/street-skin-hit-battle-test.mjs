import fs from 'node:fs/promises';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(x=>x.startsWith('--version='))?.slice(10)||'0.88.0',label=process.argv.find(x=>x.startsWith('--label='))?.slice(8)||'after',out='art-migration/versions/'+version;
const savePath='outputs/street-reskin/stress/8794-save.json',mainPath='pc_server_data/offline-replica-save.json',original=await fs.readFile(savePath),mainSha=crypto.createHash('sha256').update(await fs.readFile(mainPath)).digest('hex');
const save=JSON.parse(original),hero=save.heroes.find(h=>h.code===41010002);assert(hero);hero.dermaCode=0;hero.attr=JSON.stringify({'1':1,'2':1000000000,'3':1,'4':1});hero.skillList=[{code:550020110,level:1}];
const focused=process.argv.includes('--focused');
save.formation=[{uuid:hero.uuid,pos:1}];save.progress.stage=10;save.progress.battles=0;save.progress.wins=0;save.battleConfig={scenario:'wei',difficulty:'hell',enemyCount:focused?1:8,enemySubTypes:focused?[3]:[1,3,5,7,9,11,15,17],enemyRaces:[1,2,3,4,5,6]};save.battleEntities=[];delete save.pendingBattle;
const browser=await chromium.launch({channel:'chrome',headless:true});let page;let report={pass:false,scope:'Actual production equip proxy/persisted isolated save, native BattleAI replay and autonomous skin hit animation; no manually triggered DBPlayer hurt or edited battle payload. Main save must stay unchanged.'};
await fs.mkdir(out,{recursive:true});
try{
 await fs.writeFile(savePath,JSON.stringify(save,null,2));page=await browser.newPage({viewport:{width:600,height:1000}});const errors=[],failures=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failures.push(r.url());});page.on('requestfailed',r=>failures.push(r.url()));
 await page.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=heroes');await page.waitForFunction(()=>window.game?.GameMVC?.heroThingPy?.AllDermaInfo&&game.GameMVC.heroPy?.heroBag?.getItems().some(h=>h.config.subType===2));
 const equip=await page.evaluate(()=>{
  const hero=game.GameMVC.heroPy.heroBag.getItems().find(h=>h.config.subType===2),py=game.GameMVC.heroThingPy,cfg=config.HeroDermaLO.Get(100201);let calls=0,results=0;
  py._offlineSelectedDermaCode=100201;py.HeroDermaPutOn('offline-derma-100201',hero.uuid,()=>calls++,()=>results++);
  return {uuid:hero.uuid,dermaCode:hero.dermaCode,subType:hero.config.subType,skinSubType:cfg.subType,model:cfg.model,calls,results};
 });
 assert.equal(equip.dermaCode,100201);assert.equal(equip.calls,1);assert.equal(equip.results,1);
 let persisted;for(let i=0;i<100;i++){persisted=JSON.parse(await fs.readFile(savePath,'utf8'));if(persisted.heroes.find(h=>h.uuid===hero.uuid)?.dermaCode===100201)break;await new Promise(r=>setTimeout(r,20));}
 assert.equal(persisted.heroes.find(h=>h.uuid===hero.uuid).dermaCode,100201);assert.equal(persisted.dermas.find(d=>d.code===100201).heroUuid,hero.uuid);report.equip=equip;
 await page.addInitScript(()=>{
  window.__skinHitBattle=[];window.__skinHitNativeTriggers=[];let installed=false;
  const timer=setInterval(()=>{
   if(!installed&&window.StreetBody?.snapshot().installed&&window.DBPlayer){
    installed=true;const init=DBPlayer.prototype.init,trigger=DBPlayer.prototype.trigger;
    DBPlayer.prototype.init=function(){const r=init.apply(this,arguments);if(!this.__skinHitTraceTick){this.__skinHitTraceTick=()=>{const s=this._streetBody;if(s?.cfg.skinCode===100201&&s.action==='shouji'&&s.bitmap.visible&&__skinHitBattle.length<3000)__skinHitBattle.push({at:performance.now(),model:this._dbName,action:s.action,frame:s.frame,nativeFrame:s.nativeFrame,nativeVisible:this._armature.visible,nativeFXOnly:!!(window.StreetNativeFX&&StreetNativeFX.onlyFX(this)),fxTextures:this._armature.armature.getSlots().filter(slot=>slot.visible&&slot.displayIndex>=0&&slot.display?.visible&&slot.display.alpha>0&&(slot._colorTransform?.alphaMultiplier??1)>0&&slot.childArmature).flatMap(slot=>slot.childArmature.getSlots().filter(child=>child.displayIndex>=0).map(child=>child._textureData?.name)),onStage:!!this.stage});};this.addEventListener(egret.Event.ENTER_FRAME,this.__skinHitTraceTick,this);}return r;};
    DBPlayer.prototype.trigger=function(action){if(String(this._dbName).startsWith('hero_skin_002_01')&&__skinHitNativeTriggers.length<1000)__skinHitNativeTriggers.push({at:performance.now(),model:this._dbName,action});return trigger.apply(this,arguments);};
   }
   if(window.StreetBody){for(const p of StreetBody.snapshot().active)if(p.model.startsWith('hero_skin_002_01')&&p.visible&&p.action==='shouji'&&__skinHitBattle.length<3000)__skinHitBattle.push({at:performance.now(),...p});}
  },10);window.__skinHitBattleTimer=timer;
 });
 await page.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=demo');await page.waitForFunction(()=>window.OfflineLastBattlePayload);
 const payload=await page.evaluate(()=>{
  const incoming=[];function walk(value){if(!value||typeof value!=='object')return;if(Number(value.entityId)===11100&&'value' in value)incoming.push({value:value.value,life:value.life,status:value.status,skillId:value.skillId});for(const child of Object.values(value))if(typeof child==='object')walk(child);}walk(OfflineLastBattlePayload.battleInfo.rounds);
  return {allies:OfflineLastBattlePayload.teams[0].entities.map(e=>({entityId:e.entityId,code:e.code,dermaCode:e.dermaCode,attr:e.attr,life:e.life})),enemies:OfflineLastBattlePayload.teams[1].entities.map(e=>({entityId:e.entityId,code:e.code,dermaCode:e.dermaCode,attr:e.attr,life:e.life})),engine:OfflineLastBattlePayload.offlineCombatEngine,rounds:OfflineLastBattlePayload.battleInfo.rounds.length,incoming};
 });report.payload=payload;
 assert.equal(payload.allies.find(e=>e.code===41010002)?.dermaCode,100201,'Equipped skin must survive actual battle entity construction');assert.equal(payload.engine.mode,'original-battle-ai');
 report.aiAttrAudit=await page.evaluate(()=>window.OfflineBattleAttrAudit||[]);
 const converted=report.aiAttrAudit.find(r=>r.entityId===11100);assert.equal(converted.changes['15'].display,43);assert.equal(converted.changes['15'].native,.43);assert.equal(JSON.parse(payload.allies[0].attr)['15'],43,'Display/persisted attrs are not the AI copy');
 if(!process.argv.includes('--payload-only')){
 assert(payload.incoming.some(r=>Number(r.value)<0),'Native BattleAI must author real damage to the equipped hero');
 await page.waitForFunction(()=>StreetBody.snapshot().active.some(r=>r.model.startsWith('hero_skin_002_01')&&r.action==='shouji'&&r.visible&&r.frame>=5),null,{timeout:60000});
 await page.screenshot({path:out+'/skin-hit-battle-'+label+'.png'});await page.waitForTimeout(1000);report.samples=await page.evaluate(()=>__skinHitBattle);report.nativeTriggers=await page.evaluate(()=>__skinHitNativeTriggers);report.body=await page.evaluate(()=>StreetBody.snapshot());report.visibleHurtFxTextures=[...new Set(report.samples.flatMap(r=>r.fxTextures||[]))];assert(report.visibleHurtFxTextures.length>0,'New child FX must actually be visible during real hurt playback');
 assert(report.samples.some(r=>r.model==='hero_skin_002_01_ez'||r.model==='hero_skin_002_01'));assert(report.samples.every(r=>r.nativeVisible===false||r.nativeFXOnly));assert(new Set(report.samples.map(r=>r.frame)).size>=4);
 assert(report.nativeTriggers.some(r=>r.action==='shouji'),'Actual native battle must call the hit action');
 assert.equal(report.body.errors.length,0);assert.equal(errors.length,0);assert.equal(failures.length,0);report={...report,pass:true,errors,failures};
 }else{report.diagnosticOnly=true;console.log(JSON.stringify({payload:report.payload}));}
}catch(e){report.error=e.stack;if(page)report.diagnostic=await page.evaluate(()=>({samples:window.__skinHitBattle||[],triggers:window.__skinHitNativeTriggers||[],body:window.StreetBody?.snapshot(),payloadKeys:window.OfflineLastBattlePayload&&Object.keys(OfflineLastBattlePayload)})).catch(err=>({observationError:String(err)}));throw e;}
finally{
 await browser.close();await fs.writeFile(savePath,original);report.isolatedSaveRestored=Buffer.compare(await fs.readFile(savePath),original)===0;report.mainSaveUnchanged=crypto.createHash('sha256').update(await fs.readFile(mainPath)).digest('hex')===mainSha;
 await fs.writeFile(out+'/skin-hit-battle-'+label+'.json',JSON.stringify(report,null,2));assert(report.isolatedSaveRestored&&report.mainSaveUnchanged);
 if(report.pass)console.log(JSON.stringify({pass:true,equipped:report.equip.dermaCode,battle:report.payload.allies.map(e=>({entityId:e.entityId,code:e.code,dermaCode:e.dermaCode})),hitSamples:report.samples.length,distinctFrames:new Set(report.samples.map(x=>x.frame)).size,mainSaveUnchanged:true}));
}
