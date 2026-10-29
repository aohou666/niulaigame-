(function (global) {
    'use strict';
    var data = global.CharacterReskinData, uiHero = null, ready = false, visibleHeroView = null, visibleHeroCode = null;
    var heroFields = ['name','definition','activeSkillDesc','storyTitle1','storyTitle2','storyTitle3','storyDesc1','storyDesc2','storyDesc3'];
    function protectedRow(row, fields) {
        var out = {};
        Object.keys(row || {}).sort().forEach(function (key) { if (fields.indexOf(key) < 0) out[key] = row[key]; });
        return JSON.stringify(out);
    }
    function forCode(code) {
        var cfg = global.config && config.HeroLO.Get(Number(code));
        return cfg && data.heroes[String(cfg.subType)];
    }
    function withHero(code, callback, owner, args) {
        var previous = uiHero; uiHero = forCode(code);
        try { return callback.apply(owner, args); } finally { uiHero = previous; }
    }
    function visibleHeroContext() {
        var view = visibleHeroView;
        if (!view || !view.stage) return null;
        for (var p = view; p; p = p.parent) if (p.visible === false) return null;
        return forCode(visibleHeroCode);
    }
    function showHeroName(view, code) {
        var h = forCode(code), bitmapLabel = view.blb_name;
        if (!h || !bitmapLabel || !bitmapLabel.parent) return;
        var vertical=global.customui&&customui.CommonHeroName&&view instanceof customui.CommonHeroName;
        var label = view._reskinName;
        if (!label) {
            label = new eui.Label();label.width=vertical?60:400;label.height=vertical?260:58;
            label.size=vertical?30:34;label.bold=true;label.textAlign='center';label.lineSpacing=4;label.touchEnabled=false;
            label.textColor=0xffdf83;label.stroke=3;label.strokeColor=0x28170c;
            label.touchEnabled=false;bitmapLabel.parent.addChild(label);view._reskinName=label;
        }
        bitmapLabel.visible=false;label.visible=true;label.text=vertical?Array.from(h.name).join('\n'):h.name;
        if(vertical)label.horizontalCenter=0;else label.x=bitmapLabel.x+(bitmapLabel.width-400)/2;
        label.y=bitmapLabel.y;
        if(global.CharacterReskinAudit){global.CharacterReskinAudit.renderedNames=global.CharacterReskinAudit.renderedNames||{};global.CharacterReskinAudit.renderedNames[h.id]=label.text;}
    }
    function showPortrait(view, model, code) {
        var h = forCode(code);
        if (!model || !model.parent) return;
        if (!h) {
            model.visible = true;
            if (view._reskinPortrait) view._reskinPortrait.visible = false;
            return;
        }
        if (h.id === 13 || (global.CharacterIdle && global.CharacterIdle.has(h.id))) {
            model.visible = true;
            if (view._reskinPortrait) view._reskinPortrait.visible = false;
            if (h.id !== 13) global.CharacterIdle.bindView(model, h.id);
            return;
        }
        var parent = model.parent, image = view._reskinPortrait;
        if (!image) {
            image = new eui.Image(); image.touchEnabled = false; image.fillMode = 'scale';
            view._reskinPortrait = image; parent.addChild(image);
        }
        model.visible = false;
        image.visible = true;
        image.width = 250; image.height = 350;
        image.x = model.x - 125; image.y = model.y - 350;
        view._reskinPortraitId = h.id;
        RES.getResByUrl(h.portrait, function (texture) {
            if (!texture || view._reskinPortraitId !== h.id) return;
            image.source = texture;
            var w = texture.textureWidth, ht = texture.textureHeight;
            var scale = Math.min(280 / w, 365 / ht);
            image.width = w * scale; image.height = ht * scale;
            image.x = model.x - image.width / 2; image.y = model.y - image.height;
        }, image, RES.ResourceItem.TYPE_IMAGE);
    }
    function wrapView(ctor, method, codeGetter, modelGetter) {
        if (!ctor || !ctor.prototype[method]) return;
        var original = ctor.prototype[method];
        ctor.prototype[method] = function () {
            var code = codeGetter(this), result = withHero(code, original, this, arguments);
            code=codeGetter(this)||code;
            visibleHeroView = this;visibleHeroCode = code;
            showHeroName(this, code);
            showPortrait(this, modelGetter(this), code);
            return result;
        };
    }
    function apply() {
        if (ready || !data || !global.game || !global.config) return;
        var heroStore = game.Config.pack.t_hero, skillStore = game.Config.pack.t_skill_base;
        var beforeHeroes = {}, beforeSkills = {}, owners = {}, changed = 0;
        Object.keys(heroStore).forEach(function (code) {
            var row = heroStore[code], h = data.heroes[String(row.subType)];
            beforeHeroes[code] = protectedRow(row, heroFields);
            ['normalSkill','actSkill','posSkill1','posSkill2','posSkill3'].forEach(function (slot) {
                if (!row[slot]) return;
                var id = String(row[slot]); owners[id] = owners[id] || {};
                owners[id][String(row.subType)] = true;
            });
            if (!h) return;
            if (h.matched) {
                row.name = h.name;
                row.definition = h.definition;
                if (h.activeSkillDesc) row.activeSkillDesc = h.activeSkillDesc;
                Object.keys(h.story).forEach(function (key) { row[key] = h.story[key]; });
                changed++;
            }
        });
        Object.keys(skillStore).forEach(function (id) { beforeSkills[id] = protectedRow(skillStore[id], ['name','desc']); });
        Object.keys(data.heroes).forEach(function (id) {
            var h = data.heroes[id];
            Object.keys(h.skills).forEach(function (skillId) {
                var row = skillStore[skillId], s = h.skills[skillId];
                if (row && owners[skillId] && Object.keys(owners[skillId]).length === 1) {
                    row.name = s.name; row.desc = s.desc;
                }
            });
        });
        // 共用技能只在角色展示上下文返回文案副本，原记录及效果保持。
        var skillGet = config.SkillBaseLO.Get;
        config.SkillBaseLO.Get = function (id) {
            var row = skillGet.call(this, id), context = uiHero || visibleHeroContext();
            var display = context && context.skills[String(id)];
            return row && display ? Object.assign({}, row, {name:display.name,desc:display.desc}) : row;
        };
        var heroDifferences = [], skillDifferences = [];
        Object.keys(beforeHeroes).forEach(function (code) { if (beforeHeroes[code] !== protectedRow(heroStore[code], heroFields)) heroDifferences.push(code); });
        Object.keys(beforeSkills).forEach(function (id) { if (beforeSkills[id] !== protectedRow(skillStore[id], ['name','desc'])) skillDifferences.push(id); });
        if (heroDifferences.length || skillDifferences.length) throw new Error('换皮修改了禁止字段');
        global.CharacterReskinAudit = {version:data.version,heroRows:changed,heroSlots:Object.keys(data.heroes).length,portraits:Object.keys(data.heroes).filter(function(id){return !!data.heroes[id].portrait;}).length,protectedHeroDifferences:heroDifferences,protectedSkillDifferences:skillDifferences};
        wrapView(game.HeroMainView, 'updateHeroInfo', function (v) { return v.curInfo && v.curInfo.code; }, function (v) { return v.hero_model; });
        wrapView(game.HeroMainInfoView, 'updateView', function (v) { return v.info && v.info.code; }, function (v) { return v.hero_model; });
        wrapView(game.HeroDetailView, '_updateHeroBaseInfo', function (v) { return v.targetHeroCfg && v.targetHeroCfg.code; }, function (v) { return v.model; });
        if (global.customui) wrapView(customui.HeroDetailView, 'updateHeroInfo', function (v) { return v.baseConfig && v.baseConfig.code; }, function (v) { return v.model; });
        if(global.customui&&customui.CommonHeroName){var nameUpdate=customui.CommonHeroName.prototype.update;customui.CommonHeroName.prototype.update=function(code){var result=nameUpdate.apply(this,arguments);showHeroName(this,code);return result;};}
        if(game.HeroBagView_ListItem){
            var itemProto=game.HeroBagView_ListItem.prototype,itemChanged=itemProto.dataChanged;
            itemProto.dataChanged=function(){
                var result=itemChanged.apply(this,arguments),item=this,image=this.img_icon,source=image.source;
                this.scrollRect=new egret.Rectangle(0,0,196,143);
                image.scaleX=image.scaleY=1;image.x=30;image.y=8;image.width=150;image.height=104;image.fillMode='scale';
                function record(loaded){var audit=global.CharacterReskinAudit;if(audit&&item.data){audit.bagItems=audit.bagItems||{};audit.bagItems[item.data.uuid]={id:item.data.config.subType,loaded:loaded,x:image.x,y:image.y,width:image.width,height:image.height,inside:image.x>=0&&image.y>=0&&image.x+image.width<=196.01&&image.y+image.height<=143.01};}}
                function fit(texture){if(item.img_icon!==image||image.source!==source||!texture)return;var w=texture.textureWidth,h=texture.textureHeight;if(!w||!h)return;var ratio=Math.min(150/w,104/h);image.width=w*ratio;image.height=h*ratio;image.x=30+(150-image.width)/2;image.y=8+104-image.height;record(true);}
                record(false);
                if(typeof source==='string'){var texture=RES.getRes(source);if(texture)fit(texture);else RES.getResAsync(source,fit,item);}else fit(source);
                return result;
            };
        }
        if(global.CharacterArt)global.CharacterArt.install();
        if(global.StreetArt)global.StreetArt.install();
        ready = true;
        installCatalog();
        console.log('[RESKIN] protected configuration verified', JSON.stringify(global.CharacterReskinAudit));
        if (new URLSearchParams(location.search).get('reskin') === 'catalog') setTimeout(openCatalog, 1200);
    }
    function esc(value) { return String(value == null ? '' : value).replace(/[&<>"']/g,function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
    function installCatalog() {
        document.documentElement.style.backgroundColor='#211e28';
        document.body.style.backgroundColor='#211e28';
        var style = document.createElement('style');
        style.textContent = '.rc-open{position:fixed;right:10px;top:42px;z-index:650000;border:1px solid #d5ac66;border-radius:14px;background:#362b20ec;color:#fff1cf;padding:8px 13px;font-size:14px}.rc-root{position:fixed;inset:0;z-index:960000;background:#171b24;color:#f4efe5;overflow:auto;font-family:Arial,"Microsoft YaHei",sans-serif}.rc-head{position:sticky;top:0;display:flex;align-items:center;gap:12px;background:#222838;padding:13px 16px;z-index:2;border-bottom:1px solid #706044}.rc-head strong{font-size:20px;flex:1}.rc-root button{background:#e9c987;color:#292216;border:0;border-radius:8px;padding:9px 14px;font-size:14px}.rc-search{margin:14px;width:calc(100% - 54px);background:#252d3d;border:1px solid #535d73;border-radius:9px;padding:12px;color:white;font-size:16px}.rc-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding:0 14px 20px}.rc-card{background:#272e3d;border-radius:13px;overflow:hidden;text-align:center;border:1px solid #495163}.rc-card img{width:100%;height:170px;object-fit:contain;background:#f7f5f1}.rc-card div{padding:10px 5px}.rc-card b{font-size:14px}.rc-card small{display:block;color:#aeb6c5;margin-top:6px;font-size:12px}.rc-detail{padding:18px;max-width:720px;margin:auto}.rc-detail img{float:right;width:42%;max-height:320px;object-fit:contain;background:#f7f5f1;border-radius:16px;margin:0 0 16px 16px}.rc-detail h2{font-size:23px;color:#ebca88}.rc-detail h3{clear:both;border-top:1px solid #434c5e;padding-top:18px;color:#ebca88}.rc-detail p{white-space:pre-wrap;font-size:15px;line-height:1.75}.rc-skill{padding:13px;background:#272e3d;border-radius:10px;margin:10px 0}.rc-skill b{color:#e9c987}.rc-skill p{margin:7px 0 0}.rc-empty{padding:18px;color:#aeb6c5}';
        document.head.appendChild(style);
        var button = document.createElement('button'); button.className = 'rc-open'; button.textContent = '角色图鉴'; button.onclick = openCatalog;
        document.body.appendChild(button);
    }
    function openCatalog() {
        var old = document.querySelector('.rc-root'); if (old) old.remove();
        var root = document.createElement('div'); root.className = 'rc-root';
        document.body.appendChild(root);
        function renderList(query) {
            var list = Object.keys(data.heroes).map(function (id) {return data.heroes[id];}).filter(function (h) {return !query || h.name.indexOf(query)>=0 || h.originalName.indexOf(query)>=0;});
            root.innerHTML = '<div class="rc-head"><strong>离谱街区角色图鉴</strong><button data-close>返回游戏</button></div><input class="rc-search" placeholder="搜索角色名称" value="'+esc(query||'')+'"><div class="rc-grid">'+list.map(function (h) {return '<div class="rc-card" data-hero="'+h.id+'">'+(h.portrait?'<img src="'+h.portrait+'">':'<div class="rc-empty">'+(h.matched?'立绘待补':'原角色保留')+'</div>')+'<div><b>'+esc(h.name)+'</b><small>'+esc(h.portraitStatus)+'</small></div></div>';}).join('')+'</div>';
            root.querySelector('[data-close]').onclick=function(){root.remove();};
            root.querySelector('.rc-search').oninput=function(){var q=this.value;renderList(q);var input=root.querySelector('.rc-search');input.focus();input.setSelectionRange(q.length,q.length);};
            root.querySelectorAll('[data-hero]').forEach(function (n) {n.onclick=function(){renderDetail(data.heroes[n.dataset.hero]);};});
        }
        function renderDetail(h) {
            var slots={}, skills=[];
            Object.keys(h.skills).forEach(function (id) {var s=h.skills[id];if(!slots[s.slot]||s.level<slots[s.slot].level)slots[s.slot]=s;});
            ['普通技能','怒气技能','被动技能1','被动技能2','被动技能3'].forEach(function (slot) {if(slots[slot])skills.push(slots[slot]);});
            root.innerHTML='<div class="rc-head"><button data-back>角色列表</button><strong>'+esc(h.name)+'</strong><button data-close>返回游戏</button></div><div class="rc-detail">'+(h.portrait?'<img src="'+h.portrait+'">':'')+'<h2>'+esc(h.name)+'</h2><p>'+esc(h.definition)+'</p><h3>技能</h3>'+skills.map(function (s){return '<div class="rc-skill"><b>'+esc(s.name)+'</b><p>'+esc(s.desc)+'</p></div>';}).join('')+'<h3>故事梗概</h3><p>'+esc(h.synopsis||'暂沿用原角色故事。')+'</p>'+[1,2,3].filter(function(i){return h.story['storyDesc'+i];}).map(function(i){return '<h3>'+esc(h.story['storyTitle'+i])+'</h3><p>'+esc(h.story['storyDesc'+i])+'</p>';}).join('')+'</div>';
            root.scrollTop=0;root.querySelector('[data-back]').onclick=function(){renderList('');};root.querySelector('[data-close]').onclick=function(){root.remove();};
        }
        renderList('');
    }
    global.CharacterReskin = {activeView:function(){return visibleHeroView;},apply:apply,openCatalog:openCatalog,forCode:forCode,withHero:withHero};
})(window);
