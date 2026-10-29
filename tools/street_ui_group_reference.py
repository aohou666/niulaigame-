"""Compose labeled references only; final replacement art must be generated and reviewed."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();folder=ROOT/'art-migration/ui-groups';group=json.loads((folder/(a.name+'.json')).read_text('utf8'));manifest=json.loads((GAME/'resource/default.res_49784.json').read_text('utf8'));resources={r['name']:r for r in manifest['resources']}
cell=256;canvas=Image.new('RGBA',(cell*group['columns'],cell*group['rows']),'#40555e');draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for i,entry in enumerate(group['entries']):
 r=resources[entry['key']];entry['originalPath']='resource/'+r['url'];im=Image.open(GAME/entry['originalPath']).convert('RGBA');entry['size']=list(im.size);im.thumbnail((212,212),Image.Resampling.LANCZOS);x=(i%group['columns'])*cell;y=(i//group['columns'])*cell;canvas.alpha_composite(im,(x+(cell-im.width)//2,y+24+(cell-24-im.height)//2));draw.text((x+10,y+5),str(i+1),font=font,fill='white')
canvas.save(folder/(a.name+'-reference.png'));(folder/(a.name+'.json')).write_text(json.dumps(group,ensure_ascii=False,indent=2)+'\n','utf8');print(folder/(a.name+'-reference.png'))
