(function(global){
    'use strict';
    var installed=false,earlyPrepared=false,applied={},audit={installed:false,bindings:[],errors:[],earlyConfigInstalls:0};
    function install(early){
        if(installed||!global.StreetArtData||!global.RES||!RES.config)return;
        StreetArtData.resources.forEach(function(r){
            if(applied[r.originalKey])return;
            if(!RES.hasRes(r.originalKey)&&r.originalAvailability!=='missing-native-ui-key'){if(!early)audit.errors.push({key:r.originalKey,error:'original key missing'});return;}
            RES.config.addResourceData({name:r.targetKey,url:r.targetPath+'?v='+r.targetSha256.slice(0,16),type:'image',root:''});
            RES.config.addAlias(r.originalKey,r.targetKey);
            (r.extraAliases||[]).forEach(function(key){RES.config.addAlias(key,r.targetKey);});
            audit.bindings.push({original:r.originalKey,target:r.targetKey,url:r.targetPath});
            applied[r.originalKey]=true;
        });
        if(early)audit.earlyConfigInstalls++;
        else installed=audit.installed=true;
    }
    function prepareEarly(){
        if(earlyPrepared||!global.RES||typeof RES.loadConfig!=='function')return;
        earlyPrepared=true;
        var load=RES.loadConfig;
        RES.loadConfig=function(){
            return load.apply(this,arguments).then(function(value){install(true);return value;});
        };
    }
    global.StreetArt={install:install,prepareEarly:prepareEarly,audit:audit};
})(window);
