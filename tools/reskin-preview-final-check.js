JSON.stringify({
  version:CharacterReskinAudit.version,
  audit:CharacterReskinAudit,
  visibleRole:document.querySelector('.rc-detail h2').textContent,
  description:document.querySelector('.rc-detail p').textContent,
  skills:[].map.call(document.querySelectorAll('.rc-skill b'),function(n){return n.textContent;}),
  imageLoaded:document.querySelector('.rc-detail img').complete && document.querySelector('.rc-detail img').naturalWidth>0,
  storyVisible:document.querySelector('.rc-detail').innerText.indexOf('故事梗概')>=0,
  plannerNotesRemoved:document.querySelector('.rc-detail').innerText.indexOf('原鲁肃的结盟')<0,
  configName:config.HeroLO.Get(41000040).name,
  rawSharedName:config.SkillBaseLO.Get(550690210).name,
  scopedSharedName:CharacterReskin.withHero(41000078,function(){return config.SkillBaseLO.Get(550690210).name;})
})
