"""Prepare an additive atlas candidate; never modify the live character mapping."""
import argparse, copy, hashlib, io, json, math
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text('utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('matte');p.add_argument('--cycle',required=True);a=p.parse_args()
b=ROOT/'art-migration/generation'/a.matte;design=read(b/'action-design.json');job=read(b/'job.json');alpha=read(b/'alpha-qa.json')
source=ROOT/design['sourceBodyJob'];raw=read(source/'job.json');qa=read(source/'body-qa.json');cycle=read(ROOT/a.cycle)
assert qa['manualVideoReview']=='approved-for-matting' and qa['manualTemporalReview']=='approved-continuous'
assert alpha['manualReview']=='approved' and alpha['sourceSignature']==qa['sourceSignature']==cycle['sourceSignature']
assert alpha['alphaOutputSignature']==hashlib.sha256(''.join(r['sha256'] for r in job['outputs']).encode()).hexdigest()
assert len(job['outputs'])==len(raw['outputs'])==len(design['sourceFrameOrder'])==124
assert design['sourceFrameOrder']==[r['path'] for r in raw['outputs']]
assert cycle['heroId']==design['heroId'] and cycle['action'] in design['motionSegments']
for r in raw['outputs']+job['outputs']:assert sha(ROOT/r['path'])==r['sha256'],'Reviewed frame changed'
data=json.loads((ROOT/'local_game/street-body-data.js').read_text('utf8').split('=',1)[1].strip().rstrip(';'))
old=next(c for c in data['characters'] if c['id']==design['heroId']);assert cycle['action'] not in old['actions'],'Do not overwrite an existing action'
assert sha(ROOT/'local_game'/old['atlas'])==old['atlasSha256']
begin,end=cycle['sourceCycle'];assert 0<=begin<end<124
assert len(cycle['frameMap'])==cycle['nativeDurationFrames'] and all(begin<=i<=end for i in cycle['frameMap'])
ims=[];boxes=[]
for i in range(begin,end+1):
 im=Image.open(ROOT/raw['outputs'][i]['path']).convert('RGBA');mask=Image.open(ROOT/job['outputs'][i]['path']).getchannel('A').point(lambda v:0 if v<9 else v);im.putalpha(mask)
 box=mask.point(lambda v:255 if v>16 else 0).getbbox();assert box and min(box[0],box[1],512-box[2],512-box[3])>2
 ims.append(im);boxes.append(box)
box=[min(r[0] for r in boxes)-2,min(r[1] for r in boxes)-2,max(r[2] for r in boxes)+2,max(r[3] for r in boxes)+2]
size=[round((box[2]-box[0])*192/max(box[2]-box[0],box[3]-box[1])),round((box[3]-box[1])*192/max(box[2]-box[0],box[3]-box[1]))]
previous=Image.open(ROOT/'local_game'/old['atlas']).convert('RGBA');columns=max(1,previous.width//(size[0]+2));offset=previous.height+2
atlas=Image.new('RGBA',(previous.width,offset+math.ceil(len(ims)/columns)*(size[1]+2)));atlas.paste(previous,(0,0));cfg=copy.deepcopy(old);first=len(cfg['frames'])
for i,im in enumerate(ims):
 tile=im.crop(box).resize(size,Image.Resampling.LANCZOS);x=i%columns*(size[0]+2);y=offset+i//columns*(size[1]+2);atlas.paste(tile,(x,y));cfg['frames'].append(dict(x=x,y=y,w=size[0],h=size[1]))
buf=io.BytesIO();atlas.save(buf,format='WEBP',lossless=True,method=6,exact=True);payload=buf.getvalue();digest=hashlib.sha256(payload).hexdigest();target=b/('candidate-'+digest[:16]+'.webp');target.write_bytes(payload)
decoded=Image.open(target).convert('RGBA');assert decoded.crop((0,0,previous.width,previous.height)).tobytes()==previous.tobytes(),'Existing atlas pixels changed'
seq={'fps':cycle['nativeFps'],'nativeDurationFrames':cycle['nativeDurationFrames'],'frameMap':[first+i-begin for i in cycle['frameMap']],'nativeEvents':[],'nativeImpactFrame':None,'sourceImpactFrame':None,'geometry':{'crop':box,'root':old['root'],'bodyHeight':old['bodyHeight']},'source':b.relative_to(ROOT).as_posix(),'alphaReviewSha256':sha(b/'alpha-qa.json'),'temporalQuality':'approved-continuous','sourceFrameIndices':list(range(begin,end+1))}
cfg['actions'][cycle['action']]=seq;cfg['atlasSha256']=digest
record={'status':'candidate-only-native-audit-and-loop-validation-pending','candidateAtlas':target.relative_to(ROOT).as_posix(),'baseAtlasSha256':old['atlasSha256'],'baseCharacterConfigSha256':hashlib.sha256(json.dumps(old,sort_keys=True).encode()).hexdigest(),'preservedOldAtlasPixels':True,'oldFrameCount':first,'newFrameCount':len(ims),'config':cfg}
(b/'candidate.json').write_text(json.dumps(record,indent=2)+'\n','utf8');print(json.dumps({k:v for k,v in record.items() if k!='config'}))
