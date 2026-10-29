"""Pack reviewed real idle frames into a candidate directory, without runtime writes."""
import argparse,hashlib,io,json,math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
folder=ROOT/'art-migration/generation'/a.name
job=json.loads((folder/'job.json').read_text('utf8'))
design=json.loads((folder/'idle-design.json').read_text('utf8'))
review=json.loads((folder/'alpha-qa.json').read_text('utf8'))
assert review['manualReview']=='approved'
assert review['alphaOutputSignature']==hashlib.sha256(''.join(r['sha256'] for r in job['outputs']).encode()).hexdigest()
source=ROOT/design['sourceBodyJob']
sourcejob=json.loads((source/'job.json').read_text('utf8'))
sourceqa=json.loads((source/'body-qa.json').read_text('utf8'))
assert sourceqa['manualVideoReview']=='approved-for-matting'
assert review['sourceSignature']==sourceqa['sourceSignature']
assert design['sourceFrameOrder']==[r['path'] for r in sourcejob['outputs']]
assert len(job['outputs'])==len(design['sourceFrameOrder'])==design['length']
frames=[];bounds=[]
for raw,alpha in zip(sourcejob['outputs'],job['outputs']):
    for entry in (raw,alpha):
        assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256']
    im=Image.open(ROOT/raw['path']).convert('RGB').convert('RGBA')
    im.putalpha(Image.open(ROOT/alpha['path']).getchannel('A').point(lambda x:0 if x<9 else x))
    box=im.getchannel('A').point(lambda x:255 if x>16 else 0).getbbox()
    assert box and min(box[0],box[1],im.width-box[2],im.height-box[3])>2
    frames.append(im);bounds.append(box)
box=[min(b[0] for b in bounds)-2,min(b[1] for b in bounds)-2,
     max(b[2] for b in bounds)+2,max(b[3] for b in bounds)+2]
w,h=box[2]-box[0],box[3]-box[1]
out=ROOT/'outputs/street-reskin'/a.name/'candidate-pack';out.mkdir(parents=True,exist_ok=True)
fallback=[]
for frame in frames:
    buf=io.BytesIO();frame.save(buf,format='PNG')
    payload=buf.getvalue();sha=hashlib.sha256(payload).hexdigest();name=f'frame-{sha[:16]}.png'
    (out/name).write_bytes(payload)
    fallback.append({'file':name,'sha256':sha,'bytes':len(payload)})
profiles={}
for profile,edge in [('detail',384),('battle',192)]:
    scale=min(1,edge/max(w,h));fw,fh=round(w*scale),round(h*scale)
    tw,th=fw+4,fh+4;cols=max(1,1024//tw);per=cols*max(1,2048//th)
    pages=[];rects=[]
    for start in range(0,len(frames),per):
        subset=frames[start:start+per]
        atlas=Image.new('RGBA',(min(cols,len(subset))*tw,math.ceil(len(subset)/cols)*th))
        for i,frame in enumerate(subset):
            x,y=i%cols*tw+2,i//cols*th+2
            atlas.paste(frame.crop(box).resize((fw,fh),Image.Resampling.LANCZOS),(x,y))
            rects.append({'page':len(pages),'x':x,'y':y,'w':fw,'h':fh})
        buf=io.BytesIO();atlas.save(buf,format='WEBP',lossless=True,method=6)
        payload=buf.getvalue();sha=hashlib.sha256(payload).hexdigest();name=f'{profile}-{sha[:16]}.webp'
        (out/name).write_bytes(payload)
        pages.append({'file':name,'width':atlas.width,'height':atlas.height,'bytes':len(payload),'sha256':sha})
    profiles[profile]={'pages':pages,'frames':rects}
rgb=[np.asarray(im.convert('RGB').resize((128,128)),dtype=np.float32) for im in frames]
deltas=[float(np.abs(y-x).mean()) for x,y in zip(rgb,rgb[1:])]
report={'heroId':design['heroId'],'frameCount':len(frames),'crop':[box[0],box[1],w,h],
        'profiles':profiles,'fallback':fallback,'sourceSignature':review['sourceSignature'],
        'alphaOutputSignature':review['alphaOutputSignature'],'runtimeIntegrated':False,
        'loopSeamScreening':{'lastToFirstMeanRgbDelta':float(np.abs(rgb[-1]-rgb[0]).mean()),
                             'largestAdjacentMeanRgbDelta':max(deltas),
                             'note':'Diagnostic only; visual looping/runtime review still required'}}
(out/'candidate.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps({'candidate':str(out),'frames':len(frames),'pages':sum(len(v['pages']) for v in profiles.values()),'seam':report['loopSeamScreening']}))
