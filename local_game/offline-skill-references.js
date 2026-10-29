(function(global){
 'use strict';
 var installed=false,families={},skills=null,audit={installed:false,references:[],unresolved:[],lookupFallbacks:{},savedReferences:[],skillDefinitionsChanged:false};
 function resolve(code){
  code=Number(code);if(!code||!skills||skills[code])return code;
  var entries=families[Math.floor(code/100)]||[],candidate=0;
  for(var i=0;i<entries.length;i++)if(entries[i]<=code)candidate=entries[i];
  return candidate||code;
 }
 function install(){
  if(installed||!global.game||!game.Config.pack.t_skill_base||!global.config||!config.SkillBaseLO)return;
  skills=game.Config.pack.t_skill_base;var before=JSON.stringify(skills),fields=['normalSkill','actSkill','posSkill1','posSkill2','posSkill3'],seen={};
  Object.keys(skills).map(Number).sort(function(a,b){return a-b;}).forEach(function(code){var family=Math.floor(code/100);(families[family]||(families[family]=[])).push(code);});
  function patch(row){
   if(!row)return;
   fields.forEach(function(field){var requested=Number(row[field]);if(!requested||skills[requested])return;var replacement=resolve(requested),key=row.code+':'+field;
    if(replacement!==requested){row[field]=replacement;if(!seen[key]){seen[key]=true;audit.references.push({hero:row.subType,code:row.code,field:field,requested:requested,resolved:replacement,reason:'requested rank absent; highest authored rank in the same skill family'});}}
    else if(!seen[key]){seen[key]=true;audit.unresolved.push({hero:row.subType,code:row.code,field:field,requested:requested});}
   });
  }
  Object.keys(game.Config.pack.t_hero).forEach(function(key){patch(game.Config.pack.t_hero[key]);});
  Object.keys(config.HeroLO.Store).forEach(function(key){patch(config.HeroLO.Get(Number(key)));});
  var get=config.SkillBaseLO.Get;
  config.SkillBaseLO.Get=function(code){var resolved=resolve(code);if(Number(code)!==resolved)audit.lookupFallbacks[code]=resolved;return get.call(this,resolved);};
  audit.skillDefinitionsChanged=before!==JSON.stringify(skills);if(audit.skillDefinitionsChanged)throw Error('Skill-reference repair changed an authored skill definition');
  installed=audit.installed=true;
 }
 function normalizeSave(save){
  if(!installed||!save||!Array.isArray(save.heroes))return;
  save.heroes.forEach(function(hero){if(!Array.isArray(hero.skillList))return;hero.skillList.forEach(function(entry,index){if(!entry)return;var old=Number(entry.code),next=resolve(old);if(old&&next!==old&&skills[next]){entry.code=next;audit.savedReferences.push({uuid:hero.uuid,index:index,requested:old,resolved:next});}});});
 }
 global.OfflineSkillReferences={install:install,resolve:resolve,normalizeSave:normalizeSave,audit:audit};
})(window);
