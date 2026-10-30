(function (global) {
    'use strict';
    var data=global.CharacterIdleData, caches={}, modelIds={}, skinModelIds={}, installed=false, queue=[], loading=0;
    var atlasData=global.CharacterIdleAtlasData;
    var audit={version:data&&data.version,excluded:[13],framesPresented:0,errors:[],players:[],attachedHeroes:{},modelRequests:{}};
    function config(id){return data&&(data.heroes[String(id)]||(data.skins&&data.skins[String(id)]));}
    function skinForModel(name,owner){
        var key=String(name||'').replace(/_ez$/,''),id=skinModelIds[key],cfg=id&&config(id);
        if(!cfg||!cfg.skinCode)return 0;
        if(owner&&Number(cfg.heroId)!==Number(owner))return 0;
        var nativeOwner=/^hero_(\d+)_\d+$/.exec(key);
        // Shared numeric models need an explicit owning hero to disambiguate them.
        if(!owner&&nativeOwner&&Number(nativeOwner[1])!==Number(cfg.heroId))return 0;
        return id;
    }
    function releaseTexture(texture){if(texture){texture.disposeBitmapData=true;texture.dispose();}}
    function pump(){
        while(loading<6&&queue.length){
            var job=queue.shift();if(job.cache.dead){delete job.cache.pending[job.pendingKey||job.index];continue;}
            loading++;
            (function(job){
                var c=job.cache, cfg=c.cfg, url=encodeURI(c.atlas?c.atlas.pages[job.page].url:cfg.baseUrl+cfg.files[job.index]);
                fetch(url,{cache:'force-cache'}).then(function(r){if(!r.ok)throw Error(r.status+' '+url);return r.blob();})
                .then(function(blob){return createImageBitmap(blob);})
                .then(function(image){
                    if(c.dead){image.close();return;}
                    if(c.atlas){
                        var page=c.atlas.pages[job.page],atlasCanvas=document.createElement('canvas');atlasCanvas.width=page.width;atlasCanvas.height=page.height;
                        atlasCanvas.getContext('2d').drawImage(image,0,0);image.close();
                        var baseTexture=new egret.Texture();baseTexture.disposeBitmapData=true;baseTexture.bitmapData=new egret.BitmapData(atlasCanvas);
                        var sheet=new egret.SpriteSheet(baseTexture);c.sheets.push(sheet);c.loadedPages[job.page]=true;
                        c.atlas.frames.forEach(function(frame,index){if(frame.page===job.page)c.textures[index]=sheet.createTexture(String(index),frame.x,frame.y,frame.w,frame.h);});
                        return;
                    }
                    var box=cfg.crop, canvas=document.createElement('canvas'),resolution=Math.min(1,512/Math.max(box[2],box[3]));canvas.width=Math.max(1,Math.round(box[2]*resolution));canvas.height=Math.max(1,Math.round(box[3]*resolution));
                    var context=canvas.getContext('2d');context.drawImage(image,box[0],box[1],box[2],box[3],0,0,canvas.width,canvas.height);image.close();
                    var pixels=context.getImageData(0,0,canvas.width,canvas.height),rgba=pixels.data;
                    for(var pixel=0;pixel<rgba.length;pixel+=4)if(rgba[pixel+3]<=8)rgba[pixel]=rgba[pixel+1]=rgba[pixel+2]=rgba[pixel+3]=0;
                    context.putImageData(pixels,0,0);
                    var texture=new egret.Texture();texture.bitmapData=new egret.BitmapData(canvas);c.textures[job.index]=texture;
                }).catch(function(e){if(audit.errors.length<50)audit.errors.push({hero:cfg.id,frame:job.index,error:String(e)});})
                .then(function(){delete c.pending[job.pendingKey||job.index];loading--;pump();});
            })(job);
        }
    }
    function acquire(cfg,mode){
        var atlasHero=Object.prototype.hasOwnProperty.call(cfg,'atlas')?cfg.atlas:atlasData&&atlasData.heroes[String(cfg.id)],atlasProfile=mode==='detail'?'detail':'battle';
        var pack=atlasHero&&atlasHero.profiles[atlasProfile],key=cfg.id+(pack?':'+atlasProfile:'');
        var c=caches[key];if(!c){c={key:key,cfg:cfg,atlas:pack,sheets:[],loadedPages:{},users:0,textures:{},pending:{},dead:false};caches[key]=c;}c.users++;return c;
    }
    function request(c,index,urgent){
        if(c.dead||c.textures[index])return;
        var frame=c.atlas&&c.atlas.frames[index],pendingKey=frame?'atlas:'+frame.page:index;
        if(c.pending[pendingKey])return;c.pending[pendingKey]=true;
        var job={cache:c,index:index,pendingKey:pendingKey,page:frame&&frame.page};urgent?queue.unshift(job):queue.push(job);pump();
    }
    function trim(c,current){
        // A live loop keeps its frames. Dispose the whole cache on final release,
        // rather than deleting upcoming/displayed frames while asynchronous decode lags.
    }
    function release(c){if(--c.users>0)return;c.dead=true;if(c.atlas)c.sheets.forEach(function(sheet){sheet.dispose();});else Object.keys(c.textures).forEach(function(k){releaseTexture(c.textures[k]);});delete caches[c.key];}
    function restore(player,state){if(state.hidden&&player._armature){player._armature.visible=true;state.hidden=false;audit.actionRestores=(audit.actionRestores||0)+1;}if(state.bitmap)state.bitmap.visible=false;}
    function hideNative(player,state){if(player._armature)player._armature.visible=false;state.hidden=true;}
    function profile(view){
        for(var node=view;node;node=node.parent){
            if(global.game&&game.FormationModelComponent&&node instanceof game.FormationModelComponent)return 'formation';
            if(/MapEntity|FightEntity/.test(node.__class__||''))return 'battle';
        }
        return 'detail';
    }
    // Use the whole sequence's union bounds, never the changing skeleton bounds.
    // UI sprites live beside the auto-fitted model, outside its scale feedback loop.
    function place(player,state,texture){
        var bitmap=state.bitmap,cfg=state.cfg,layout=player._characterIdleLayout,box=cfg.crop;
        var parent=layout&&layout.view.parent,ui=!!parent;
        var target=ui?parent:player;
        if(bitmap.parent!==target){
            if(bitmap.parent)bitmap.parent.removeChild(bitmap);
            if(ui&&parent.addChildAt)parent.addChildAt(bitmap,parent.getChildIndex(layout.view)+1);else target.addChild(bitmap);
        }
        var mode=ui?profile(layout.view):'battle',width=mode==='formation'?120:mode==='detail'?420:145,height=mode==='formation'?145:mode==='detail'?270:135,bodyHeight=mode==='formation'?125:mode==='detail'?250:110;
        var coordinateSpace=ui?parent:player;
        if(mode!=='formation'&&coordinateSpace.localToGlobal){var origin=coordinateSpace.localToGlobal(0,0),unitX=coordinateSpace.localToGlobal(1,0),unitY=coordinateSpace.localToGlobal(0,1),sx=Math.max(.01,Math.hypot(unitX.x-origin.x,unitX.y-origin.y)),sy=Math.max(.01,Math.hypot(unitY.x-origin.x,unitY.y-origin.y));width/=sx;height/=sy;bodyHeight/=sy;}
        var scale=Math.min(width/Math.max(1,box[2]),height/Math.max(1,box[3]),bodyHeight/Math.max(1,cfg.bodyHeight));
        bitmap.scaleX=scale*box[2]/((texture&&texture.textureWidth)||box[2]);bitmap.scaleY=scale*box[3]/((texture&&texture.textureHeight)||box[3]);
        var x=ui?(layout.view.horizontalCenter!=null&&isFinite(Number(layout.view.horizontalCenter))?parent.width/2+Number(layout.view.horizontalCenter):layout.view.x):0;
        var y=mode==='formation'?parent.height-23:ui?layout.view.y:0;
        bitmap.x=x-box[2]*scale/2;bitmap.y=y-box[3]*scale;
        state.fit={mode:mode,width:width,height:height,scale:scale,x:bitmap.x,y:bitmap.y,drawWidth:box[2]*scale,drawHeight:box[3]*scale,bodyHeight:cfg.bodyHeight*scale,ui:ui};
        if(!state.fitRange)state.fitRange={min:scale,max:scale,samples:0};state.fitRange.min=Math.min(state.fitRange.min,scale);state.fitRange.max=Math.max(state.fitRange.max,scale);state.fitRange.samples++;
        if(ui){for(var node=layout.view;node&&node!==parent;node=node.parent)if(!node.visible)return false;}
        return true;
    }
    function detach(player){
        var s=player._characterIdleState;if(!s)return;restore(player,s);
        player.removeEventListener(egret.Event.ENTER_FRAME,s.tick,player);
        player.removeEventListener(egret.Event.REMOVED_FROM_STAGE,s.removed,player);
        if(s.bitmap.parent)s.bitmap.parent.removeChild(s.bitmap);release(s.cache);player._characterIdleState=null;
        var i=audit.players.indexOf(player);if(i>=0)audit.players.splice(i,1);
    }
    function bind(player,id){
        var cfg=config(id);if(!cfg){audit.lastUnbound={name:player._dbName,id:id};detach(player);return;}
        var old=player._characterIdleState;if(old&&old.cfg.id===cfg.id)return;detach(player);
        var bitmap=new egret.Bitmap();bitmap.name='canonicalCharacterIdle';bitmap.touchEnabled=false;bitmap.visible=false;player.addChild(bitmap);
        var s={cfg:cfg,cache:acquire(cfg,player._characterIdleLayout?profile(player._characterIdleLayout.view):'battle'),bitmap:bitmap,start:egret.getTimer(),frame:-1,hidden:false,tick:null,removed:null};
        hideNative(player,s);request(s.cache,0,true);
        s.tick=function(){
            if(!player.stage)return;
            var action=player.action||player._action||player.lastAction||'daiji';
            if(action!=='daiji'){restore(player,s);s.start=egret.getTimer();return;}
            if(!s.started){if(!s.cache.textures[0])return;s.started=true;s.start=egret.getTimer();}
            var current=Math.floor((egret.getTimer()-s.start)*cfg.fps/1000)%cfg.frameCount;
            request(s.cache,current,true);for(var i=1;i<=6;i++)request(s.cache,(current+i)%cfg.frameCount,false);
            hideNative(player,s);
            var presented=s.cache.textures[current]?current:s.frame>=0?s.frame:0,texture=s.cache.textures[presented];if(!texture)return;
            var visible=place(player,s,texture);
            if(bitmap.texture!==texture){bitmap.texture=texture;s.frame=presented;audit.framesPresented++;}
            bitmap.visible=visible;
            hideNative(player,s);
            trim(s.cache,current);
        };
        s.removed=function(){detach(player);};player._characterIdleState=s;
        player.addEventListener(egret.Event.ENTER_FRAME,s.tick,player);player.addEventListener(egret.Event.REMOVED_FROM_STAGE,s.removed,player);
        audit.players.push(player);audit.attachedHeroes[cfg.id]=cfg.materialId;
    }
    function heroForView(view){
        if(view._characterIdleHeroId)return Number(view._characterIdleHeroId);
        var d=view.data||{},code=Number(d.code||(d.info&&d.info.code)||(d.playerInfo&&d.playerInfo.firstCode));
        var row=code&&global.config&&global.config.HeroLO.Get(code);return row?Number(row.subType):0;
    }
    function bindView(view,id){
        if(!view)return;view._characterIdleHeroId=Number(id);
        view._characterIdleLayout={view:view,width:420,height:300};
        if(view.IdleActions)view.IdleActions=[];
        if(view._characterIdleViewTick){view._characterIdleViewTick();return;}
        var tick=function(){
            var nativePlayer=view.getModel&&view.getModel(),hero=heroForView(view),p=nativePlayer;
            hero=skinForModel(nativePlayer&&nativePlayer._dbName,hero)||hero;
            if(config(hero)&&profile(view)!=='battle'){
                if(nativePlayer){detach(nativePlayer);nativePlayer._characterIdleSuppressNative=true;if(nativePlayer._armature)nativePlayer._armature.visible=false;}
                p=view._characterIdleStandIn;
                if(!p){p=new egret.DisplayObjectContainer();p.name='canonicalIdleRenderer';p.action='daiji';view._characterIdleStandIn=p;view.addChild(p);}
            }else if(view._characterIdleStandIn){
                detach(view._characterIdleStandIn);if(view._characterIdleStandIn.parent)view._characterIdleStandIn.parent.removeChild(view._characterIdleStandIn);view._characterIdleStandIn=null;
                if(nativePlayer){nativePlayer._characterIdleSuppressNative=false;if(nativePlayer._armature)nativePlayer._armature.visible=true;}
            }
            if(!p)return;
            p._characterIdleHeroId=hero;
            p._characterIdleLayout=view._characterIdleLayout;
            bind(p,hero);
        };
        view._characterIdleViewTick=tick;view.addEventListener(egret.Event.ENTER_FRAME,tick,view);tick();
    }
    function install(){
        if(installed||!data||!global.DBPlayer||!global.game||!game.Config.pack.t_hero)return;installed=true;
        Object.keys(game.Config.pack.t_hero).forEach(function(code){
            var row=game.Config.pack.t_hero[code],cfg=config(row.subType),id=Number(row.subType);
            if(cfg)row.name=cfg.name;var key=String(row.model||'').replace(/_ez$/,'');
            if(key)modelIds[key]=modelIds[key]===undefined?id:(modelIds[key]===id?id:0);
        });
        Object.keys(data.skins||{}).forEach(function(id){
            var cfg=data.skins[id];
            if(!cfg||!cfg.skinCode||!config(cfg.heroId))return;
            (cfg.models||[]).forEach(function(name){var key=String(name).replace(/_ez$/,'');skinModelIds[key]=skinModelIds[key]===undefined?Number(id):(skinModelIds[key]===Number(id)?Number(id):0);});
        });
        var proto=DBPlayer.prototype,init=proto.init,destroy=proto.destroy,trigger=proto.trigger,ready=proto.readyToPlay;
        proto.init=function(name){audit.modelRequests[name]=(audit.modelRequests[name]||0)+1;var r=init.apply(this,arguments),key=String(name).replace(/_ez$/,''),id=modelIds[key],variant=/^hero_(\d+)_\d+$/.exec(key);if(variant&&(config(Number(variant[1]))||Number(variant[1])===13))id=Number(variant[1]);id=skinForModel(key)||id;if(this._characterIdleSuppressNative){if(this._armature)this._armature.visible=false;}else bind(this,id);return r;};
        proto.destroy=function(){detach(this);this._characterIdleHeroId=0;this._characterIdleLayout=null;this._characterIdleSuppressNative=false;return destroy.apply(this,arguments);};
        if(trigger)proto.trigger=function(action){var result=trigger.apply(this,arguments),s=this._characterIdleState;if(this._characterIdleSuppressNative&&this._armature)this._armature.visible=false;else if(s){if((action||this.action)==='daiji')hideNative(this,s);else restore(this,s);}return result;};
        if(ready)proto.readyToPlay=function(){var result=ready.apply(this,arguments),s=this._characterIdleState;if(this._characterIdleSuppressNative&&this._armature)this._armature.visible=false;else if(s&&(!this.action||this.action==='daiji'))hideNative(this,s);return result;};
        if(global.customui&&customui.HeroDynamicModel){
            var dynamic=customui.HeroDynamicModel.prototype,update=dynamic.update,reset=dynamic.reset;
            dynamic.update=function(){this._characterIdleHeroId=0;var r=update.apply(this,arguments),id=heroForView(this);var p=this.getModel&&this.getModel();if(id)bindView(this,id);return r;};
            dynamic.reset=function(){this._characterIdleHeroId=0;this._characterIdleLayout=null;if(this._characterIdleViewTick){this.removeEventListener(egret.Event.ENTER_FRAME,this._characterIdleViewTick,this);this._characterIdleViewTick=null;}var standIn=this._characterIdleStandIn;if(standIn){detach(standIn);if(standIn.parent)standIn.parent.removeChild(standIn);this._characterIdleStandIn=null;}var p=this.getModel&&this.getModel();if(p){detach(p);p._characterIdleHeroId=0;p._characterIdleLayout=null;p._characterIdleSuppressNative=false;}return reset.apply(this,arguments);};
        }
        audit.installed=true;audit.mappedHeroes=Object.keys(data.heroes).length;console.log('[CHARACTER-IDLE]',audit.mappedHeroes,'full sequences; original ID13 excluded');
        if(new URLSearchParams(location.search).has('heroaudit')){
            var report=document.createElement('pre');report.id='hero-config-audit';report.style.display='none';
            report.textContent=JSON.stringify({skillRepair:global.CharacterSkillRepairAudit,passiveCandidates:[14,31,32,33,48,49,50,51,52,65,66,67,68,69].map(function(id){return {id:id,skills:[3,4,5].map(function(slot){var key=550000000+id*10000+slot*100+10;return {key:key,skill:game.Config.pack.t_skill_base[key]||null};})};}),heroes:Object.keys(game.Config.pack.t_hero).map(function(key){var row=game.Config.pack.t_hero[key];return {code:row.code,id:row.subType,name:row.name,color:row.color,tier:row.tier,realStarLevel:row.realStarLevel,initStar:row.initStar,maxLevel:row.maxLevel,model:row.model,halfPic:row.halfPic,normalSkill:row.normalSkill,actSkill:row.actSkill,posSkill1:row.posSkill1,posSkill2:row.posSkill2,posSkill3:row.posSkill3,skillUnlock:row.skillUnlock};}),owned:game.GameMVC.heroPy.heroBag.getItems().map(function(hero){return {uuid:hero.uuid,code:hero.code,id:hero.config.subType,level:hero.level,starLevel:hero.starLevel,skillList:hero.skillList};})});document.body.appendChild(report);
        }
        if(new URLSearchParams(location.search).has('idlecheck')){
            var panel=document.createElement('pre');panel.id='idle-audit';panel.style.cssText='position:fixed;left:0;bottom:0;max-height:180px;overflow:auto;z-index:999999;background:#000c;color:#fff;font:11px monospace;pointer-events:none';document.body.appendChild(panel);
            setInterval(function(){panel.textContent=JSON.stringify(snapshot());},500);
        }
        if(new URLSearchParams(location.search).has('idlepreview'))setTimeout(openPreview,1500);
    }
    function openPreview(){
        var stage=egret.MainContext.instance.stage,layer=new egret.DisplayObjectContainer(),bg=new egret.Shape(),view=new customui.HeroDynamicModel();
        bg.graphics.beginFill(0x263344);bg.graphics.drawRect(0,0,stage.stageWidth,stage.stageHeight);bg.graphics.endFill();layer.addChild(bg);layer.addChild(view);stage.addChild(layer);
        view.x=stage.stageWidth/2;view.y=stage.stageHeight*.76;
        var ui=document.createElement('div');ui.id='idle-preview';ui.style.cssText='position:fixed;inset:0 0 auto;z-index:999999;padding:12px;background:#172232ee;color:white;font:14px sans-serif';
        ui.innerHTML='<strong>游戏待机动作预览 · 完整原序列 · 24 fps</strong><div style="margin-top:10px;display:flex;gap:8px"><select aria-label="角色" style="flex:1;min-width:0;padding:8px"></select><button>逐项验证</button><a href="?mode=heroes" style="color:#fff">返回游戏</a></div><p id="idle-preview-status"></p><pre id="idle-preview-result" style="max-height:70px;overflow:auto;font-size:11px"></pre>';
        document.body.appendChild(ui);var select=ui.querySelector('select'),status=ui.querySelector('p'),result=ui.querySelector('pre'),testTimer=null,results=[],ids=Object.keys(data.heroes).map(Number);ids.push(13);ids.sort(function(a,b){return a-b;});
        ids.forEach(function(id){var cfg=config(id),option=document.createElement('option');option.value=id;option.textContent=cfg?id+' '+cfg.originalName+' → '+cfg.name:'13 于禁（保留原待机）';select.appendChild(option);});
        function show(id){var rows=game.Config.heroConfigBySubType(id),row=rows&&rows[0];if(!row){status.textContent='配置缺失 '+id;return;}view.update({code:row.code,useHD:true,isStatic:true});bindView(view,id);var cfg=config(id);status.textContent=cfg?cfg.materialId+' · '+cfg.frameCount+' 帧 · '+cfg.width+'×'+cfg.height:'于禁：原版骨骼待机';}
        select.onchange=function(){if(testTimer){clearInterval(testTimer);testTimer=null;}show(Number(select.value));};show(Number(select.value));
        ui.querySelector('button').onclick=function(){
            if(testTimer)return;results=[];var index=0,previous=-1,sampled=false;select.value=ids[0];show(ids[0]);
            testTimer=setInterval(function(){var id=ids[index],p=view._characterIdleStandIn||view.getModel(),s=p&&p._characterIdleState,cfg=config(id);if(!sampled){previous=s?s.frame:-1;sampled=true;return;}
                results.push({id:id,material:cfg&&cfg.materialId,pass:id===13?!s:!!(s&&s.cfg.id===id&&s.bitmap.visible&&s.frame!==previous&&s.fit&&s.fit.drawWidth<=s.fit.width+.001&&s.fit.drawHeight<=s.fit.height+.001&&s.fitRange.max===s.fitRange.min),frame:s&&s.frame,fit:s&&s.fit,fitRange:s&&s.fitRange});result.textContent=JSON.stringify({checked:results.length,total:ids.length,passed:results.filter(function(r){return r.pass;}).length,results:results});
                previous=-1;sampled=false;index++;if(index===ids.length){clearInterval(testTimer);testTimer=null;status.textContent='验证完成：'+results.filter(function(r){return r.pass;}).length+'/'+ids.length;return;}select.value=ids[index];show(ids[index]);
            },650);
        };
    }
    function snapshot(){return {cacheCount:Object.keys(caches).length,queued:queue.length,loading:loading,atlasVersion:atlasData&&atlasData.version,roster:global.CharacterRosterAudit,nativeOwned:global.game&&game.GameMVC&&game.GameMVC.heroPy&&game.GameMVC.heroPy.heroBag?game.GameMVC.heroPy.heroBag.getItems().length:0,installed:installed,mappedHeroes:audit.mappedHeroes,framesPresented:audit.framesPresented,modelRequests:audit.modelRequests,actionRestores:audit.actionRestores||0,lastUnbound:audit.lastUnbound,attachedHeroes:audit.attachedHeroes,modelKeys:Object.keys(modelIds).slice(0,4).map(function(k){return [k,modelIds[k]];}),errors:audit.errors.slice(),active:audit.players.map(function(p){var s=p._characterIdleState;return {hero:s.cfg.id,material:s.cfg.materialId,frame:s.frame,frames:s.cfg.frameCount,fps:s.cfg.fps,nativeVisible:!!(p._armature&&p._armature.visible),action:p.action||p._action,visible:s.bitmap.visible,onStage:!!p.stage,fit:s.fit,fitRange:s.fitRange,cache:{dead:s.cache.dead,users:s.cache.users,loaded:Object.keys(s.cache.textures).length,pending:Object.keys(s.cache.pending).length,atlas:!!s.cache.atlas,pages:Object.keys(s.cache.loadedPages).length,decodedBytes:s.cache.atlas?Object.keys(s.cache.loadedPages).reduce(function(total,key){var page=s.cache.atlas.pages[key];return total+page.width*page.height*4;},0):Object.keys(s.cache.textures).reduce(function(total,key){var t=s.cache.textures[key];return total+t.textureWidth*t.textureHeight*4;},0)},bitmapStage:!!s.bitmap.stage,textureSize:s.bitmap.texture?[s.bitmap.texture.textureWidth,s.bitmap.texture.textureHeight]:null,renderBounds:s.bitmap.getTransformedBounds?s.bitmap.getTransformedBounds(egret.MainContext.instance.stage):null,ancestors:(function(){var a=[];for(var node=s.bitmap;node&&a.length<8;node=node.parent)a.push({type:node.__class__,visible:node.visible,alpha:node.alpha,cache:node.cacheAsBitmap,scroll:node.scrollRect,scale:node.scaleX});return a;})()};})};}
    global.CharacterIdle={install:install,has:function(id){return !!config(id);},bindView:bindView,snapshot:snapshot,data:data};
})(window);
