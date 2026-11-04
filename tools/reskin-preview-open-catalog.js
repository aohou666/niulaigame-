CharacterReskin.openCatalog();
JSON.stringify({cards:document.querySelectorAll('.rc-card').length,portraits:document.querySelectorAll('.rc-card img').length,names:[].slice.call(document.querySelectorAll('.rc-card b'),0,8).map(function(n){return n.textContent;})})
