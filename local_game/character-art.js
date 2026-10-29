(function(global){
    'use strict';
    var installed=false,audit={version:'0.21.0',installed:false,bindings:[],conflicts:[]};
    function install(){
        if(installed||!global.CharacterArtData||!global.RES||!global.game||!game.Config.pack.t_hero)return;
        var heroes=Object.assign({},CharacterArtData.heroes,CharacterArtData.supplementalHeroes||{}),bindings={};
        function add(row,id,skin){
            var h=heroes[String(id)];if(!h)return;
            ['avatar','avatar2','halfPic','pictureDraw','dermaPic'].forEach(function(field){
                var key=row[field]&&row[field]+'_png',binding=key&&h.bindings[key];
                if(!binding)return;
                bindings[binding.name]={key:key,url:binding.url,hero:id,kind:skin?'skin-'+field:field};
                row[field]=binding.name.slice(0,-4);
            });
        }
        Object.keys(game.Config.pack.t_hero).forEach(function(key){var row=game.Config.pack.t_hero[key];add(row,row.subType,false);});
        var skins=game.Config.pack.t_hero_derma||{};
        Object.keys(skins).forEach(function(key){var row=skins[key];add(row,row.subType,true);});
        Object.keys(bindings).forEach(function(name){
            var item=bindings[name];
            RES.config.addResourceData({name:name,url:item.url,type:'image',root:''});
            audit.bindings.push({key:item.key,target:name,url:item.url,hero:item.hero,kind:item.kind});
        });
        audit.heroes=Object.keys(CharacterArtData.heroes).length;audit.supplementalHeroes=Object.keys(CharacterArtData.supplementalHeroes||{}).length;audit.skinConfigs=Object.keys(skins).length;
        audit.skinVariantsComplete=false; // Canonical identity binding is not a new skin variant.
        installed=audit.installed=true;
    }
    global.CharacterArt={install:install,audit:audit};
})(window);
