"""Render every generated body frame for review and compare pose anchors; never auto-approve."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();folder=ROOT/'art-migration/generation'/a.name
job=json.loads((folder/'job.json').read_text('utf8'));design=json.loads((folder/'body-design.json').read_text('utf8'));files=[ROOT/r['path'] for r in job.get('outputs',[])]
if not files:raise SystemExit('No completed video frames')
out=ROOT/'outputs/street-reskin'/a.name;out.mkdir(exist_ok=True)
for start in range(0,len(files),64):
 sheet=Image.new('RGB',(1088,1088),'#17242b');draw=ImageDraw.Draw(sheet)
 for i,path in enumerate(files[start:start+64]):
  with Image.open(path) as im:im=im.convert('RGB');im.thumbnail((132,116));sheet.paste(im,((i%8)*136,(i//8)*136))
  draw.text(((i%8)*136+6,(i//8)*136+119),str(start+i),fill='white')
 sheet.save(out/f'all-frames-{start//64+1}.jpg',quality=94)
chosen=sorted(set([0,len(files)-1]+[round(i*(len(files)-1)/15) for i in range(16)]));sheet=Image.new('RGB',(1024,1024),'#17242b');draw=ImageDraw.Draw(sheet)
for i,index in enumerate(chosen):
 with Image.open(files[index]) as im:im=im.convert('RGB');im.thumbnail((252,230));sheet.paste(im,((i%4)*256,(i//4)*256))
 draw.text(((i%4)*256+6,(i//4)*256+235),str(index),fill='white')
sheet.save(out/'key-frames.jpg',quality=94)
arrays=[];bounds=[];cropped=[];empty=[]
for path in files:
 with Image.open(path) as im:
  rgb=np.asarray(im.convert('RGB'));mask=rgb.max(2)>12;y,x=np.where(mask);box=[int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None;bounds.append(box)
  if box is None:empty.append(len(bounds)-1)
  elif box[0]<4 or box[1]<4 or box[2]>im.width-5 or box[3]>im.height-5:cropped.append(len(bounds)-1)
  arrays.append(np.asarray(im.convert('RGB').resize((128,128)),dtype=np.float32)/255)
anchors={}
for kind in ['attack','skill']:
 with Image.open(ROOT/design['inputs'][kind]['prepared']) as im:reference=np.asarray(im.convert('RGB').resize((128,128)),dtype=np.float32)/255
 begin,end=design['actions'][kind]['sourceFrames'];distances=[float(np.square(arrays[i]-reference).mean()) for i in range(begin,min(end+1,len(arrays)))];closest=begin+min(range(len(distances)),key=distances.__getitem__)
 anchors[kind]={'closestGuidePoseFrame':closest,'requestedGuideFrame':design['actions'][kind]['guideImpactFrame'],'guideDistance':min(distances)}
previous=json.loads((folder/'body-qa.json').read_text('utf8')) if (folder/'body-qa.json').exists() else {}
report={'frames':len(files),'allFramesContactPages':math.ceil(len(files)/64),'poseAnchors':anchors,'bounds':bounds,'croppedFrames':cropped,'emptyFrames':empty,'automaticChecksPassed':not cropped and not empty,'sourceSignature':hashlib.sha256(''.join(r['sha256'] for r in job['outputs']).encode()).hexdigest(),'manualVideoReview':previous.get('manualVideoReview','pending'),'runtimeIntegrated':False}
if 'manualNotes' in previous:report['manualNotes']=previous['manualNotes']
(folder/'body-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({k:v for k,v in report.items() if k!='bounds'}))
