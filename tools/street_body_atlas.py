"""Package approved body motion; preserve native action clocks and fixed root."""
import json, math, hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'art-migration/generation/hero001-body-actions-matte-v1'
job=json.loads((folder/'job.json').read_text('utf8'))
design=json.loads((folder/'body-design.json').read_text('utf8'))
assert design['manualVideoReview']=='approved-for-matting'
frames=[];bounds=[]
for raw,entry in zip(design['sourceFrameOrder'],job['outputs']):
 rgb=Image.open(ROOT/raw).convert('RGB');alpha=Image.open(ROOT/entry['path']).getchannel('A')
 alpha=alpha.point(lambda a:0 if a<9 else a)
 rgba=rgb.convert('RGBA');rgba.putalpha(alpha);frames.append(rgba)
 box=alpha.point(lambda a:255 if a>16 else 0).getbbox();assert box
 bounds.append(box)
assert len(frames)==73
box=(min(b[0] for b in bounds)-2,min(b[1] for b in bounds)-2,max(b[2] for b in bounds)+2,max(b[3] for b in bounds)+2)
assert box[0]>0 and box[1]>0 and box[2]<512 and box[3]<512
size=(round((box[2]-box[0])*192/max(box[2]-box[0],box[3]-box[1])),round((box[3]-box[1])*192/max(box[2]-box[0],box[3]-box[1])))
cols=10;rows=math.ceil(len(frames)/cols);atlas=Image.new('RGBA',(cols*(size[0]+2),rows*(size[1]+2)))
rects=[];contact=Image.new('RGB',(1024,1024),'#63747a');draw=ImageDraw.Draw(contact)
for i,im in enumerate(frames):
 tile=im.crop(box).resize(size,Image.Resampling.LANCZOS);x=(i%cols)*(size[0]+2);y=(i//cols)*(size[1]+2);atlas.paste(tile,(x,y));rects.append(dict(x=x,y=y,w=size[0],h=size[1]))
for i in range(16):
 n=round(i*72/15);im=frames[n].copy();im.thumbnail((250,230));contact.paste(im,((i%4)*256,(i//4)*256),im);draw.text(((i%4)*256,(i//4)*256+233),str(n),fill='white')
out=ROOT/'local_game/assets/street/characters/001/actions';out.mkdir(parents=True,exist_ok=True)
atlas.save(out/'body.webp',lossless=True,method=6)
contact.save(ROOT/'outputs/street-reskin/body-final-alpha-contact.jpg',quality=95)
def attack(n):
 if n<=12:return round(n*10/12)
 if n<=18:return round(10+(n-12)*14/6)
 return round(24+(n-18)*11/23)
cfg={'version':'0.25.0','characters':[{'id':1,'models':['hero_001_01','hero_001_01_ez'],'atlas':'assets/street/characters/001/actions/body.webp','frames':rects,'crop':list(box),'root':[256,466.7],'bodyHeight':413.3,'actions':{'gongji':{'fps':30,'frameMap':[attack(n) for n in range(42)],'nativeImpactFrame':12,'sourceImpactFrame':10},'jineng':{'fps':30,'frameMap':[36+round(n*36/47) for n in range(48)]}},'source':folder.relative_to(ROOT).as_posix()}]}
cfg['characters'][0]['atlasSha256']=hashlib.sha256((out/'body.webp').read_bytes()).hexdigest()
datafile=ROOT/'local_game/street-body-data.js'
if datafile.exists():
 old=json.loads(datafile.read_text('utf8').split('=',1)[1].strip().rstrip(';'));cfg['characters']+= [r for r in old['characters'] if r['id']!=1];cfg['characters'].sort(key=lambda r:r['id']);cfg['version']=max([cfg['version'],old['version']],key=lambda s:tuple(map(int,s.split('.'))))
datafile.write_text('window.StreetBodyData='+json.dumps(cfg,separators=(',',':'))+';\n','utf8')
(folder/'integration.json').write_text(json.dumps({'status':'prepared-runtime-validation-pending','crop':box,'tileSize':size,'nativeClocksRetained':True,'sha256':hashlib.sha256((out/'body.webp').read_bytes()).hexdigest()},indent=2)+'\n','utf8')
print(json.dumps({'frames':len(frames),'crop':box,'atlasSize':atlas.size,'bytes':(out/'body.webp').stat().st_size}))
