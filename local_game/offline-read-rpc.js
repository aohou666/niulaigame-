(function(global){
    'use strict';
    var save=null,installed=false,trainingRead=null,pending=[];
    function read(module,action){
        var stateSave=typeof save==='function'?save():save;
        if((module==='peakWar'&&action==='GetPeakWarFreedomInfo')||(module==='spectralTower'&&action==='GetSpectralTowerInfo')){
            if(!trainingRead)return new Promise(function(resolve,reject){pending.push({module:module,action:action,resolve:resolve,reject:reject});});
            return null;
        }
        if(module==='kit'&&action==='GetKitInfo')return Promise.resolve({err:0,kitList:stateSave&&(stateSave.kitList||stateSave.kits)||[],historyList:stateSave&&stateSave.kitHistory||[]});
        if(module==='mount'&&action==='GetMountInfo')return Promise.resolve({err:0,mountList:stateSave&&(stateSave.mountList||stateSave.mounts)||[],mountInfo:stateSave&&stateSave.mountInfo||{historyList:[],handbookList:[]}});
        if(module==='mountEquip'&&action==='GetMountEquipInfo')return Promise.resolve({err:0,equipList:stateSave&&(stateSave.mountEquipList||stateSave.mountEquips)||[]});
        if(module==='worldEmpires'&&action==='GetWorldEmpiresCurDt'){
            var start=new Date();start.setHours(0,0,0,0);
            var end=new Date(start.getTime());end.setDate(end.getDate()+1);
            return Promise.resolve({err:0,startDt:Math.floor(start.getTime()/1000),endDt:Math.floor(end.getTime()/1000)});
        }
        if(module==='guildDefence'&&action==='GetGuildDefenceInfo'){
            var state=stateSave&&stateSave.guildDefence||{code:0,stageInfos:[]};
            return Promise.resolve({err:0,playerInfo:{code:Number(state.code)||0},stageInfos:state.stageInfos||[]});
        }
        return null;
    }
    function installEarly(){
        if(installed||!global.Utils||!Utils.Socket)return;
        var original=Utils.Socket.send;
        Utils.Socket.send=function(module,action){return read(module,action)||original.apply(this,arguments);};
        installed=true;
    }
    global.OfflineReadRPC={read:read,installEarly:installEarly,setSave:function(value){save=value;},setTrainingRead:function(handler){trainingRead=handler;var queue=pending;pending=[];queue.forEach(function(job){Promise.resolve().then(function(){return handler(job.module,job.action);}).then(job.resolve,job.reject);});}};
})(window);
