(function(global){
 'use strict';
 // Keep the original child-armature clocks and draw only approved FX slots.
 // This initial path covers battle bodies. UI previews require separate fitting.
 var audit={presented:0,restored:0,errors:[]};
 function approved(player,skin){
  var key=String(player._dbName||'')+'_bin',entry=(global.StreetArtData&&StreetArtData.containers||[]).filter(function(r){return r.originalKey===key&&Number(r.skinCode)===Number(skin);})[0],names={};
  function collect(r){if(r.nativeRuntimeAuditSha256&&r.nativeAnimationReplacement)names[r.nativeAnimationReplacement]=true;(r.inheritedReplacements||[]).forEach(collect);}
  if(entry)collect(entry);return names;
 }
 function restore(player,owner){
  var s=player&&player._streetNativeFX;if(!s||(owner&&s.owner!==owner))return;
  s.slots.forEach(function(row){row.slot.visible=row.visible;});
  if(player._armature===s.display){s.display.x=s.x;s.display.y=s.y;s.display.scaleX=s.sx;s.display.scaleY=s.sy;}
  player._streetNativeFX=null;audit.restored++;
 }
 function show(player,skin,bodyHeight,owner){
  var display=player&&player._armature,arm=display&&display.armature;
  if(!arm||player._characterIdleSuppressNative){restore(player);return false;}
  var names=approved(player,skin),slots=arm.getSlots(),allowed=slots.filter(function(slot){return slot.childArmature&&names[slot.childArmature.armatureData.name];});
  if(!allowed.length){restore(player);return false;}
  var aabb=arm.armatureData.aabb;if(!aabb||aabb.height<=0){restore(player);return false;}
  var s=player._streetNativeFX;
  if(s&&(s.display!==display||s.owner!==owner)){restore(player);s=null;}
  if(!s){s={owner:owner,display:display,x:display.x,y:display.y,sx:display.scaleX,sy:display.scaleY,slots:slots.map(function(slot){return {slot:slot,visible:slot.visible};})};player._streetNativeFX=s;}
  var origin=player.localToGlobal(0,0),unit=player.localToGlobal(0,1),sy=Math.max(.01,Math.hypot(unit.x-origin.x,unit.y-origin.y)),scale=bodyHeight/(aabb.height*sy);
  display.scaleX=(s.sx<0?-1:1)*scale;display.scaleY=(s.sy<0?-1:1)*scale;
  display.x=-(aabb.x+aabb.width/2)*display.scaleX;display.y=-(aabb.y+aabb.height)*display.scaleY;
  s.slots.forEach(function(row){row.slot.visible=!!(row.visible&&row.slot.childArmature&&names[row.slot.childArmature.armatureData.name]);});
  display.visible=true;s.skin=skin;s.names=Object.keys(names);s.scale=scale;audit.presented++;return true;
 }
 function onlyFX(player){var s=player&&player._streetNativeFX,slots=s&&s.display.armature.getSlots().filter(function(slot){return slot.visible;});return !!(s&&s.display.visible&&slots.length&&slots.every(function(slot){return slot.childArmature&&s.names.indexOf(slot.childArmature.armatureData.name)>=0;}));}
 global.StreetNativeFX={show:show,restore:restore,onlyFX:onlyFX,snapshot:function(){return {presented:audit.presented,restored:audit.restored,errors:audit.errors.slice()};}};
})(window);
