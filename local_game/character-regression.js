(function(){
    'use strict';
    if(!new URLSearchParams(location.search).has('heroaudit'))return;
    var timer=setInterval(function(){
        if(!window.CharacterIdle||!CharacterIdle.snapshot().installed||!window.OfflineReplica)return;
        clearInterval(timer);start();
    },200);
    function start(){
        var bar=document.createElement('div');bar.id='hero-regression';bar.style.cssText='position:fixed;top:0;left:0;right:0;z-index:999999;background:#172232ee;color:white;padding:6px;font:12px sans-serif';
        bar.innerHTML='<select aria-label="核对角色"></select><button data-open>打开详情</button><button data-all>逐项检查85个详情</button><button data-bag>背包检查结果</button><pre id="hero-regression-results" style="max-height:65px;overflow:auto"></pre>';document.body.appendChild(bar);
        var ids=Object.keys(CharacterIdleData.heroes).map(Number).sort(function(a,b){return a-b;}),select=bar.querySelector('select'),output=bar.querySelector('pre'),running=false;
        ids.forEach(function(id){var option=document.createElement('option');option.value=id;option.textContent=id+' '+CharacterIdleData.heroes[id].name;select.appendChild(option);});
        function open(id){var hero=game.GameMVC.heroPy.heroBag.getItems().find(function(h){return Number(h.config.subType)===id;});if(!hero)throw Error('Not owned '+id);game.AppFacade.getInstance().showSubView(game.HeroMediator.N,game.HeroMediator.SV.NEW_HERO_MAIN_INFO,{uuid:hero.uuid});}
        bar.querySelector('[data-open]').onclick=function(){open(Number(select.value));};
        bar.querySelector('[data-bag]').onclick=function(){output.textContent=JSON.stringify({kind:'bag',items:window.CharacterReskinAudit.bagItems||{}});};
        bar.querySelector('[data-all]').onclick=function(){
            if(running)return;running=true;var results=[],index=0,firstFrame=null,firstTime=0,opened=0,restoreHero=null;
            var baseOnly=new URLSearchParams(location.search).has('baseaudit');
            function next(){
                if(restoreHero){restoreHero.hero.dermaCode=restoreHero.code;restoreHero=null;}
                if(index===ids.length){running=false;return;}
                select.value=ids[index];firstFrame=null;firstTime=0;opened=Date.now();
                try{
                    if(baseOnly){var h=game.GameMVC.heroPy.heroBag.getItems().find(function(hero){return Number(hero.config.subType)===ids[index];});restoreHero={hero:h,code:h.dermaCode};h.dermaCode=0;}
                    open(ids[index]);
                }catch(e){results.push({id:ids[index],pass:false,error:String(e),stack:e.stack});index++;next();}
            }
            next();var poll=setInterval(function(){
                if(!running){clearInterval(poll);return;}
                var id=ids[index],view=CharacterReskin.activeView(),cfg=view&&view.info&&view.info.config,match=cfg&&Number(cfg.subType)===id,stand=view&&view.hero_model&&view.hero_model._characterIdleStandIn,state=stand&&stand._characterIdleState;
                var skinCode=match&&Number(view.info.dermaCode)||0;
                var skin=skinCode&&config.HeroDermaLO.Get(skinCode),ownIdle=skinCode&&CharacterIdleData.skins&&CharacterIdleData.skins[skinCode];
                if(match&&skin&&!ownIdle&&!baseOnly){
                    var native=view.hero_model.getModel(),model=native&&String(native._dbName).replace(/_ez$/,''),ready=native&&native.isReady&&native._armature&&native._armature.visible&&!native._characterIdleSuppressNative&&!stand&&model===skin.model;
                    if(ready){if(!firstTime)firstTime=Date.now();else if(Date.now()-firstTime>=600){
                        var nativeInfo=view.curComponents&&view.curComponents[0],nativeSlots=nativeInfo&&nativeInfo.gp_skills?nativeInfo.gp_skills.$children.filter(function(item){return item.visible;}).length:0;
                        var expectedSlots=[cfg.actSkill,cfg.posSkill1,cfg.posSkill2,cfg.posSkill3].filter(Boolean).length;
                        results.push({id:id,name:CharacterIdleData.heroes[id].name,pass:nativeSlots===expectedSlots,presentation:'original-unreplaced-skin',skinCode:skinCode,nativeModel:model,visibleSkills:nativeSlots,expectedSkills:expectedSlots,completeSkin:false});index++;next();
                    }}else if(Date.now()-opened>8000){results.push({id:id,pass:false,error:'configured native skin did not load',skinCode:skinCode,model:model});index++;next();}
                    output.textContent=JSON.stringify({scope:'current equipped details; native unreplaced skins are explicitly incomplete',checked:results.length,total:ids.length,passed:results.filter(function(r){return r.pass;}).length,results:results});return;
                }
                if(match&&state&&state.frame>=0&&state.bitmap.visible){if(firstFrame===null){firstFrame=state.frame;firstTime=Date.now();}else if(Date.now()-firstTime>=600&&(state.frame!==firstFrame||Date.now()-opened>8000)){
                    var info=view.curComponents&&view.curComponents[0],slots=info&&info.gp_skills?info.gp_skills.$children.filter(function(item){return item.visible;}).length:0;
                    var expectedIdleId=ownIdle?skinCode:id;
                    results.push({id:id,name:CharacterIdleData.heroes[id].name,pass:state.cfg.id===expectedIdleId&&state.frame!==firstFrame&&slots===[cfg.actSkill,cfg.posSkill1,cfg.posSkill2,cfg.posSkill3].filter(Boolean).length,presentation:ownIdle?'independent-skin-idle':'new-base-idle',skinCode:skinCode,idleId:state.cfg.id,expectedIdleId:expectedIdleId,first:firstFrame,last:state.frame,visibleSkills:slots,expectedSkills:[cfg.actSkill,cfg.posSkill1,cfg.posSkill2,cfg.posSkill3].filter(Boolean).length});index++;next();
                }}else if(Date.now()-opened>8000){results.push({id:id,pass:false,error:'detail did not load',match:!!match,frame:state&&state.frame});index++;next();}
                output.textContent=JSON.stringify({scope:baseOnly?'85 base heroes with browser-only dermaCode cleared and restored per detail; no equip transaction':'current equipped details',checked:results.length,total:ids.length,passed:results.filter(function(r){return r.pass;}).length,results:results});
            },100);
        };
    }
})();
