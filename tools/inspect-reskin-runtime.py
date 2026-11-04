from pathlib import Path
import re
s=Path('local_game/js/main.min_6fea25ed.js').read_text(encoding='utf-8')
for token in ['prototype.updateHeroInfo=function','HeroMainViewSkin','HeroDetailViewSkin']:
    p=s.find(token)
    print(token,s[max(0,p-130):p+2400])
