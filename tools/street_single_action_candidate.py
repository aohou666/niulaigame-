"""Generate one explicitly scoped action; never imply a complete character set."""
import argparse, hashlib, json, shutil
from PIL import Image
from street_comfy import ROOT, COMFY, submit
from street_motion_preflight import check_single_gesture

p=argparse.ArgumentParser()
p.add_argument('body_job');p.add_argument('--guide-qa',required=True)
p.add_argument('--revision',required=True,type=int);p.add_argument('--prompt-file',required=True)
p.add_argument('--endpoints-only',action='store_true');p.add_argument('--prepare-only',action='store_true');p.add_argument('--action',choices=['gongji','shouji','paobu'],default='gongji')
a=p.parse_args()
source=ROOT/'art-migration/generation'/a.body_job
design=json.loads((source/'body-design.json').read_text('utf8'));hid=design['heroId']
if a.action=='gongji':check_single_gesture([hid], ROOT/'art-migration/native-action-events.json')
kind={'gongji':'attack','shouji':'hurt','paobu':'run'}[a.action]
name=f'hero{hid:03}-single-{kind}-minimax-v{a.revision}'
assert not (ROOT/'art-migration/generation'/name).exists(),'Poll existing job instead of resubmitting'
qa=json.loads((ROOT/a.guide_qa).read_text('utf8'));guide=ROOT/qa['image']
assert qa['manualReview']=='approved'
assert hashlib.sha256(guide.read_bytes()).hexdigest()==qa['sha256']
idle=ROOT/design['inputs']['idle']['prepared']
assert hashlib.sha256(idle.read_bytes()).hexdigest()==design['inputs']['idle']['sha256']
out=ROOT/'art-migration/references'/name;out.mkdir(parents=True,exist_ok=True)
with Image.open(guide) as im:
 im=im.convert('RGBA');box=im.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();im=im.crop(box)
 subject_height=design['inputs']['idle'].get('subjectHeight',design['inputs']['idle']['size'][1])
 root_x,root_y=design['inputs']['idle']['foot']
 scale=min(subject_height/im.height,560/im.width);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',(768,768));foot=im.getchannel('A').crop((0,int(im.height*.88),im.width,im.height));pixels=list(foot.getdata());anchor=sum((i%im.width)*v for i,v in enumerate(pixels))/max(1,sum(pixels))
 x=round(root_x-anchor);y=round(root_y-im.height);assert x>=12 and y>=12 and x+im.width<=756 and y+im.height<=756,'Shared scale/root cannot fit guide safely'
 canvas.alpha_composite(im,(x,y));canvas.save(out/(kind+'.png'))
g=json.loads((source/'workflow.json').read_text('utf8'))
for node in list(g):
 if node in ['6','9','10'] or int(node)>=21:del g[node]
for node,path,input_kind in [('4',idle,'idle'),('5',out/(kind+'.png'),kind)]:
 filename=name+'-'+input_kind+'.png';shutil.copy2(path,COMFY/'input'/filename);g[node]['inputs']['image']=filename
g['7']['inputs']['length']=124;g['7']['inputs']['first_frame']=['4',0];g['7']['inputs']['last_frame']=['4',0]
g['7']['inputs']['prompt']=(ROOT/a.prompt_file).read_text('utf8')
g['8']['inputs']['positive']=['7',0];g['8']['inputs']['frame_idx']=62;g['8']['inputs']['image']=['5',0]
g['13']['inputs']['conditioning']=['8',0]
if a.endpoints_only:
 g['13']['inputs']['conditioning']=['7',0];g.pop('8',None)
if a.action=='paobu':
 g['7']['inputs']['first_frame']=['5',0];g['7']['inputs']['last_frame']=['5',0];g['13']['inputs']['conditioning']=['7',0];g.pop('8',None)
g['14']['inputs']['noise_seed']=202610300000+hid+a.revision*1000
g['18']['inputs']['filename_prefix']='street-reskin/'+name;g['20']['inputs']['filename_prefix']='street-reskin/'+name+'-video'
(out/'workflow.json').write_text(json.dumps(g,indent=2),'utf8')
record={'heroId':hid,'length':124,'scope':a.action+' only; other actions not generated or approved','inputs':{'idle':design['inputs']['idle'],kind:{'source':qa['image'],'prepared':(out/(kind+'.png')).relative_to(ROOT).as_posix(),'sourceSha256':qa['sha256'],'sha256':hashlib.sha256((out/(kind+'.png')).read_bytes()).hexdigest(),'size':list(im.size),'foot':[root_x,root_y],'normalization':'same subject height and foot anchor as idle'}},'motionSegments':{a.action:[0,123]},'conditioningMode':'endpoints-only' if a.endpoints_only or a.action=='paobu' else 'midpoint-guide','loopRequired':a.action=='paobu','manualVideoReview':'pending','runtimeIntegrated':False}
(out/'action-design.json').write_text(json.dumps(record,indent=2),'utf8')
if not a.prepare_only:
 folder=submit(g,name,front=False);shutil.copy2(out/'action-design.json',folder/'action-design.json')
print(json.dumps({'name':name,'submitted':not a.prepare_only,'prepared':str(out)}))
