"""Contact every generated VFX frame and record bounds/brightness, no automatic approval."""
import argparse,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();folder=ROOT/'art-migration/generation'/a.name;job=json.loads((folder/'job.json').read_text('utf8'));images=[Image.open(ROOT/r['path']).convert('RGB') for r in job.get('outputs',[])];assert images,'No generated frames';out=ROOT/'outputs/street-reskin'/a.name;out.mkdir(exist_ok=True)
for label,indices,col,tw,th in [('all-1',range(min(64,len(images))),8,136,136),('all-2',range(64,len(images)),8,136,136),('large',[round(i*(len(images)-1)/15) for i in range(16)],4,256,256)]:
 indices=list(indices)
 if not indices:continue
 sheet=Image.new('RGB',(col*tw,math.ceil(len(indices)/col)*th),'#263c43');draw=ImageDraw.Draw(sheet)
 for j,n in enumerate(indices):
  im=images[n].copy();im.thumbnail((tw-4,th-22));sheet.paste(im,(j%col*tw,j//col*th));draw.text((j%col*tw+4,(j//col+1)*th-18),str(n),fill='white')
 sheet.save(out/(label+'.jpg'),quality=95)
energy=[];bounds=[];cropped=[]
for i,im in enumerate(images):
 arr=np.array(im);energy.append(float(arr.mean()));yy,xx=np.where(arr.max(2)>24);box=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1] if len(xx) else None;bounds.append(box)
 if box and min(box[0],box[1],im.width-box[2],im.height-box[3])<4:cropped.append(i)
previous=json.loads((folder/'effect-qa.json').read_text('utf8')) if (folder/'effect-qa.json').exists() else {};d={'frames':len(images),'energy':energy,'bounds':bounds,'croppedFrames':cropped,'peakFrame':max(range(len(energy)),key=energy.__getitem__),'endpointMeanAbsoluteDifference':float(np.abs(np.asarray(images[0],dtype=float)-np.asarray(images[-1],dtype=float)).mean()),'manualReview':previous.get('manualReview','pending'),'runtimeIntegrated':previous.get('runtimeIntegrated',False)}
if 'manualNotes' in previous:d['manualNotes']=previous['manualNotes']
(folder/'effect-qa.json').write_text(json.dumps(d,indent=2)+'\n','utf8');print(json.dumps({k:v for k,v in d.items() if k not in ['energy','bounds']}))
