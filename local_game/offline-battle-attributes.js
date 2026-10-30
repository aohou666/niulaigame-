(function(global){
 'use strict';
 // fillLocalAdvancedAttrs emits these offline UI values in percentage points.
 // Native BattleAIAttrData uses them directly in e.g.1+Hit-Miss and needs ratios.
 var ids=[11,12,13,14,15,16,17,18,19,20,21,22,23,24,29,30,33,34,92,93,94,301,302,303,304,311,312,313,314,315,316,317,318,319,320,321,333];
 function prepare(input){
  var copy=JSON.parse(JSON.stringify(input)),audit=[];
  (copy.teams||[]).forEach(function(team){(team.entities||[]).forEach(function(entity){
   var ext=typeof entity.ext==='string'?JSON.parse(entity.ext||'{}'):(entity.ext||{});
   if(ext.offlineAdvancedAttrUnit!=='percent-points')return;
   var attrs=typeof entity.attr==='string'?JSON.parse(entity.attr||'{}'):Object.assign({},entity.attr||{}),changed={};
   ids.forEach(function(id){if(attrs[id]===undefined)return;var value=Number(attrs[id]);if(!isFinite(value))throw Error('Invalid offline rate '+entity.entityId+'/'+id);attrs[id]=value/100;changed[id]={display:value,native:attrs[id]};});
   entity.attr=JSON.stringify(attrs);ext.offlineAdvancedAttrUnit='native-ratios';entity.ext=JSON.stringify(ext);
   audit.push({entityId:entity.entityId,code:entity.code,changes:changed});
  });});
  return {input:copy,audit:audit};
 }
 global.OfflineBattleAttributes={prepare:prepare,percentPointIds:ids.slice()};
})(window);
