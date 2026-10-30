(function(global){
 'use strict';
 var installed=false,byModel={},byArmature={},caches={},players=[],audit={framesPresented:0,errors:[],actions:{},atlasRequests:0,suppressedViewsDetached:0};
 function acquire(cfg){
  var c=caches[cfg.id];if(c){c.users++;return c;}
  c={cfg:cfg,users:1,dead:false,ready:false,textures:[],sheet:null};caches[cfg.id]=c;
  // Let detail/formation layout mark its idle-only native stand-in before I/O.
  requestAnimationFrame(function(){
   players.slice().forEach(function(p){if(p._streetBody&&p._streetBody.cache===c&&p._characterIdleSuppressNative){audit.suppressedViewsDetached++;detach(p);}});
   if(c.dead||!c.users)return;audit.atlasRequests++;
   fetch(cfg.atlas+'?v='+(cfg.atlasSha256||StreetBodyData.version),{cache:'force-cache'}).then(function(r){if(!r.ok)throw Error(r.status+' '+cfg.atlas);return r.blob();}).then(createImageBitmap).then(function(image){
   if(c.dead){image.close();return;}
   var canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;canvas.getContext('2d').drawImage(image,0,0);image.close();
   var texture=new egret.Texture();texture.disposeBitmapData=true;texture.bitmapData=new egret.BitmapData(canvas);c.sheet=new egret.SpriteSheet(texture);
   cfg.frames.forEach(function(f,i){c.textures[i]=c.sheet.createTexture(String(i),f.x,f.y,f.w,f.h);});c.ready=true;
   }).catch(function(e){audit.errors.push({hero:cfg.id,error:String(e)});});
  });return c;
 }
 function release(c){if(--c.users>0)return;c.dead=true;if(c.sheet)c.sheet.dispose();delete caches[c.cfg.id];}
 function restore(player,state){
  state.bitmap.visible=false;
  if(state.hidden&&player._armature){var idle=player._characterIdleState;player._armature.visible=!(player._characterIdleSuppressNative||(idle&&idle.hidden));}
  state.hidden=false;
 }
 function detach(player){var s=player._streetBody;if(!s)return;restore(player,s);player.removeEventListener(egret.Event.ENTER_FRAME,s.tick,player);player.removeEventListener(egret.Event.REMOVED_FROM_STAGE,s.removed,player);if(s.bitmap.parent)s.bitmap.parent.removeChild(s.bitmap);release(s.cache);player._streetBody=null;var i=players.indexOf(player);if(i>=0)players.splice(i,1);}
 function render(player){
  var s=player._streetBody;if(!s)return;
  if(player._characterIdleSuppressNative){audit.suppressedViewsDetached++;detach(player);return;}
  var action=player.action||player._action||'daiji',seq=(s.cfg.modelActionOverrides&&s.cfg.modelActionOverrides[player._dbName]&&s.cfg.modelActionOverrides[player._dbName][action])||s.cfg.actions[action],display=player._armature,clock=display&&display.animation&&display.animation.lastAnimationState;
  if(!player._characterIdleSuppressNative&&display&&(s.cfg.qualityQuarantineActions||[]).indexOf(action)>=0){
   restore(player,s);var idle=player._characterIdleState;if(idle){idle.bitmap.visible=false;idle.hidden=false;}display.visible=true;return;
  }
  if(!seq&&action!=='daiji'&&display){
   restore(player,s);var fallbackIdle=player._characterIdleState;if(fallbackIdle){fallbackIdle.bitmap.visible=false;fallbackIdle.hidden=false;}display.visible=true;return;
  }
  if(player._characterIdleSuppressNative||!seq||!clock||!s.cache.ready){restore(player,s);return;}
  var nativeFrame=Math.min(seq.frameMap.length-1,Math.max(0,Math.floor(clock.currentTime*seq.fps+.0001))),frame=seq.frameMap[nativeFrame];
  if(s.frame!==frame||s.action!==action){s.bitmap.texture=s.cache.textures[frame];s.frame=frame;s.action=action;audit.framesPresented++;audit.actions[action]=(audit.actions[action]||0)+1;}
  var origin=player.localToGlobal(0,0),unit=player.localToGlobal(0,1),sy=Math.max(.01,Math.hypot(unit.x-origin.x,unit.y-origin.y));
  var cfg=s.cfg,geometry=seq.geometry||cfg,box=geometry.crop,targetHeight=110;
  if(cfg.supplemental)for(var node=player.parent;node;node=node.parent)if(node._streetBodyViewHeroId===cfg.id){targetHeight=250;break;}
  var scale=targetHeight/(geometry.bodyHeight*sy),b=s.bitmap;
  b.x=(box[0]-geometry.root[0])*scale;b.y=(box[1]-geometry.root[1])*scale;b.width=(box[2]-box[0])*scale;b.height=(box[3]-box[1])*scale;b.visible=true;
  if(player._characterIdleState)player._characterIdleState.bitmap.visible=false;
  display.visible=false;s.hidden=true;s.nativeFrame=nativeFrame;
 }
 function attach(player,name,armature){
  var actual=armature||(player._armature&&player._armature.armature&&player._armature.armature.armatureData&&player._armature.armature.armatureData.name);
  if(/^effect_/.test(String(actual||''))){detach(player);return;}
  var key=String(name)+'/'+String(actual||''),cfg=Object.prototype.hasOwnProperty.call(byArmature,key)?byArmature[key]:byModel[String(name)];if(!cfg||player._characterIdleSuppressNative){detach(player);return;}
  if(player._streetBody&&player._streetBody.cfg===cfg)return;detach(player);
  var bitmap=new egret.Bitmap();bitmap.name='generatedStreetBody';bitmap.touchEnabled=false;bitmap.visible=false;player.addChild(bitmap);
  var s={cfg:cfg,cache:acquire(cfg),bitmap:bitmap,hidden:false,frame:-1,action:null};s.tick=function(){render(player);};s.removed=function(){detach(player);};player._streetBody=s;
  player.addEventListener(egret.Event.ENTER_FRAME,s.tick,player);player.addEventListener(egret.Event.REMOVED_FROM_STAGE,s.removed,player);players.push(player);render(player);
 }
 function install(){
  if(installed||!global.StreetBodyData||!global.DBPlayer||new URLSearchParams(location.search).get('streetbody')==='0')return;
  var skins=StreetBodyData.skins||{};
  var independent=Object.keys(skins).map(function(key){var cfg=skins[key];if(!cfg||Number(cfg.id)!==Number(key)||Number(cfg.skinCode)!==Number(key)||!cfg.heroId||!cfg.armature){audit.errors.push({skin:key,error:'invalid independent body identity or armature'});return null;}return cfg;}).filter(function(cfg){return !!cfg;});
  StreetBodyData.characters.concat(independent).forEach(function(cfg){cfg.models.forEach(function(name){
   if(cfg.skinCode&&!cfg.armature){audit.errors.push({skin:cfg.skinCode,error:'independent skin requires explicit body armature'});return;}
   var table=cfg.armature?byArmature:byModel,key=cfg.armature?String(name)+'/'+cfg.armature:String(name);
   if(Object.prototype.hasOwnProperty.call(table,key)&&table[key]!==cfg){table[key]=null;audit.errors.push({hero:cfg.id,error:'ambiguous body binding '+key});}else table[key]=cfg;
  });});
  var p=DBPlayer.prototype,init=p.init,ready=p.readyToPlay,trigger=p.trigger,reset=p.reset,destroy=p.destroy;
  p.init=function(name){detach(this);var request={model:String(name),armature:arguments[1]==null?null:String(arguments[1])};this._streetBodyRequest=request;var r=init.apply(this,arguments);this._streetBodyRequest=request;attach(this,name,request.armature);return r;};
  p.readyToPlay=function(){var r=ready.apply(this,arguments),request=this._streetBodyRequest;if(request)attach(this,request.model,request.armature);render(this);return r;};
  p.trigger=function(){var r=trigger.apply(this,arguments);render(this);return r;};
  p.reset=function(){detach(this);this._streetBodyRequest=null;return reset.apply(this,arguments);};p.destroy=function(){detach(this);this._streetBodyRequest=null;return destroy.apply(this,arguments);};installed=true;
 }
 global.StreetBody={install:install,render:render,snapshot:function(){return {installed:installed,framesPresented:audit.framesPresented,actions:audit.actions,atlasRequests:audit.atlasRequests,suppressedViewsDetached:audit.suppressedViewsDetached,errors:audit.errors.slice(),caches:Object.keys(caches).map(function(k){return {id:k,users:caches[k].users,ready:caches[k].ready};}),active:players.map(function(p){var s=p._streetBody;return {model:p._dbName,action:p.action,frame:s.frame,nativeFrame:s.nativeFrame,visible:s.bitmap.visible,nativeVisible:!!(p._armature&&p._armature.visible),ready:s.cache.ready,onStage:!!p.stage};})};}};
})(window);
