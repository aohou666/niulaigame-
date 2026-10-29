(function(global){
    'use strict';
    var installed=false,byModel={},caches={},players=[],audit={installed:false,framesPresented:0,errors:[],models:{}};
    function acquire(cfg){
        var c=caches[cfg.id];if(c){c.users++;return c;}
        c={cfg:cfg,users:1,dead:false,textures:[],sheet:null,ready:false};caches[cfg.id]=c;
        fetch(cfg.atlas,{cache:'force-cache'}).then(function(r){if(!r.ok)throw Error(r.status+' '+cfg.atlas);return r.blob();})
        .then(function(blob){return createImageBitmap(blob);}).then(function(image){
            if(c.dead){image.close();return;}
            var canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;canvas.getContext('2d').drawImage(image,0,0);image.close();
            var texture=new egret.Texture();texture.disposeBitmapData=true;texture.bitmapData=new egret.BitmapData(canvas);c.sheet=new egret.SpriteSheet(texture);
            cfg.frames.forEach(function(f,index){c.textures[index]=c.sheet.createTexture(String(index),f.x,f.y,f.w,f.h);});c.ready=true;
        }).catch(function(e){audit.errors.push({effect:cfg.id,error:String(e)});});return c;
    }
    function release(c){if(--c.users>0)return;c.dead=true;if(c.sheet)c.sheet.dispose();delete caches[c.cfg.id];}
    function detach(player){
        var state=player._streetEffect;if(!state)return;
        player.removeEventListener(egret.Event.ENTER_FRAME,state.tick,player);player.removeEventListener(egret.Event.REMOVED_FROM_STAGE,state.removed,player);
        if(state.bitmap.parent)state.bitmap.parent.removeChild(state.bitmap);
        if(player._armature)player._armature.visible=true;
        release(state.cache);player._streetEffect=null;var i=players.indexOf(player);if(i>=0)players.splice(i,1);
    }
    function render(player){
        var state=player._streetEffect;if(!state)return;
        var display=player._armature,animation=display&&display.animation,clock=animation&&animation.lastAnimationState;
        if(display)display.visible=false;
        if(!clock||!state.cache.ready){state.bitmap.visible=false;return;}
        var cfg=state.cfg,frame=Math.min(cfg.frameCount-1,Math.max(0,Math.floor(clock.currentTime*cfg.fps+0.0001)));
        if(state.frame!==frame){state.bitmap.texture=state.cache.textures[frame];state.frame=frame;audit.framesPresented++;}
        state.bitmap.x=cfg.render.x;state.bitmap.y=cfg.render.y;state.bitmap.width=cfg.render.width;state.bitmap.height=cfg.render.height;state.bitmap.alpha=cfg.render.alpha===undefined?1:cfg.render.alpha;state.bitmap.visible=true;
    }
    function attach(player,name){
        var cfg=byModel[String(name)];if(!cfg){detach(player);return;}
        if(player._streetEffect&&player._streetEffect.cfg===cfg)return;
        detach(player);var bitmap=new egret.Bitmap();bitmap.name='generatedStreetEffect';bitmap.touchEnabled=false;bitmap.blendMode=egret.BlendMode.ADD;bitmap.visible=false;player.addChild(bitmap);
        var state={cfg:cfg,cache:acquire(cfg),bitmap:bitmap,frame:-1,tick:null,removed:null};state.tick=function(){render(player);};state.removed=function(){detach(player);};
        player._streetEffect=state;player.addEventListener(egret.Event.ENTER_FRAME,state.tick,player);player.addEventListener(egret.Event.REMOVED_FROM_STAGE,state.removed,player);players.push(player);
        audit.models[name]=(audit.models[name]||0)+1;render(player);
    }
    function install(){
        if(installed||!global.StreetEffectsData||!global.DBPlayer||new URLSearchParams(location.search).get('streetfx')==='0')return;
        StreetEffectsData.effects.forEach(function(cfg){cfg.models.forEach(function(name){byModel[name]=cfg;});});
        var proto=DBPlayer.prototype,init=proto.init,ready=proto.readyToPlay,destroy=proto.destroy,reset=proto.reset;
        proto.init=function(name){var result=init.apply(this,arguments);attach(this,name);return result;};
        proto.readyToPlay=function(){var result=ready.apply(this,arguments);render(this);return result;};
        proto.reset=function(){detach(this);return reset.apply(this,arguments);};
        proto.destroy=function(){detach(this);return destroy.apply(this,arguments);};
        installed=audit.installed=true;
    }
    global.StreetEffects={install:install,render:render,audit:audit,snapshot:function(){return {installed:installed,framesPresented:audit.framesPresented,errors:audit.errors.slice(),models:audit.models,caches:Object.keys(caches).map(function(key){var c=caches[key];return {id:key,users:c.users,ready:c.ready};}),active:players.map(function(p){return {model:p._dbName,frame:p._streetEffect.frame,ready:p._streetEffect.cache.ready,onStage:!!p.stage,nativeVisible:!!(p._armature&&p._armature.visible)};})};}};
})(window);
