"""Prepare an explicitly scoped independent-skin action, never a base-hero replacement."""
import argparse, hashlib, json, shutil
from PIL import Image
from street_comfy import ROOT, COMFY, submit

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text('utf8'))
p=argparse.ArgumentParser();p.add_argument('--skin-code',type=int,required=True);p.add_argument('--action',choices=['gongji','jineng'],required=True);p.add_argument('--guide-qa',required=True);p.add_argument('--prompt-file',required=True);p.add_argument('--revision',type=int,required=True);a=p.parse_args()
assert a.skin_code==100201,'Other skins require their own native/reference inventory'
name=f'skin{a.skin_code}-{a.action}-minimax-v{a.revision}'
assert not (ROOT/'art-migration/generation'/name).exists(),'Collect existing job instead'
qa_path=ROOT/a.guide_qa;qa=read(qa_path);guide=ROOT/qa['image'];assert qa['manualReview']=='approved' and sha(guide)==qa['sha256']
idle_design=read(ROOT/'art-migration/generation/skin100201-idle-minimax-v3/idle-design.json');idle=ROOT/idle_design['inputs']['idle']['prepared'];assert sha(idle)==idle_design['inputs']['idle']['sha256']
native_path=ROOT/'art-migration/skin-migration/100201/native-events.json';native=read(native_path);rows=[r for r in native['records'] if r['action']==a.action];assert len(rows)==2
assert {r['durationFrames'] for r in rows}=={45 if a.action=='gongji' else 46}
if a.action=='gongji':assert all(len(r['events'])==1 and r['events'][0]['frame0']==18 for r in rows)
out=ROOT/'art-migration/references'/name;out.mkdir(parents=True,exist_ok=False)
with Image.open(guide) as image:
 image=image.convert('RGBA');box=image.getchannel('A').point(lambda v:255 if v>64 else 0).getbbox();image=image.crop(box)
 # The wheel is the shared root. Preserve rider height and the idle foot anchor.
 height=idle_design['inputs']['idle']['size'][1];root=idle_design['inputs']['idle']['foot'];scale=min(height/image.height,600/image.width)
 image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
 alpha=image.getchannel('A');bottom=alpha.crop((0,int(image.height*.9),image.width,image.height));values=list(bottom.getdata());anchor=sum((i%image.width)*v for i,v in enumerate(values))/max(1,sum(values))
 x=round(root[0]-anchor);y=round(root[1]-image.height);assert x>=12 and y>=12 and x+image.width<=756
 canvas=Image.new('RGBA',(768,768));canvas.alpha_composite(image,(x,y));prepared=out/'guide.png';canvas.save(prepared)
g=read(ROOT/'art-migration/generation/skin100201-idle-minimax-v3/workflow.json')
for node,file,kind in [('4',idle,'idle'),('5',prepared,'guide')]:
 filename=name+'-'+kind+'.png';shutil.copy2(file,COMFY/'input'/filename);g[node]={'class_type':'LoadImage','inputs':{'image':filename}}
g['7']['inputs'].update(prompt=(ROOT/a.prompt_file).read_text('utf8'),last_frame=['4',0])
guide_frame=50 if a.action=='gongji' else 62
g['8']={'class_type':'MiniMaxH3AddGuide','inputs':{'positive':['7',0],'latent':['7',1],'frame_idx':guide_frame,'vae':['3',0],'image':['5',0]}}
g['13']['inputs']['conditioning']=['8',0];g['14']['inputs']['noise_seed']=20261030100201+a.revision*100+(a.action=='jineng')
g['18']['inputs']['filename_prefix']='street-reskin/'+name;g['20']['inputs']['filename_prefix']='street-reskin/'+name+'-video'
record={'heroId':2,'skinCode':a.skin_code,'models':[r['model'] for r in rows],'length':124,'scope':a.action+' only; independent skin, not base hero','motionSegments':{a.action:[0,123]},'inputs':{'idle':idle_design['inputs']['idle'],'guide':{'source':qa['image'],'sourceSha256':qa['sha256'],'prepared':prepared.relative_to(ROOT).as_posix(),'sha256':sha(prepared)}},'nativeAuditPath':native_path.relative_to(ROOT).as_posix(),'nativeAuditSha256':sha(native_path),'nativeFrames':rows[0]['durationFrames'],'nativeEvents':rows[0]['events'],'guideFrame':guide_frame,'conditioningMode':'idle endpoints with action guide','manualVideoReview':'pending','runtimeIntegrated':False}
folder=submit(g,name,front=False);(folder/'action-design.json').write_text(json.dumps(record,indent=2)+'\n','utf8');print(json.dumps({'name':name,'scope':record['scope'],'guideFrame':guide_frame}))
