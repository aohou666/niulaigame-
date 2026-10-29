"""Package a reviewed character sequence; native frame events remain authoritative."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';BASE=ROOT/'art-migration/generation'
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--attack-anchor',required=True,type=int);p.add_argument('--version',required=True);a=p.parse_args();folder=BASE/a.name
job=json.loads((folder/'job.json').read_text('utf8'));design=json.loads((folder/'body-design.json').read_text('utf8'));hid=design['heroId'];source=ROOT/design['sourceBodyJob'];qa=json.loads((source/'body-qa.json').read_text('utf8'))
assert qa['manualVideoReview']=='approved-for-matting' and qa['automaticChecksPassed'];assert len(job['outputs'])==len(design['sourceFrameOrder'])==73
images=[];bounds=[]
for raw,entry in zip(design['sourceFrameOrder'],job['outputs']):
 im=Image.open(ROOT/raw).convert('RGB').convert('RGBA');alpha=Image.open(ROOT/entry['path']).getchannel('A').point(lambda v:0 if v<9 else v);im.putalpha(alpha);box=alpha.point(lambda v:255 if v>16 else 0).getbbox();assert box
 assert min(box[0],box[1],512-box[2],512-box[3])>2
 images.append(im);bounds.append(box)
box=[min(b[0] for b in bounds)-2,min(b[1] for b in bounds)-2,max(b[2] for b in bounds)+2,max(b[3] for b in bounds)+2];size=[round((box[2]-box[0])*192/max(box[2]-box[0],box[3]-box[1])),round((box[3]-box[1])*192/max(box[2]-box[0],box[3]-box[1]))]
atlas=Image.new('RGBA',(10*(size[0]+2),math.ceil(len(images)/10)*(size[1]+2)));rects=[]
for i,im in enumerate(images):
 tile=im.crop(box).resize(size,Image.Resampling.LANCZOS);x=(i%10)*(size[0]+2);y=(i//10)*(size[1]+2);atlas.paste(tile,(x,y));rects.append(dict(x=x,y=y,w=size[0],h=size[1]))
out=GAME/f'assets/street/characters/{hid:03}/actions';out.mkdir(parents=True,exist_ok=True);atlas.save(out/'body.webp',lossless=True,method=6)
actions={}
for kind,action in [('attack','gongji'),('skill','jineng')]:
 plan=design['actions'][kind]['native'];count=plan['durationFrames'];begin,end=design['actions'][kind]['sourceFrames'];events=[e for e in plan['rawEvents'] if e.get('name') in ['pia','zd']]
 if kind=='attack' and events:
  assert len(events)==1,'Multiple strikes require reviewed multiple source anchors';impact=events[0]['frame0'];anchor=a.attack_anchor;assert begin<=anchor<=end and 0<impact<count-1
  frameMap=[round(begin+(anchor-begin)*n/impact) if n<=impact else round(anchor+(end-anchor)*(n-impact)/(count-1-impact)) for n in range(count)]
 else:impact=None;anchor=None;frameMap=[begin+round(n*(end-begin)/(count-1)) for n in range(count)]
 actions[action]={'fps':plan['fps'],'frameMap':frameMap,'nativeEvents':events,'nativeImpactFrame':impact,'sourceImpactFrame':anchor,'nativeDurationFrames':count}
cfg={'id':hid,'models':[design['actions']['attack']['native']['model'],design['actions']['attack']['native']['model']+'_ez'],'atlas':(out/'body.webp').relative_to(GAME).as_posix(),'frames':rects,'crop':box,'root':[256,466.7],'bodyHeight':design['inputs']['idle']['size'][1]*512/768,'actions':actions,'source':folder.relative_to(ROOT).as_posix()}
cfg['atlasSha256']=hashlib.sha256((out/'body.webp').read_bytes()).hexdigest()
p=GAME/'street-body-data.js';d=json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'));d['version']=a.version;d['characters']=[r for r in d['characters'] if r['id']!=hid]+[cfg];d['characters'].sort(key=lambda r:r['id']);p.write_text('window.StreetBodyData='+json.dumps(d,separators=(',',':'))+';\n','utf8')
contact=Image.new('RGB',(1024,1024),'#53676e');draw=ImageDraw.Draw(contact)
for i in range(16):
 n=round(i*72/15);im=images[n].copy();im.thumbnail((250,230));contact.paste(im,((i%4)*256,(i//4)*256),im);draw.text(((i%4)*256,(i//4)*256+233),str(n),fill='white')
contact.save(ROOT/f'outputs/street-reskin/body-{hid:03}-final-alpha.jpg',quality=95)
(folder/'integration.json').write_text(json.dumps({'status':'prepared-runtime-validation-pending','heroId':hid,'crop':box,'tileSize':size,'nativeClocksRetained':True,'sha256':hashlib.sha256((out/'body.webp').read_bytes()).hexdigest()},indent=2)+'\n','utf8');print(json.dumps({'hero':hid,'bytes':(out/'body.webp').stat().st_size,'actions':{k:{'nativeFrames':v['nativeDurationFrames'],'nativeImpact':v['nativeImpactFrame'],'sourceImpact':v['sourceImpactFrame']} for k,v in actions.items()}}))
