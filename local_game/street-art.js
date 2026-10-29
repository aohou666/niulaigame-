(function(global){
    'use strict';
    var installed=false,audit={installed:false,bindings:[],errors:[]};
    function install(){
        if(installed||!global.StreetArtData||!global.RES||!RES.config)return;
        StreetArtData.resources.forEach(function(r){
            if(!RES.hasRes(r.originalKey)){audit.errors.push({key:r.originalKey,error:'original key missing'});return;}
            RES.config.addResourceData({name:r.targetKey,url:r.targetPath,type:'image',root:''});
            RES.config.addAlias(r.originalKey,r.targetKey);
            (r.extraAliases||[]).forEach(function(key){RES.config.addAlias(key,r.targetKey);});
            audit.bindings.push({original:r.originalKey,target:r.targetKey,url:r.targetPath});
        });
        installed=audit.installed=true;
    }
    global.StreetArt={install:install,audit:audit};
})(window);
