import fs from 'node:fs/promises';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const label=process.argv.find(v=>v.startsWith('--label='))?.slice(8)||'probe',out='outputs/street-reskin/skin-idle-routing';await fs.mkdir(out,{recursive:true});
const raw=await fs.readFile('local_game/character-idle-data.js','utf8'),data=JSON.parse(raw.slice(raw.indexOf('=')+1).trim().replace(/;$/,''));
// One static test texture probes model routing only. This is never saved into game data,
// never approved as animation and never included in completed-skin counts.
data.skins={'100201':{...structuredClone(data.heroes['2']),id:100201,skinCode:100201,heroId:2,name:'TEST ONLY',models:['hero_skin_002_01','hero_skin_002_01_ez'],materialId:'test-routing-only',frameCount:1,width:111,height:111,crop:[0,0,111,111],bodyHeight:111,fps:1,atlas:null,baseUrl:'assets/street/skins/100201/revision-1f3efd1c1a2b6b40/',files:['head1_hero_002_04_png.png']}};
const b=await chromium.launch({channel:'chrome',headless:true});try{
 const p=await b.newPage(),errors=[],network=[];p.on('pageerror',e=>errors.push({message:e.message,stack:e.stack}));p.on('requestfailed',r=>network.push({url:r.url(),failure:r.failure()}));p.on('response',r=>{if(r.status()>=400)network.push({url:r.url(),status:r.status()});});await p.route('**/character-idle-data.js*',route=>route.fulfill({status:200,contentType:'application/javascript',body:'window.CharacterIdleData='+JSON.stringify(data)+';'}));
 await p.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await p.waitForFunction(()=>CharacterIdle.snapshot().installed&&game.GameMVC.heroPy.heroBag.getItems().length>0);
 await p.evaluate(()=>{window.__skinResourceFailures=[];RES.addEventListener(RES.ResourceEvent.ITEM_LOAD_ERROR,e=>__skinResourceFailures.push({name:e.resItem?.name,url:e.resItem?.url}),null);window.__skinPromiseFailures=[];for(const key of ['getResAsync','getResByUrl']){const original=RES[key];RES[key]=function(...args){const caller=new Error().stack,r=original.apply(this,args);return r&&typeof r.then==='function'?r.then(v=>v,e=>{__skinPromiseFailures.push({method:key,key:args[0],reason:String(e),caller});throw e;}):r;};}});
 const result=await p.evaluate(async options=>{
  const hero=game.GameMVC.heroPy.heroBag.getItems().find(h=>h.config.subType===2);let view;
  if(options.modelOnly){const host=new eui.Group();host.width=720;host.height=1280;egret.MainContext.instance.stage.addChild(host);view=new customui.HeroDynamicModel();view.width=420;view.height=300;view.x=360;view.y=650;host.addChild(view);}
  else {const params={info:hero.config,uuid:hero.uuid,dermaCode:100201,isCanPutOn:false,isCanPutDown:false,isCanActivate:false,isShowAllBtn:false};let panel;
   if(options.normalPanel){const original=game.HeroDermaPanel.prototype.updateView;game.HeroDermaPanel.prototype.updateView=function(...args){panel=this;return original.apply(this,args);};try{game.AppFacade.getInstance().showSubView(game.HeroMediator.N,game.HeroMediator.SV.HERO_DERMA,params);const start=Date.now();while(!panel&&Date.now()-start<10000)await new Promise(r=>setTimeout(r,50));if(!panel)throw Error('Normal panel did not open');}finally{game.HeroDermaPanel.prototype.updateView=original;}}
   else {panel=new game.HeroDermaPanel();egret.MainContext.instance.stage.addChild(panel);panel.validateNow();panel.updateView(params);panel.validateNow();}view=panel.hero_model0;}
  const rows=[];
  for(const model of ['hero_skin_002_01','hero_skin_002_01_ez','hero_002_01','hero_skin_002_01']){
   view.update({code:hero.code,model});await new Promise(r=>setTimeout(r,600));const native=view.getModel(),stand=view._characterIdleStandIn,state=stand?._characterIdleState||native?._characterIdleState;
   rows.push({requested:model,actualModel:native?._dbName,id:state?.cfg.id,material:state?.cfg.materialId,visible:state?.bitmap.visible,textureReady:!!state?.bitmap.texture,cacheKey:state?.cache.key});
  }return {rows,baseHeroCount:Object.keys(CharacterIdleData.heroes).length,resourceFailures:__skinResourceFailures,promiseFailures:__skinPromiseFailures};
 },{modelOnly:process.argv.includes('--model-only'),normalPanel:process.argv.includes('--normal-panel')});const pass=result.rows.every(r=>r.id===(r.requested.startsWith('hero_skin_')?100201:2)&&r.visible&&r.textureReady)&&errors.length===0;
 await fs.writeFile(out+'/'+label+'.json',JSON.stringify({pass,...result,errors,network,scope:'Browser-only single-frame test fixture validates independent skin routing, not animation or complete skin'},null,2));console.log(JSON.stringify({pass,rows:result.rows,errors:errors.length,network,promiseFailures:result.promiseFailures.map(r=>({method:r.method,key:r.key,reason:r.reason})),resourceFailures:result.resourceFailures}));
 if(!pass)process.exitCode=1;
}finally{await b.close();}
