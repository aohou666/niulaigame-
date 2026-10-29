"""Structural candidate checks; passing never substitutes for a manual visual review."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'art-migration/generation'
def run():
 candidates=[]
 for folder in sorted(base.iterdir()):
  jobfile=folder/'job.json'
  if not jobfile.exists():continue
  job=json.loads(jobfile.read_text('utf8'))
  if job['status']!='generated-unreviewed' or not (folder/'design.json').exists():continue
  design=json.loads((folder/'design.json').read_text('utf8'))
  if not isinstance(design.get('heroId'),int) or not isinstance(design.get('action'),str):continue
  chosen=next((x for x in job.get('outputs',[]) if '_alpha' in x['path']),None)
  if chosen is None:continue
  image_path=ROOT/chosen['path'];findings=[]
  with Image.open(image_path) as image:
   image=image.convert('RGBA');alpha=image.getchannel('A');bbox=alpha.point(lambda x:255 if x>16 else 0).getbbox()
   if bbox is None:findings.append('empty character')
   elif bbox[0]<4 or bbox[1]<4 or bbox[2]>image.width-4 or bbox[3]>image.height-4:findings.append('silhouette touches frame edge; check cropping')
   if alpha.getextrema()!=(0,255):findings.append('alpha range needs inspection')
   coverage=sum(alpha.histogram()[17:])/(image.width*image.height)
   if coverage<.08 or coverage>.9:findings.append('unusual foreground coverage')
  record={'image':chosen['path'],'sha256':chosen['sha256'],'size':[image.width,image.height],'bbox':bbox,'foregroundFraction':round(coverage,4),'findings':findings,'automaticChecksPassed':not findings,'manualReview':'pending','runtimeIntegrated':False}
  prior=folder/'qa.json'
  if prior.exists():
   previous=json.loads(prior.read_text('utf8'))
   if previous.get('sha256')==record['sha256']:
    record['manualReview']=previous.get('manualReview','pending')
    if 'manualNotes' in previous:record['manualNotes']=previous['manualNotes']
  prior.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
  candidates.append((folder,image_path,record,design))
 font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
 for start in range(0,len(candidates),18):
  canvas=Image.new('RGB',(1200,1080),'#26373c');draw=ImageDraw.Draw(canvas)
  for i,(folder,path,qa,design) in enumerate(candidates[start:start+18]):
   x=(i%6)*200;y=(i//6)*360
   with Image.open(path) as image:
    image=image.convert('RGBA');image.thumbnail((190,300),Image.Resampling.LANCZOS);canvas.paste(image,(x+(200-image.width)//2,y+300-image.height),image)
   draw.text((x+5,y+308),str(design['heroId'])+' '+design['action'],fill='#f5ead6',font=font)
   draw.text((x+5,y+333),'复查边缘' if qa['findings'] else '待人工复查',fill='#ff9c64' if qa['findings'] else '#9fe0c7',font=font)
  canvas.save(ROOT/f'outputs/street-reskin/action-candidates-{start//18+1}.jpg',quality=92)
 summary={'candidates':len(candidates),'automaticPass':sum(not r['findings'] for _,_,r,_ in candidates),'manualApproved':sum(r['manualReview']=='approved' for _,_,r,_ in candidates),'flagged':[(f.name,r['findings']) for f,_,r,_ in candidates if r['findings']]}
 (ROOT/'outputs/street-reskin/candidate-qa-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf8');return summary
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False))
