"""Typeset replacement skill title at the original native texture dimensions."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'art-migration/generation/skin100201-native-skill-title-v1'
OUT.mkdir(exist_ok=True)
font_path=Path('C:/Windows/Fonts/msyhbd.ttc')
assert font_path.exists()
title='核桃开场'
image=Image.new('RGBA',(271,110))
draw=ImageDraw.Draw(image)
font=ImageFont.truetype(str(font_path),58)
box=draw.textbbox((0,0),title,font=font,stroke_width=4)
x=(271-(box[2]-box[0]))//2-box[0]
y=(110-(box[3]-box[1]))//2-box[1]
draw.text((x,y),title,font=font,fill=(255,245,218,255),stroke_width=4,stroke_fill=(61,45,30,255))
target=OUT/'zd_txt_002_skin_01.png'
image.save(target)
original=ROOT/'local_game/resource/assets/shuzhi/jineng_banner/zd_txt_002_skin_01_805fce76.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof={'productionIntegrated':False,'visualApproval':'pending','originalKey':'zd_txt_002_skin_01_png','size':[271,110],'text':title,'originalPath':original.relative_to(ROOT).as_posix(),'originalSha256':sha(original),'sourceKind':'new typography, no original glyph pixels reused','fontPath':str(font_path),'fontSha256':sha(font_path),'targetPath':target.relative_to(ROOT).as_posix(),'targetSha256':sha(target)}
(OUT/'candidate.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'size':image.size,'alphaBounds':image.getbbox(),'text':title},ensure_ascii=False))
