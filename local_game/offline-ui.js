(function (global) {
    "use strict";

    var styleAdded = false;
    function addStyle() {
        if (styleAdded) return;
        styleAdded = true;
        var style = document.createElement("style");
        style.textContent = [
            ".ol-root{position:fixed;inset:0;z-index:800000;background:linear-gradient(#401c12,#160c09);color:#f8e7c2;font-family:Arial,'Microsoft YaHei',sans-serif;overflow:auto;padding:18px;box-sizing:border-box}",
            ".ol-head{position:sticky;top:0;z-index:4;display:flex;align-items:center;gap:12px;padding:12px 14px;background:#21130fee;border:1px solid #9e6b2d;border-radius:12px;box-shadow:0 6px 20px #0008}",
            ".ol-head h1{font-size:27px;margin:0;flex:1;color:#ffd06b}.ol-muted{color:#cbb99a;font-size:14px}.ol-btn{border:1px solid #e4ad4d;border-radius:8px;padding:10px 13px;background:linear-gradient(#ffe08a,#c98a29);color:#321b0b;font-weight:700;font-size:15px;cursor:pointer}.ol-btn.red{background:linear-gradient(#f59a78,#a33b2c);color:#fff}.ol-btn.dark{background:#3b2a20;color:#f6d99c}.ol-btn:disabled{filter:grayscale(1);opacity:.55}",
            ".ol-section{max-width:900px;margin:16px auto;padding:16px;background:#251611e8;border:1px solid #76502c;border-radius:14px}.ol-section h2{margin:0 0 12px;color:#ffc75c;font-size:22px}",
            ".ol-lineup{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.ol-slot{min-height:92px;border:1px dashed #a87536;border-radius:10px;padding:10px;background:#342118;display:flex;gap:9px;align-items:center}.ol-slot.selected{outline:3px solid #ffd369}.ol-slot b{display:block}.ol-slot small{color:#cbb99a}",
            ".ol-portrait{width:62px;height:62px;object-fit:cover;border-radius:9px;background:#523725;border:2px solid #bb8540}.ol-roster{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.ol-card{position:relative;min-height:154px;padding:8px;border:1px solid #77512d;border-radius:10px;background:#332118;text-align:center}.ol-card.in{border-color:#ffd369;box-shadow:0 0 10px #ffbd3f88}.ol-card .ol-portrait{width:76px;height:76px}.ol-card b{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ol-card small{display:block;color:#cfb995}.ol-card button{margin-top:6px;width:100%;padding:6px}",
            ".ol-tools{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}.ol-tools input,.ol-tools select{background:#1d1512;color:#f7e4bd;border:1px solid #77512d;border-radius:7px;padding:9px;font-size:15px}",
            ".ol-scenarios{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.ol-scenario{padding:15px;border:1px solid #74502e;border-radius:12px;background:#342116;cursor:pointer}.ol-scenario.selected{border:3px solid #ffd36c}.ol-scenario h3{margin:0 0 6px;color:#ffd36c}.ol-preview{display:flex;gap:7px;flex-wrap:wrap}.ol-chip{padding:6px 9px;border-radius:18px;background:#59402c;font-size:13px}",
            ".ol-world-hud{position:fixed;inset:0;z-index:700000;pointer-events:none;font-family:Arial,'Microsoft YaHei',sans-serif}.ol-world-top{position:absolute;top:86px;left:10px;right:10px;display:flex;gap:7px;flex-wrap:wrap;pointer-events:auto}.ol-world-bottom{position:absolute;left:8px;right:8px;bottom:14px;display:grid;grid-template-columns:repeat(4,1fr);gap:6px;padding:8px;background:#21130ed9;border:1px solid #a87432;border-radius:12px;pointer-events:auto}.ol-world-bottom .ol-btn,.ol-world-top .ol-btn{font-size:13px;padding:8px 6px}.ol-world-scene{position:absolute;left:0;right:0;top:150px;bottom:190px;pointer-events:none}.ol-world-scene.moving{pointer-events:auto;background:#ffca4410}.ol-marker{position:absolute;transform:translate(-50%,-50%);pointer-events:auto;transition:left .8s ease,top .8s ease;text-align:center;color:#fff;font-size:12px;text-shadow:0 1px 3px #000}.ol-marker i{display:grid;place-items:center;width:42px;height:42px;border-radius:50%;border:3px solid #fff;background:#34915b;font-style:normal;font-size:22px;box-shadow:0 2px 8px #000}.ol-marker.enemy i{background:#b64035}.ol-marker.city i{border-radius:8px;background:#b7882d}.ol-marker.selected i{outline:4px solid #ffe165}.ol-marker span{display:block;padding:2px 5px;background:#000a;border-radius:5px;white-space:nowrap}",
            ".ol-modal-wrap{position:fixed;inset:0;z-index:900000;display:grid;place-items:center;background:#0009;padding:20px;font-family:Arial,'Microsoft YaHei',sans-serif}.ol-modal{width:min(680px,96vw);max-height:82vh;overflow:auto;background:#271712;color:#f8e5bd;border:2px solid #bf8537;border-radius:16px;padding:20px}.ol-modal h2{margin:0 0 12px;color:#ffd16a}.ol-modal table{width:100%;border-collapse:collapse}.ol-modal th,.ol-modal td{padding:9px;border-bottom:1px solid #64442c;text-align:left}.ol-modal-actions{display:flex;gap:9px;margin-top:15px;flex-wrap:wrap}.ol-toast{position:fixed;left:50%;top:18%;transform:translateX(-50%);z-index:950000;background:#23150eef;border:1px solid #e8b34d;border-radius:10px;padding:12px 18px;color:#ffe2a0;font-weight:700;box-shadow:0 4px 18px #000a}",
            "@media(max-width:600px){.ol-root{padding:9px}.ol-head h1{font-size:22px}.ol-lineup{grid-template-columns:repeat(2,1fr)}.ol-roster{grid-template-columns:repeat(3,1fr)}.ol-scenarios{grid-template-columns:1fr}.ol-section{padding:11px}.ol-world-bottom{grid-template-columns:repeat(4,1fr)}}"
        ].join("");
        document.head.appendChild(style);
    }

    function esc(value) {
        return String(value == null ? "" : value).replace(/[&<>\"']/g, function (c) {
            return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];
        });
    }
    function num(value) { return Number(value) || 0; }
    function rootPage(title, subtitle) {
        addStyle();
        var gameDiv = document.getElementById("gameDiv");
        if (gameDiv) gameDiv.style.display = "none";
        var old = document.querySelector(".ol-root");
        if (old) old.remove();
        var root = document.createElement("div");
        root.className = "ol-root";
        root.innerHTML = '<div class="ol-head"><button class="ol-btn dark" data-home>返回入口</button><div><h1>'+esc(title)+'</h1><div class="ol-muted">'+esc(subtitle)+'</div></div></div>';
        root.querySelector("[data-home]").onclick = function () { location.href = "offline-launcher.html"; };
        document.body.appendChild(root);
        return root;
    }
    function toast(message) {
        addStyle();
        var node = document.createElement("div");
        node.className = "ol-toast";
        node.textContent = message;
        document.body.appendChild(node);
        setTimeout(function () { node.remove(); }, 2200);
    }
    function modal(title, html, actions) {
        addStyle();
        var wrap = document.createElement("div");
        wrap.className = "ol-modal-wrap";
        wrap.innerHTML = '<div class="ol-modal"><div style="display:flex;gap:10px;align-items:center;position:sticky;top:0;background:#271712;z-index:2"><h2 style="flex:1">'+esc(title)+'</h2><button class="ol-btn dark" data-modal-close>关闭</button></div><div class="ol-modal-body">'+html+'</div><div class="ol-modal-actions"></div></div>';
        wrap.querySelector('[data-modal-close]').onclick=function(){wrap.remove();};
        var footer = wrap.querySelector(".ol-modal-actions");
        (actions || []).forEach(function (action) {
            var button = document.createElement("button");
            button.className = "ol-btn " + (action.className || "");
            button.textContent = action.text;
            button.onclick = function () { action.onClick(wrap); };
            footer.appendChild(button);
        });
        var close = document.createElement("button"); close.className="ol-btn dark"; close.textContent="关闭"; close.onclick=function(){wrap.remove();}; footer.appendChild(close);
        document.body.appendChild(wrap);
        return wrap;
    }

    function textureToImage(img, keys, initials) {
        img.alt = initials;
        function tryAt(index) {
            if (index >= keys.length || !global.RES || !RES.getResAsync) return;
            var key = keys[index];
            if (!key) return tryAt(index + 1);
            Promise.resolve(RES.getResAsync(key)).then(function (texture) {
                if (!texture) return tryAt(index + 1);
                var bitmap = texture.$bitmapData || texture.bitmapData || texture;
                var source = bitmap && (bitmap.source || bitmap.$source || bitmap);
                if (!source || !source.width) return tryAt(index + 1);
                var x = num(texture.$bitmapX), y = num(texture.$bitmapY);
                var w = num(texture.$bitmapWidth) || num(texture.textureWidth) || source.width;
                var h = num(texture.$bitmapHeight) || num(texture.textureHeight) || source.height;
                var canvas = document.createElement("canvas"); canvas.width = Math.max(1,w); canvas.height = Math.max(1,h);
                canvas.getContext("2d").drawImage(source,x,y,w,h,0,0,w,h);
                img.src = canvas.toDataURL("image/png");
                img.dataset.loaded = "1";
            }).catch(function () { tryAt(index + 1); });
        }
        tryAt(0);
    }
    function heroCatalog(ctx) {
        return ctx.state.heroes.map(function (hero) {
            var cfg = ctx.config.HeroLO.Get(hero.code) || {};
            return {hero:hero,cfg:cfg,name:cfg.name || ("武将"+hero.code),keys:[(cfg.avatar2||"")+"_png",(cfg.avatar||"")+"_png",(cfg.halfPic||"")+"_png"]};
        }).sort(function(a,b){return num(b.hero.pos)-num(a.hero.pos)||num(a.cfg.race)-num(b.cfg.race)||num(a.cfg.subType)-num(b.cfg.subType);});
    }

    function showHeroes(ctx) {
        var root = rootPage("英雄与阵容", "点击阵位后选择武将上阵；点击已上阵武将可下阵。所有更改立即写入本地存档。");
        var lineupSection=document.createElement("section"); lineupSection.className="ol-section";
        var rosterSection=document.createElement("section"); rosterSection.className="ol-section";
        root.appendChild(lineupSection); root.appendChild(rosterSection);
        var catalog=heroCatalog(ctx), selectedPos=1, query="", race=0;
        function saveFormation() {
            ctx.state.formation = ctx.state.heroes.filter(function(h){return num(h.pos)>0&&num(h.pos)<=6;}).map(function(h){return {uuid:h.uuid,pos:num(h.pos)};}).sort(function(a,b){return a.pos-b.pos;});
            ctx.save();
            if (ctx.game.GameMVC.heroPy) ctx.game.GameMVC.heroPy.handleHeroList(ctx.state.heroes);
        }
        function renderLineup() {
            var slots=[];
            for(var pos=1;pos<=6;pos++){
                var item=catalog.find(function(x){return num(x.hero.pos)===pos;});
                slots.push('<div class="ol-slot '+(selectedPos===pos?'selected':'')+'" data-pos="'+pos+'">'+(item?'<img class="ol-portrait" data-hero="'+esc(item.hero.uuid)+'"><div><b>'+esc(item.name)+'</b><small>'+item.hero.level+'级 · 战力'+num(item.hero.fightCap)+'</small><button class="ol-btn red" data-down="'+esc(item.hero.uuid)+'">下阵</button></div>':'<div><b>阵位 '+pos+'</b><small>选择此位置，再点击下方武将</small></div>')+'</div>');
            }
            lineupSection.innerHTML='<h2>当前阵容（'+ctx.state.formation.length+'/6）</h2><div class="ol-lineup">'+slots.join('')+'</div>';
            lineupSection.querySelectorAll('[data-pos]').forEach(function(node){node.onclick=function(e){if(e.target.dataset.down)return;selectedPos=num(node.dataset.pos);renderLineup();renderRoster();};});
            lineupSection.querySelectorAll('[data-down]').forEach(function(btn){btn.onclick=function(e){e.stopPropagation();var h=ctx.state.heroes.find(function(x){return x.uuid===btn.dataset.down;});if(h)h.pos=0;saveFormation();renderLineup();renderRoster();toast('武将已下阵');};});
            lineupSection.querySelectorAll('img[data-hero]').forEach(function(img){var item=catalog.find(function(x){return x.hero.uuid===img.dataset.hero;});textureToImage(img,item.keys,item.name.slice(0,1));});
        }
        function renderRoster(){
            var filtered=catalog.filter(function(item){return (!query||item.name.indexOf(query)>=0||String(item.hero.code).indexOf(query)>=0)&&(!race||num(item.cfg.race)===race);});
            rosterSection.innerHTML='<h2>武将背包（显示 '+filtered.length+' / '+catalog.length+'）</h2><div class="ol-tools"><input data-search placeholder="搜索武将名称或编号" value="'+esc(query)+'"><select data-race><option value="0">全部阵营</option><option value="1">魏</option><option value="2">蜀</option><option value="3">吴</option><option value="4">群</option></select><button class="ol-btn dark" data-top>回到顶部</button></div><div class="ol-roster">'+filtered.map(function(item){var inTeam=num(item.hero.pos)>0;return '<div class="ol-card '+(inTeam?'in':'')+'"><img class="ol-portrait" data-hero="'+esc(item.hero.uuid)+'"><b>'+esc(item.name)+'</b><small>'+item.hero.level+'级 · '+(item.hero.starLevel||item.cfg.initStar||0)+'星</small><small>编号 '+item.hero.code+'</small><button class="ol-btn '+(inTeam?'red':'')+'" data-pick="'+esc(item.hero.uuid)+'">'+(inTeam?'下阵（位置'+item.hero.pos+'）':'上阵到位置 '+selectedPos)+'</button></div>';}).join('')+'</div>';
            rosterSection.querySelector('[data-race]').value=String(race);
            rosterSection.querySelector('[data-search]').oninput=function(){query=this.value.trim();renderRoster();};
            rosterSection.querySelector('[data-race]').onchange=function(){race=num(this.value);renderRoster();};
            rosterSection.querySelector('[data-top]').onclick=function(){scrollTo(0,0);};
            rosterSection.querySelectorAll('[data-pick]').forEach(function(btn){btn.onclick=function(){var hero=ctx.state.heroes.find(function(x){return x.uuid===btn.dataset.pick;});if(!hero)return;if(num(hero.pos)>0){hero.pos=0;toast('武将已下阵');}else{ctx.state.heroes.forEach(function(x){if(num(x.pos)===selectedPos)x.pos=0;});hero.pos=selectedPos;toast(heroCatalog(ctx).find(function(x){return x.hero.uuid===hero.uuid;}).name+' 已上阵');}saveFormation();renderLineup();renderRoster();};});
            rosterSection.querySelectorAll('img[data-hero]').forEach(function(img){var item=catalog.find(function(x){return x.hero.uuid===img.dataset.hero;});textureToImage(img,item.keys,item.name.slice(0,1));});
        }
        renderLineup(); renderRoster();
    }

    var scenarios=[
        {id:"yellow",name:"黄巾余党",desc:"群雄步兵与术士，适合测试普通技能",offset:3,color:"#8d6b25"},
        {id:"wei",name:"曹魏精锐",desc:"高防御阵容，敌方反击伤害较高",offset:17,color:"#315a91"},
        {id:"shu",name:"蜀汉突击",desc:"高速度阵容，首回合连续反击",offset:31,color:"#468742"},
        {id:"wu",name:"江东火阵",desc:"主动技能频繁，第二回合压力更高",offset:47,color:"#a74739"},
        {id:"legend",name:"名将试炼",desc:"随机正式武将组成可编辑挑战队",offset:61,color:"#7f4895"},
        {id:"god",name:"神将天团",desc:"神阵营随机组合",offset:79,color:"#c59538"},
        {id:"demon",name:"魔将军团",desc:"魔阵营随机组合",offset:97,color:"#713d83"},
        {id:"mixed",name:"六势联军",desc:"六个势力完全随机",offset:113,color:"#536b72"},
        {id:"cavalry",name:"铁骑突袭",desc:"前排压制型随机组合",offset:131,color:"#8a5534"},
        {id:"shield",name:"铜墙铁壁",desc:"防御与护盾型随机组合",offset:149,color:"#496477"},
        {id:"burst",name:"雷霆斩首",desc:"爆发型随机组合",offset:167,color:"#a43c32"},
        {id:"control",name:"奇谋控场",desc:"控制型随机组合",offset:191,color:"#4b598f"},
        {id:"healing",name:"回春战阵",desc:"治疗续航型随机组合",offset:223,color:"#3d7d61"}
    ];
    function showBattleConfig(ctx){
        var root=rootPage("战斗配置", "选择敌方阵容、难度和敌军数量，再进入使用原模型、技能与特效的本地战斗。");
        var section=document.createElement("section");section.className="ol-section";root.appendChild(section);
        var saved=ctx.state.battleConfig||{};
        var chosen=scenarios.some(function(s){return s.id===saved.scenario;})?saved.scenario:"yellow";
        var difficulty=["normal","hard","hell"].indexOf(saved.difficulty)>=0?saved.difficulty:"normal";
        var enemyCount=Math.max(1,Math.min(8,num(saved.enemyCount)||8));
        function persistConfig(){ctx.state.battleConfig={scenario:chosen,difficulty:difficulty,enemyCount:enemyCount};ctx.save();}
        function render(){
            section.innerHTML='<h2>敌方部队</h2><div class="ol-scenarios">'+scenarios.map(function(s){return '<div class="ol-scenario '+(chosen===s.id?'selected':'')+'" data-scenario="'+s.id+'" style="border-color:'+s.color+'"><h3>'+s.name+'</h3><div>'+s.desc+'</div><div class="ol-preview"><span class="ol-chip">阵容种子 '+s.offset+'</span><span class="ol-chip">正式武将</span></div></div>';}).join('')+'</div><h2 style="margin-top:20px">战斗规则</h2><div class="ol-tools"><label>难度 <select data-diff><option value="normal">普通</option><option value="hard">困难</option><option value="hell">炼狱</option></select></label><label>敌军人数 <select data-count>'+[1,2,3,4,5,6,7,8].map(function(n){return '<option value="'+n+'">'+n+'人</option>';}).join('')+'</select></label></div><div class="ol-muted">原包 test_skill 战报包含 11–18 共八个敌方阵位；本地战斗已恢复 1–8 人，并在每次开战时按新种子随机抽取正式武将。普通：敌军反击约8%；困难：约16%；炼狱：约24%。</div><div style="margin-top:20px"><button class="ol-btn" data-start style="width:100%;font-size:22px">开始本地阵容战</button></div>';
            section.querySelector('[data-diff]').value=difficulty;section.querySelector('[data-count]').value=String(enemyCount);
            section.querySelectorAll('[data-scenario]').forEach(function(n){n.onclick=function(){chosen=n.dataset.scenario;persistConfig();render();};});
            section.querySelector('[data-diff]').onchange=function(){difficulty=this.value;persistConfig();};section.querySelector('[data-count]').onchange=function(){enemyCount=num(this.value);persistConfig();};
            section.querySelector('[data-start]').onclick=function(){persistConfig();location.href='index_bh_lite3zbtest_andr.html?mode=demo&scenario='+encodeURIComponent(chosen)+'&difficulty='+encodeURIComponent(difficulty)+'&enemyCount='+enemyCount;};
        }persistConfig();render();
    }

    function ensureWorld(state){
        var w=state.world||(state.world={}); if(!Array.isArray(w.units))w.units=[];if(!Array.isArray(w.cities))w.cities=[];
        if (!w.visualEntitiesMigratedV8) {
            w.units = w.units.filter(function (u) { return u && u.id && isFinite(Number(u.x)) && isFinite(Number(u.y)); });
            w.cities = w.cities.filter(function (c) { return c && c.id && isFinite(Number(c.x)) && isFinite(Number(c.y)); });
            w.visualEntitiesMigratedV8 = true;
        }
        w.nextId=num(w.nextId)||1;w.buildings=w.buildings||{camp:1,forge:1,market:1};w.pendingRewards=w.pendingRewards||{gold:0,iron:0,pill:0};w.bountyDone=num(w.bountyDone);w.fourProgress=num(w.fourProgress);w.lastHarvest=num(w.lastHarvest)||Date.now();return w;
    }
    function showWorld(ctx){
        addStyle();var w=ensureWorld(ctx.state);ctx.save();var hud=document.createElement('div');hud.className='ol-world-hud';
        hud.innerHTML='<div class="ol-world-top"><button class="ol-btn" data-act="friend">生成友军</button><button class="ol-btn red" data-act="enemy">生成敌军</button><button class="ol-btn" data-act="players">生成5名玩家</button><button class="ol-btn" data-act="city">生成城池</button><button class="ol-btn dark" data-act="move">指定移动</button><button class="ol-btn dark" data-act="home">返回入口</button></div><div class="ol-world-scene"></div><div class="ol-world-bottom"><button class="ol-btn dark" data-panel="rank">排行</button><button class="ol-btn dark" data-panel="build">建筑</button><button class="ol-btn dark" data-panel="reward">奖励</button><button class="ol-btn dark" data-panel="bounty">野外悬赏</button><button class="ol-btn dark" data-panel="four">四象争霸</button><button class="ol-btn dark" data-panel="empire">霸业宏图</button><button class="ol-btn" data-panel="harvest">一键收获</button><button class="ol-btn dark" data-panel="help">说明</button></div>';
        document.body.appendChild(hud);var scene=hud.querySelector('.ol-world-scene'),selected=null,moving=false;
        function rand(min,max){return Math.round(min+Math.random()*(max-min));}
        function persist(){ctx.save();}
        function addUnit(type){var u={id:'unit-'+w.nextId++,name:(type==='enemy'?'敌军':'友军')+(w.nextId-1),type:type,x:rand(12,88),y:rand(18,82),fightCap:80000+rand(1,15)*10000,level:30+rand(1,70)};w.units.push(u);w.pendingRewards.gold+=300;persist();renderMarkers();toast('已在地图生成'+u.name);return u;}
        function addCity(){var c={id:'city-'+w.nextId++,name:'本地城池'+(w.cities.length+1),type:'city',x:rand(15,85),y:rand(18,78),level:1,occupied:false};w.cities.push(c);persist();renderMarkers();toast('城池已生成');}
        function renderMarkers(){scene.innerHTML='';w.cities.concat(w.units).forEach(function(o){var n=document.createElement('div');n.className='ol-marker '+o.type+(selected===o.id?' selected':'');n.style.left=o.x+'%';n.style.top=o.y+'%';n.innerHTML='<i>'+(o.type==='city'?'城':o.type==='enemy'?'敌':'友')+'</i><span>'+esc(o.name)+(o.level?' Lv.'+o.level:'')+'</span>';n.onclick=function(e){e.stopPropagation();selected=o.id;renderMarkers();toast('已选择 '+o.name);};scene.appendChild(n);});}
        scene.onclick=function(e){if(!moving||!selected)return;var r=scene.getBoundingClientRect(),o=w.units.concat(w.cities).find(function(x){return x.id===selected;});if(!o)return;o.x=Math.max(4,Math.min(96,(e.clientX-r.left)/r.width*100));o.y=Math.max(5,Math.min(95,(e.clientY-r.top)/r.height*100));moving=false;scene.classList.remove('moving');persist();renderMarkers();toast(o.name+' 已移动到新位置');};
        function reward(gold,iron,pill,label){ctx.state.wallet['2']=num(ctx.state.wallet['2'])+gold;ctx.state.items['30000003']=num(ctx.state.items['30000003'])+iron;ctx.state.items['30000002']=num(ctx.state.items['30000002'])+pill;ctx.state.progress.gold=ctx.state.wallet['2'];persist();toast(label+'：铜钱+'+gold+' 玄铁+'+iron+' 进阶丹+'+pill);}
        function openPanel(kind){
            if(kind==='rank'){var people=[{name:(ctx.state.player&&ctx.state.player.name)||'本地玩家',type:'self',fightCap:(ctx.state.formation||[]).length*25000+num(ctx.state.player&&ctx.state.player.fightCap)}].concat(w.units).sort(function(a,b){return b.fightCap-a.fightCap;});modal('本地霸业排行','<table><tr><th>名次</th><th>玩家</th><th>阵营</th><th>战力</th></tr>'+people.map(function(p,i){return '<tr><td>'+(i+1)+'</td><td>'+esc(p.name)+'</td><td>'+(p.type==='self'?'自己':p.type==='enemy'?'敌对':'友方')+'</td><td>'+p.fightCap+'</td></tr>';}).join('')+'</table>');}
            else if(kind==='build'){var rows=Object.keys(w.buildings).map(function(k){var names={camp:'营地',forge:'锻造坊',market:'集市'};return '<tr><td>'+names[k]+'</td><td>'+w.buildings[k]+'级</td><td><button class="ol-btn" data-up="'+k+'">升级</button></td></tr>';}).join('');var m=modal('本地建筑','<div>升级消耗铜钱，建筑等级会提高一键收获产量。</div><table>'+rows+'</table>');m.querySelectorAll('[data-up]').forEach(function(b){b.onclick=function(){var cost=w.buildings[b.dataset.up]*2000;if(num(ctx.state.wallet['2'])<cost)return toast('铜钱不足');ctx.state.wallet['2']-=cost;w.buildings[b.dataset.up]++;persist();m.remove();openPanel('build');toast('建筑升级成功');};});}
            else if(kind==='reward'){var p=w.pendingRewards;modal('霸业奖励','<p>地图行动累计奖励：</p><table><tr><td>铜钱</td><td>'+p.gold+'</td></tr><tr><td>玄铁</td><td>'+p.iron+'</td></tr><tr><td>进阶丹</td><td>'+p.pill+'</td></tr></table>',[{text:'全部领取',onClick:function(m){reward(p.gold,p.iron,p.pill,'奖励领取成功');p.gold=p.iron=p.pill=0;persist();m.remove();}}]);}
            else if(kind==='bounty'){modal('野外悬赏','<p>完成悬赏会在地图生成一支敌军。选中敌军并移动友军靠近即可模拟追击。</p><p>已完成：'+w.bountyDone+' 次</p>',[{text:'讨伐山贼',onClick:function(m){addUnit('enemy');w.bountyDone++;w.pendingRewards.gold+=2500;w.pendingRewards.iron+=8;persist();m.remove();toast('悬赏目标已出现，奖励进入奖励中心');}}]);}
            else if(kind==='four'){modal('四象争霸','<p>当前进度：'+w.fourProgress+'/4</p><div class="ol-preview"><span class="ol-chip">青龙</span><span class="ol-chip">白虎</span><span class="ol-chip">朱雀</span><span class="ol-chip">玄武</span></div>',[{text:w.fourProgress>=4?'重置赛季':'挑战下一守卫',onClick:function(m){if(w.fourProgress>=4)w.fourProgress=0;else{w.fourProgress++;w.pendingRewards.gold+=1200;w.pendingRewards.pill+=2;}persist();m.remove();toast('四象争霸进度已更新');}}]);}
            else if(kind==='empire'){modal('霸业宏图','<p>已生成城池 '+w.cities.length+' 座，占领后持续提高收获。</p><table>'+w.cities.map(function(c){return '<tr><td>'+esc(c.name)+'</td><td>'+(c.occupied?'已占领':'中立')+'</td><td><button class="ol-btn" data-occupy="'+c.id+'">'+(c.occupied?'升级':'占领')+'</button></td></tr>';}).join('')+'</table>');document.querySelectorAll('[data-occupy]').forEach(function(b){b.onclick=function(){var c=w.cities.find(function(x){return x.id===b.dataset.occupy;});if(c){c.occupied=true;c.level++;w.pendingRewards.gold+=1000;persist();document.querySelector('.ol-modal-wrap').remove();openPanel('empire');}};});}
            else if(kind==='harvest'){var hours=Math.max(1,Math.floor((Date.now()-w.lastHarvest)/3600000)+1),levels=Object.keys(w.buildings).reduce(function(a,k){return a+w.buildings[k];},0),cities=w.cities.filter(function(c){return c.occupied;}).length,gold=hours*(1000+levels*300+cities*500);w.lastHarvest=Date.now();reward(gold,10+cities*3,2+Math.floor(levels/3),'一键收获完成');}
            else modal('世界地图说明','<p>生成的友军、敌军、玩家和城池会显示在地图上并写入本地存档。</p><p>点击地图标记进行选择，点击“指定移动”，再点击地图目标位置即可移动。</p><p>底部所有玩法均使用本地数据，不连接原服务器。</p>');
        }
        hud.querySelectorAll('[data-act]').forEach(function(b){b.onclick=function(){var a=b.dataset.act;if(a==='friend')addUnit('friend');else if(a==='enemy')addUnit('enemy');else if(a==='players'){for(var i=0;i<5;i++)addUnit(i%2?'enemy':'friend');toast('已生成5名本地玩家');}else if(a==='city')addCity();else if(a==='move'){if(!selected)return toast('请先点击选择一个单位或城池');moving=true;scene.classList.add('moving');toast('请点击地图上的目标位置');}else location.href='offline-launcher.html';};});
        hud.querySelectorAll('[data-panel]').forEach(function(b){b.onclick=function(){openPanel(b.dataset.panel);};});renderMarkers();
    }

    global.OfflineUI={showHeroes:showHeroes,showBattleConfig:showBattleConfig,showWorld:showWorld,scenarios:scenarios,toast:toast};
})(window);
