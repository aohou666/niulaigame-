"""Append reviewed generated locomotion/recoil to an existing native-clock atlas."""
import argparse, hashlib, json, math
from pathlib import Path
from PIL import Image
from street_atomic import atomic_write_text

ROOT=Path(__file__).resolve().parents[1]; GAME=ROOT/'local_game'
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--version',required=True);p.add_argument('--hurt-start',type=int,required=True);p.add_argument('--hurt-peak',type=int,required=True);a=p.parse_args()
folder=ROOT/'art-migration/generation'/a.name
assert json.loads((folder/'alpha-review.json').read_text('utf8'))['status']=='approved'
design=json.loads((folder/'idle-design.json').read_text('utf8'));hid=design['heroId']
datafile=GAME/'street-body-data.js';data=json.loads(datafile.read_text('utf8').split('=',1)[1].strip().rstrip(';'))
cfg=next(c for c in data['characters'] if c['id']==hid);assert not cfg.get('independentMotionSource'),'Already promoted'
assert abs(cfg['bodyHeight']-design['bodyHeight'])<.001 and cfg['root']==design['root']
images=[];bounds=[]
def append_source(name):
 source=ROOT/name;d=json.loads((source/('body-design.json' if (source/'body-design.json').exists() else 'idle-design.json')).read_text('utf8'));job=json.loads((source/'job.json').read_text('utf8'))
 assert len(d['sourceFrameOrder'])==len(job['outputs'])==73
 qa=json.loads((ROOT/d['sourceBodyJob']/'body-qa.json').read_text('utf8'));assert qa['manualVideoReview']=='approved-for-matting' and qa['automaticChecksPassed']
 for raw,matte in zip(d['sourceFrameOrder'],job['outputs']):
  im=Image.open(ROOT/raw).convert('RGB').convert('RGBA');alpha=Image.open(ROOT/matte['path']).getchannel('A').point(lambda v:0 if v<9 else v);im.putalpha(alpha);box=alpha.point(lambda v:255 if v>16 else 0).getbbox();assert box and min(box[0],box[1],512-box[2],512-box[3])>2
  images.append(im);bounds.append(box)
append_source(cfg['source'])
if cfg.get('independentIdleSource'):append_source(cfg['independentIdleSource'])
assert len(images)==len(cfg['frames']),'Retain every existing source frame/index'
offset=len(images);append_source(folder.relative_to(ROOT).as_posix())
box=[min(b[0] for b in bounds)-2,min(b[1] for b in bounds)-2,max(b[2] for b in bounds)+2,max(b[3] for b in bounds)+2]
size=[round((box[2]-box[0])*192/max(box[2]-box[0],box[3]-box[1])),round((box[3]-box[1])*192/max(box[2]-box[0],box[3]-box[1]))]
atlas=Image.new('RGBA',(10*(size[0]+2),math.ceil(len(images)/10)*(size[1]+2)));rects=[]
for i,im in enumerate(images):
 tile=im.crop(box).resize(size,Image.Resampling.LANCZOS);x=i%10*(size[0]+2);y=i//10*(size[1]+2);atlas.paste(tile,(x,y));rects.append(dict(x=x,y=y,w=size[0],h=size[1]))
auditpath=ROOT/'art-migration/versions'/a.version/'motion-native-events.json';audit=json.loads(auditpath.read_text('utf8'));assert audit['complete'];native={(r['model'],r['action']):r for r in audit['records']}
def actions(model):
 result={}
 for action,(begin,end) in design['motionSegments'].items():
  row=native[(model,action)];assert not row['events'];count=row['durationFrames']
  if action=='shouji':
   begin=a.hurt_start;peak=a.hurt_peak;assert design['motionSegments'][action][0]<=begin<peak<end
   knots=[(0,begin),(max(1,round((count-1)*.2)),peak),(count-1,end)]
   mapping=[]
   for n in range(count):
    left,right=next((x,y) for x,y in zip(knots,knots[1:]) if x[0]<=n<=y[0]);mapping.append(offset+round(left[1]+(right[1]-left[1])*(n-left[0])/(right[0]-left[0])))
  else:mapping=[offset+begin+round(n*(end-begin)/(count-1)) for n in range(count)]
  result[action]={'fps':row['fps'],'frameMap':mapping,'nativeEvents':[],'nativeImpactFrame':None,'sourceImpactFrame':None,'nativeDurationFrames':count,'sourceGeneratedJob':design['sourceBodyJob'],'sourceSegment':[begin,end]}
 return result
base=actions(cfg['models'][0]);cfg['actions'].update(base)
for model in cfg['models'][1:]:
 for action,seq in actions(model).items():
  if seq!=base[action]:cfg.setdefault('modelActionOverrides',{}).setdefault(model,{})[action]=seq
cfg.update(frames=rects,crop=box,independentMotionSource=folder.relative_to(ROOT).as_posix(),supplementalNativeActionAuditPath=auditpath.relative_to(ROOT).as_posix(),supplementalNativeActionAuditSha256=hashlib.sha256(auditpath.read_bytes()).hexdigest())
target=GAME/cfg['atlas'];atlas.save(target,lossless=True,method=6);cfg['atlasSha256']=hashlib.sha256(target.read_bytes()).hexdigest();data['version']=a.version
atomic_write_text(datafile,'window.StreetBodyData='+json.dumps(data,separators=(',',':'))+';\n')
(folder/'integration.json').write_text(json.dumps({'status':'prepared-runtime-validation-pending','heroId':hid,'version':a.version,'sourceOffset':offset,'sourceFrames':73,'actions':list(base),'crop':box,'nativeClocksRetained':True,'atlasSha256':cfg['atlasSha256']},indent=2)+'\n','utf8')
print(json.dumps({'hero':hid,'totalFrames':len(images),'newActions':list(base),'bytes':target.stat().st_size}))
