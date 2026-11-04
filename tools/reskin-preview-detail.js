document.querySelector('[data-hero="40"]').click();
JSON.stringify({name:document.querySelector('.rc-detail h2').textContent,skills:[].map.call(document.querySelectorAll('.rc-skill b'),function(n){return n.textContent;}),text:document.querySelector('.rc-detail').innerText.slice(0,1100),image:document.querySelector('.rc-detail img').getAttribute('src')})
