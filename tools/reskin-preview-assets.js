JSON.stringify({
  resources:['_main_m_png','_hero_m_png','wujiang_img_dikuang_png'].map(function(k){return {key:k,info:RES.getResourceInfo(k),loaded:!!RES.getRes(k)};}),
  gameVisible:document.getElementById('gameDiv').style.display,
  canvasStyle:document.querySelector('canvas').getAttribute('style'),
  active:Object.keys(game.GameMVC.heroMed._views||{}),
  errors:window.CharacterReskinAudit
})
