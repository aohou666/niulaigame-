"""Matte one explicitly approved still reference; no animation approval is implied."""
import argparse, hashlib, json, shutil
from street_comfy import ROOT, COMFY, submit
p=argparse.ArgumentParser();p.add_argument('source_job');p.add_argument('--name',required=True);p.add_argument('--skin-code',type=int);a=p.parse_args()
b=ROOT/'art-migration/generation'/a.source_job;qa=json.loads((b/'qa.json').read_text('utf8'));job=json.loads((b/'job.json').read_text('utf8'))
assert qa['manualReview']=='approved' and len(job['outputs'])==1,'Exactly one approved still is required'
row=job['outputs'][0];source=ROOT/qa['image'];assert source.resolve()==(ROOT/row['path']).resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest()==qa['sha256']==row['sha256'],'Source changed after review'
assert not (ROOT/'art-migration/generation'/a.name).exists(),'Poll existing matte job instead of resubmitting'
filename=a.name+'-'+qa['sha256'][:16]+'.png';shutil.copy2(source,COMFY/'input'/filename)
g={'1':{'class_type':'LoadImage','inputs':{'image':filename}},'2':{'class_type':'easy imageRemBg','inputs':{'images':['1',0],'rem_mode':'BEN2','image_output':'Hide','save_prefix':'street-reskin/'+a.name,'add_background':'none','torchscript_jit':False,'refine_foreground':False}},'3':{'class_type':'SaveImage','inputs':{'images':['2',0],'filename_prefix':'street-reskin/'+a.name}}}
f=submit(g,a.name,front=False);(f/'image-design.json').write_text(json.dumps({'skinCode':a.skin_code,'source':row['path'],'sourceSha256':qa['sha256'],'manualSourceReview':(b/'qa.json').relative_to(ROOT).as_posix(),'sourceReviewSha256':hashlib.sha256((b/'qa.json').read_bytes()).hexdigest(),'scope':'single pose reference only','alphaReview':'pending'},indent=2)+'\n','utf8')
