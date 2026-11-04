JSON.stringify({
  audit:window.CharacterReskinAudit,
  heroViews:game.HeroMediator.SV,
  owned:game.GameMVC.heroPy.heroBag.getItems().slice(0,8).map(function(h){return {uuid:h.uuid,code:h.code,name:h.config.name};}),
  registered:typeof game.HeroMainView.prototype.updateHeroInfo,
  sharedRaw:config.SkillBaseLO.Get(550690210).name,
  sharedScoped:CharacterReskin.withHero(41000078,function(){return config.SkillBaseLO.Get(550690210).name;}),
  portraitUrls:Object.keys(CharacterReskinData.heroes).filter(function(id){return CharacterReskinData.heroes[id].portrait;}).length
})
