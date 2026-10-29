"""Show idle and latest candidate guides side by side for actual prop/identity review."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'art-migration/generation';p=argparse.ArgumentParser();p.add_argument('ids',nargs='+',type=int);p.add_argument('--name',default='pose-compare');a=p.parse_args();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for start in range(0,len(a.ids),8):
 canvas=Image.new('RGB',(1440,mathHeight:=340*((min(8,len(a.ids)-start)+1)//2)),'#34474b');draw=ImageDraw.Draw(canvas)
 for i,hid in enumerate(a.ids[start:start+8]):
  files=[ROOT/f'local_game/assets/street/characters/{hid:03}/portrait.png'];labels=['idle']
  for kind in ['attack','skill']:
   candidates=sorted(BASE.glob(f'hero{hid:03}-{kind}-v*/qa.json'),reverse=True);path=next((path for path in candidates if json.loads(path.read_text('utf8'))['manualReview']!='rejected'),None);files.append(ROOT/json.loads(path.read_text('utf8'))['image'] if path else None);labels.append(kind+(' '+path.parent.name.rsplit('-',1)[-1] if path else ' missing'))
  for k,path in enumerate(files):
   x=(i%2)*720+k*240;y=(i//2)*340
   if path:
    with Image.open(path) as im:
     im=im.convert('RGBA');im=im.crop(im.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox());im.thumbnail((228,290));canvas.paste(im,(x+(240-im.width)//2,y+290-im.height),im)
   draw.text((x+6,y+302),str(hid)+' '+labels[k],font=font,fill='white')
 canvas.save(ROOT/f'outputs/street-reskin/{a.name}-{start//8+1}.jpg',quality=95)
