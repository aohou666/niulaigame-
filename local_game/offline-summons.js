(function(global){
 'use strict';
 var installed=false,audit={installed:false,created:[],detonations:[],guards:[],rendererLinks:[],copiedBuffValues:0,totals:{created:0,detonations:0,guards:0,rendererLinks:0}};
 function record(kind,row){audit.totals[kind]++;audit[kind].push(row);if(audit[kind].length>512)audit[kind].shift();}
 function list(value){return value?JSON.parse(value):[];}
 function state(world){var id=world.battleResultP&&world.battleResultP.battleInfo.uuid;if(!world._streetSummons||world._streetSummons.uuid!==id)world._streetSummons={uuid:id,owners:{},created:[],pending:[],flushing:false};return world._streetSummons;}
 function ownerState(world,owner){var s=state(world);return s.owners[owner.id]||(s.owners[owner.id]={ownerId:owner.id,generation:0,current:null,forward:[]});}
 function dtoFor(world,id){var teams=world.battleResultP.teams;for(var i=0;i<teams.length;i++)for(var j=0;j<teams[i].entities.length;j++)if(Number(teams[i].entities[j].entityId)===Number(id))return {team:teams[i],entity:teams[i].entities[j]};return null;}
 function registerForward(owner,buff,world){var o=ownerState(world,owner);list(buff.cfg.effectEx).forEach(function(code){if(o.forward.indexOf(Number(code))<0)o.forward.push(Number(code));});}
 function spawn(owner,buff,world){
  var ext=list(buff.cfg.effectEx),hero=config.HeroLO.Get(Number(ext[0])),source=dtoFor(world,owner.id);if(!hero||!source)throw Error('Summon authored template/owner missing: '+buff.code);
  var o=ownerState(world,owner),old=o.current&&world.entites.getValue(o.current),replace=old&&!old.isDead;var generation=++o.generation;
  // Reserve a separate unique suffix so the first predecessor is not the caster.
  // Wrap indices without crossing camps; explicit renderer links bridge each generation.
  var camp=game.BattleAIUtils.GetCampByID(owner.id),pos=Math.floor(Number(owner.id)/100)%10,index=2+(generation-1)%8,unique=1+Math.floor((generation-1)/8);if(unique>99)throw Error('Summon protocol capacity exhausted');var id=camp*10000+index*1000+pos*100+unique;
  var attr={};Object.keys(owner.attr).forEach(function(key){attr[key]=Number(key)===game.EAttrType.Life?owner.getInitAttr(Number(key)):owner.getAttr(Number(key));});
  (ext[1]||[]).forEach(function(pair){attr[pair[0]]=Math.ceil(Number(attr[pair[0]]||0)*Number(pair[1])/1000);});
  if(replace)(ext[2]||[]).forEach(function(pair){attr[pair[0]]=Math.ceil(Number(attr[pair[0]]||0)*Number(pair[1])/1000);});
  var skills=[hero.normalSkill,hero.actSkill,hero.posSkill1,hero.posSkill2,hero.posSkill3].filter(function(code){return Number(code)&&config.SkillBaseLO.Get(Number(code));});
  var dto={entityId:id,code:hero.code,type:game.BattleEntityType.FireRobot,level:source.entity.level,dermaCode:0,anger:Number(hero.initEnergy)||0,angerMax:Number(hero.maxEnergy)||4,life:Number(attr[game.EAttrType.Life]),lifeMax:Number(attr[game.EAttrType.Life]),attr:JSON.stringify(attr),skillIds:skills,ext:JSON.stringify({offlineSummon:true,ownerId:owner.id,generation:generation,previousEntityId:o.current||0,sourceBuffId:buff.code})};
  var entity=game.BattleAIUtils.createAIEntityByData(dto);entity._streetSummonOwner=owner.id;source.team.entities.push(dto);world.entites.setValue(entity.id,entity);state(world).created.push(JSON.parse(JSON.stringify(dto)));o.current=id;buff.value=id;
  o.forward.forEach(function(code){var cfg=config.BuffLO.Get(code);if(cfg&&cfg.type===85)entity._streetGuard={buffId:code,coeff:list(cfg.effectEx),ownerId:owner.id};});
  if(replace)state(world).pending.push({oldId:old.id,ownerId:owner.id,newId:id});
  record('created',{ownerId:owner.id,entityId:id,code:dto.code,sourceBuffId:buff.code,lifeMax:dto.lifeMax,atk:attr[game.EAttrType.Atk],replaced:!!replace});
 }
 function detonate(world){
  var s=state(world);if(s.flushing)return;s.flushing=true;
  try{while(s.pending.length){var row=s.pending.shift(),old=world.entites.getValue(row.oldId);if(!old||old.isDead)continue;
   var event=new game.BattleAISkillEventData(game.BattleAIDamageType.SKILL_ATTACK,0);event.sourceID=old.id;event.offlineDetonatingId=old.id;event.offlineSummonOwnerId=row.ownerId;
   game.BattleAITriggerMgr.getInstance().triggerEvent(game.EConditionType.FireRobotDetonate,world,event);
   var life=old.life;game.BattleAIEntityProcess.changeEntityLife(old,-life);var res=game.BattleAIReportHelper.createBattleRes(old);res.value=-life;res.life=0;res.sourceId=row.ownerId;world.addBattleRes(res);game.BattleAIEntityProcess.onDead(old,world);record('detonations',row);
  }}finally{s.flushing=false;}
 }
 function guard(target,world,res,event){
  if(!event||event.damage<=0)return;
  var entries=state(world).owners,chosen=null;Object.keys(entries).some(function(key){var current=entries[key].current,npc=current&&world.entites.getValue(current);if(npc&&!npc.isDead&&npc.id!==target.id&&npc._streetGuard&&game.BattleAIUtils.GetCampByID(npc.id)===game.BattleAIUtils.GetCampByID(target.id)){chosen=npc;return true;}return false;});if(!chosen)return;
  var cfg=chosen._streetGuard,damage=Number(event.damage),transfer=Math.ceil(damage*Number(cfg.coeff[0]||0)/1000);event.damage=Math.ceil(damage*Number(cfg.coeff[2]||0)/1000);
  game.BattleAIEntityProcess.changeEntityLife(chosen,-transfer);var hit=game.BattleAIReportHelper.createBattleRes(chosen);hit.sourceId=event.sourceID;hit.skillId=event.skillID;hit.value=-transfer;hit.life=chosen.resLife;hit.buffAdd=[{buffId:cfg.buffId,type:85,value:0}];world.addBattleRes(hit);if(chosen.isDead)game.BattleAIEntityProcess.onDead(chosen,world);
  record('guards',{ownerId:cfg.ownerId,targetId:target.id,entityId:chosen.id,incoming:damage,transferred:transfer,remaining:event.damage,mitigation:damage-transfer-event.damage});
  var trigger=new game.BattleAISkillEventData(game.BattleAIDamageType.SKILL_ATTACK,transfer);trigger.sourceID=event.sourceID;trigger.offlineSummonOwnerId=cfg.ownerId;game.BattleAITriggerMgr.getInstance().triggerEventWithEntityID(game.EConditionType.FireRobotHelp,event.sourceID,world,trigger);
 }
 function collect(world,payload){
  state(world).created.forEach(function(dto){var camp=game.BattleAIUtils.GetCampByID(dto.entityId),team=payload.teams[camp-1];if(!team)throw Error('Summon renderer camp missing '+camp);if(!team.entities.some(function(e){return Number(e.entityId)===Number(dto.entityId);}))team.entities.push(JSON.parse(JSON.stringify(dto)));});
 }
 function rendererLink(args,original,context){
  if(!args||!args.buff||[131,142].indexOf(Number(args.buff.type))<0)return original.call(context,args);
  var models=args.ins.id2FightModel,current=models[Number(args.buff.value)],meta=current&&JSON.parse(current.curEntity.ext||'{}');if(!meta||!meta.offlineSummon)return original.call(context,args);
  var info=current.fightModelInfo,step=Number(args.buff.type)===131?-1:1,key=''+info.camp+(info.index+step)+info.posId+info.unique,linked=null;
  Object.keys(models).some(function(id){var candidate=models[id],data=candidate&&candidate.curEntity;if(!data)return false;if(step<0&&(candidate.isDead||candidate._isDead||Number(candidate.life)<=0))return false;var ext=JSON.parse(data.ext||'{}');if(ext.offlineSummon&&ext.ownerId===meta.ownerId&&ext.generation===meta.generation+step){linked=candidate;return true;}return false;});
  var had=Object.prototype.hasOwnProperty.call(models,key),saved=models[key];if(linked)models[key]=linked;else delete models[key];record('rendererLinks',{type:Number(args.buff.type),entityId:Number(args.buff.value),linkedId:linked&&linked.curEntity.entityId||0});
  // Native handlers synchronously capture predecessor/successor before awaiting VFX.
  var row=audit.rendererLinks[audit.rendererLinks.length-1],start=Date.now();
  try{var result=original.call(context,args);return result&&result.then?result.then(function(value){row.completed=true;row.elapsedMs=Date.now()-start;return value;}):result;}finally{if(had)models[key]=saved;else delete models[key];}
 }
 function install(){
  if(installed||!global.game||!game.BattleAIBaseSkillEffect)return;
  var parser=game.BattleAIBuffParserMgr.Ins,create=new game.BattleAIBaseBuff,forward=new game.BattleAIBaseBuff,explode=new game.BattleAIBaseBuff;
  create.onAdd=spawn;forward.onAdd=registerForward;explode.onAdd=function(target,buff,world,event){var source=event&&world.entites.getValue(event.sourceID);if(!source||source.entityType!==game.BattleEntityType.FireRobot)throw Error('Detonation buff has no authored summon source');buff.value=source.id;};
  parser.dict.setValue(game.EBuffType.FireRobot,create);parser.dict.setValue(game.EBuffType.FireRobotSkill,forward);parser.dict.setValue(game.EBuffType.FireRobotDetonate,explode);
  var base=game.BattleAIBaseSkillEffect.prototype,execute=base.executeBuffList,before=base.exectBuffListBeforeDamage;
  base.executeBuffList=function(target,codes,world,result,event){var value=execute.apply(this,arguments);(result.buffAdd||[]).forEach(function(pb){for(var i=target.buffLst.length-1;i>=0;i--){var b=target.buffLst.get(i);if(Number(b.code)===Number(pb.buffId)){if(b.value!==undefined){pb.value=b.value;audit.copiedBuffValues++;}break;}}});return value;};
  base.exectBuffListBeforeDamage=function(target,world,result,event){var value=before.apply(this,arguments);guard(target,world,result,event);return value;};
  var zero=game.BattleAISkillEffect0.prototype,zeroExecute=zero.execute;zero.execute=function(source,effect,targets,world,event){var result=zeroExecute.apply(this,arguments);detonate(world);return result;};
  game.BattleAIConditionMgr.Ins.dict.setValue(game.EConditionType.FireRobotDetonate,{check:function(source,target,condition,world,event){return !!event&&(Number(condition[1])===1?source.id===event.offlineDetonatingId:source.id===event.offlineSummonOwnerId);}});
  game.BattleAIConditionMgr.Ins.dict.setValue(game.EConditionType.FireRobotHelp,{check:function(source,target,condition,world,event){return !!event&&source.id===event.offlineSummonOwnerId;}});
  game.BattleAITargetFilterMgr.Ins.dict.setValue(48,{filter:function(entities,source,args,event){var result=new List;for(var i=0;i<entities.length;i++)if(event&&entities[i].id===event.sourceID)result.push(entities[i]);return result;}});
  var get=game.FB_base.get;game.FB_base.get=function(args){return rendererLink(args,get,this);};
  installed=audit.installed=true;
 }
 global.OfflineSummons={install:install,collect:collect,audit:audit};
})(window);
