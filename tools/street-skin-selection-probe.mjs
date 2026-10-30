import fs from 'node:fs/promises';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out='outputs/street-reskin/skin-selection-probe';await fs.mkdir(out,{recursive:true});const b=await chromium.launch({channel:'chrome',headless:true});
try{
 const p=await b.newPage({viewport:{width:480,height:900}}),errors=[];p.on('pageerror',e=>errors.push({message:e.message,stack:e.stack}));await p.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await p.waitForFunction(()=>window.CharacterArt?.audit.installed&&game.GameMVC.heroPy.heroBag.getItems().length>0);
 const result=await p.evaluate(async()=>{
  const hero=game.GameMVC.heroPy.heroBag.getItems().find(h=>h.config.subType===2),panel=new game.HeroDermaPanel();egret.MainContext.instance.stage.addChild(panel);panel.validateNow();
  panel.updateView({info:hero.config,uuid:hero.uuid,dermaCode:100201,isCanPutOn:false,isCanPutDown:false,isCanActivate:false,isShowAllBtn:false});panel.validateNow();await new Promise(r=>setTimeout(r,400));
  const list=panel.dataprovider.source.map(r=>({code:r.code,index:r.index,isLast:r.isLast,choose:r.choose}));
  const before={previewCode:panel.dermaConfig?.code,selectedIndex:panel.curSelectIndex},target=panel.dataprovider.source.find(r=>r.code===100202);if(!target)throw Error('Target skin missing from native panel list');
  // Same production callback order as native HeroDermaItem touch handler; no equip RPC.
  target.updateShowCb();target.updateChooseCb(target.index);await new Promise(r=>setTimeout(r,400));
  const after={previewCode:panel.dermaConfig?.code,selectedIndex:panel.curSelectIndex,selectedCode:panel.dataprovider.source[panel.curSelectIndex]?.code,selectedRows:panel.dataprovider.source.filter(r=>r.choose).map(r=>r.code),name:panel.lb_name0.text};
  return {target:100202,before,after,list,previewMatches:after.previewCode===100202,selectionMatches:after.selectedCode===100202,scope:'Native panel and production selection callbacks; no equip, activation or save writes requested'};
 });const pass=result.previewMatches&&result.selectionMatches&&errors.length===0;await p.screenshot({path:out+'/after-selection.png'});await fs.writeFile(out+'/result.json',JSON.stringify({pass,...result,errors},null,2));console.log(JSON.stringify({pass,...result,errorCount:errors.length}));if(!pass)process.exitCode=1;
}finally{await b.close();}
