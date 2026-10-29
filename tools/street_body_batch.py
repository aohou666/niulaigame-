"""Generate motion only from manually reviewed identity poses. No automatic art approval."""
import argparse,hashlib,json,re,shutil
from pathlib import Path
from PIL import Image
from street_comfy import ROOT,COMFY,submit
from street_motion_preflight import check_single_gesture
from street_multihit_plan import validate as validate_choreography, apply_choreography
p=argparse.ArgumentParser();p.add_argument('ids',nargs='+',type=int);p.add_argument('--revision',type=int,default=1);p.add_argument('--height',type=int,default=560);p.add_argument('--root-y',type=int,default=700);p.add_argument('--length',type=int,choices=[73,124],default=73);p.add_argument('--base-steps',type=int,choices=[16,24,32]);p.add_argument('--landmarks',type=Path);p.add_argument('--idle-reference-qa',type=Path);p.add_argument('--choreography',type=Path);guides=p.add_mutually_exclusive_group();guides.add_argument('--dense-guides',action='store_true');guides.add_argument('--sparse-guides',action='store_true');p.add_argument('--queue-tail',action='store_true');p.add_argument('--retain-lit-prop',action='store_true');a=p.parse_args()
assert 550<=a.root_y<=700, 'Root must retain top and bottom safety margins'
assert a.length==73 or a.sparse_guides,'Longer trained-range pilot uses sparse guides only'
base=ROOT/'art-migration/generation'
choreography=json.loads(a.choreography.read_text('utf8')) if a.choreography else None
if choreography:
 assert a.ids==[choreography['heroId']] and a.length==choreography['length'] and a.sparse_guides
 validate_choreography(choreography,json.loads((ROOT/'art-migration/native-action-events.json').read_text('utf8')))
 assert choreography.get('status')=='ready-for-generation', 'Choreography still awaits reviewed guides'
else:
 check_single_gesture(a.ids, ROOT/'art-migration/native-action-events.json')
plan=json.loads((ROOT/'outputs/combat-action-plan-20261022/combat-action-plan.json').read_text('utf8'))['rows']
template=json.loads((base/'hero001-body-actions-minimax-v3-fastdecode/workflow.json').read_text('utf8'))
overrides=json.loads((ROOT/'art-migration/prop-continuity-overrides.json').read_text('utf8'))
landmarks=json.loads(a.landmarks.read_text('utf8')) if a.landmarks else None
idleReference=None
if a.idle_reference_qa:
 reference=json.loads(a.idle_reference_qa.read_text('utf8'))
 assert len(a.ids)==1 and reference['heroId']==a.ids[0], 'Reference must belong to this one character'
 assert reference['manualReview']=='approved', 'Reference requires visual approval'
 idleReference=ROOT/reference['image']
 assert hashlib.sha256(idleReference.read_bytes()).hexdigest()==reference['sha256'], 'Reference changed after review'
def normalize(source,out,name,hid):
 if landmarks:
  assert landmarks['heroId']==hid,'Landmarks belong to one manually inspected character only'
  mark=landmarks['poses'][name];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==mark['sourceSha256'],'Landmarks are bound to the exact inspected pose image'
  with Image.open(source) as original:
   image=original.convert('RGBA');box=image.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();image=image.crop(box)
   rootX=landmarks['rootX'];footX=mark['footX']-box[0];footY=mark['footY']-box[1];subjectHeight=mark['footY']-mark['headY'];assert subjectHeight>0
   scale=min(a.height/subjectHeight,(rootX-20)/max(1,footX),(748-rootX)/max(1,image.width-footX),(a.root_y-20)/max(1,footY),(748-a.root_y)/max(1,image.height-footY))
   image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
   x=round(rootX-footX*scale);y=round(a.root_y-footY*scale);assert x>=18 and y>=18 and x+image.width<=750 and y+image.height<=750
   canvas=Image.new('RGBA',(768,768));canvas.alpha_composite(image,(x,y));target=out/(name+'.png');canvas.save(target)
   inputname=f'street_body{hid:03}_{name}_v{a.revision}.png';shutil.copy2(target,COMFY/'input'/inputname)
   return inputname,{'source':source.relative_to(ROOT).as_posix(),'prepared':target.relative_to(ROOT).as_posix(),'sourceSha256':digest,'foot':[rootX,a.root_y],'size':image.size,'subjectHeight':round(subjectHeight*scale,3),'normalization':'manually inspected head/feet landmarks; full prop bbox retained','sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
 with Image.open(source) as image:
  image=image.convert('RGBA');box=image.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();image=image.crop(box)
  scale=min(normalHeight/image.height,560/image.width);image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
  foot=image.getchannel('A').crop((0,int(image.height*.88),image.width,image.height));pixels=list(foot.getdata());anchor=sum((i%image.width)*v for i,v in enumerate(pixels))/max(1,sum(pixels))
  x=max(12,min(756-image.width,round(384-anchor)));canvas=Image.new('RGBA',(768,768));canvas.alpha_composite(image,(x,a.root_y-image.height));target=out/(name+'.png');canvas.save(target)
  inputname=f'street_body{hid:03}_{name}_v{a.revision}.png';shutil.copy2(target,COMFY/'input'/inputname)
  return inputname,{'source':source.relative_to(ROOT).as_posix(),'prepared':target.relative_to(ROOT).as_posix(),'foot':[round(x+anchor,2),a.root_y],'size':image.size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
for hid in reversed(a.ids):
 name=f'hero{hid:03}-body-actions-minimax-v{a.revision}'
 if (base/name).exists():continue
 poses={};rows={kind:next(r for r in plan if r['heroId']==hid and r['slot']==slot) for kind,slot in [('attack','普攻'),('skill','大招')]}
 for kind in ['attack','skill']:
  candidates=sorted(base.glob(f'hero{hid:03}-{kind}-v*'),key=lambda f:int(re.search(r'-v(\d+)',f.name).group(1)),reverse=True)
  folder=next((f for f in candidates if (f/'qa.json').exists() and json.loads((f/'qa.json').read_text('utf8'))['manualReview']=='approved'),None)
  if not folder:raise RuntimeError(f'{hid} {kind} has no manually approved pose')
  poses[kind]=ROOT/json.loads((folder/'qa.json').read_text('utf8'))['image']
 out=ROOT/(f'art-migration/references/body-{hid:03}'+(f'-v{a.revision}' if a.revision>1 else ''));out.mkdir(parents=True,exist_ok=True)
 inputs={};files={}
 sourceImages={'idle':idleReference or ROOT/f'local_game/assets/street/characters/{hid:03}/portrait.png',**poses};limits=[]
 for sourceImage in sourceImages.values():
  with Image.open(sourceImage) as image:
   box=image.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();limits.append(560*(box[3]-box[1])/(box[2]-box[0]))
 normalHeight=min(a.height,*limits)
 for kind,source in sourceImages.items():files[kind],inputs[kind]=normalize(source,out,kind,hid)
 if landmarks:
  heights=[r['subjectHeight'] for r in inputs.values()];assert max(heights)-min(heights)<1.5,'Full prop margins would rescale actors differently; lower shared --height before submission'
 if str(hid) in overrides:
  actual=overrides[str(hid)]
  for kind in rows:rows[kind]=dict(rows[kind],bodyDesign=actual[kind],weaponObservation=actual['prop'])
 else:raise RuntimeError(f'{hid} needs individually observed physical action/prop overrides before new generation')
 for kind in rows:
  assert not any(text in rows[kind]['bodyDesign'] for text in ['蓄能','释放能量','能量收束','待立绘核对']),'Body action description still contains an unreviewed effect/placeholder instruction'
 split,peakA,peakB=(36,16,54) if a.length==73 else (62,28,92)
 prompt=f'''One locked-camera studio rehearsal showing the EXACT single costumed character in the reference images. Same face, horns, hair, outfit, fabric, colors, anatomy and all original held objects in every frame. Tactile 2.5D semi-realistic semi-cartoon absurd neighborhood production style. Entire character, head, hands, feet, tail and complete objects remain fully visible with safe blank margins. Matte black featureless studio background and constant soft neutral illumination.
 Two physical pantomime exercises, each performed ONCE through natural intermediate joint positions. Exercise A, frames0-{split-1}: start in the relaxed reference posture, prepare the movement, reach the second reference posture near frame{peakA}, then recover continuously to the relaxed posture by frame{split}. Exact physical movement: {rows['attack']['bodyDesign']}. Observed real objects and hand assignment: {rows['attack']['weaponObservation']}.
 Exercise B, frames{split}-{a.length-1}: start relaxed, prepare and perform this distinct physical gesture, reach the third reference posture near frame{peakB}, then recover to the original relaxed posture by frame{a.length-1}. Exact physical movement: {rows['skill']['bodyDesign']}. Observed objects: {rows['skill']['weaponObservation']}.
 Keep both feet/root in their original location. Animate grounded knees, shoulders, elbows and wrists with natural cloth follow-through. Maintain one coherent body and constant object lengths/hand assignments. Crisp clean silhouette and continuous movement through preparation, extension and recovery; only a brief natural pause. No walking, sliding, zoom, camera movement, duplicated anatomy, invented objects, secondary light effects, streaks, particles, sparks, motion-blur shapes or backdrop changes. This is a quiet physical studio rehearsal, with only the original character and physical costume/objects visible.'''
 if a.retain_lit_prop:
  assert hid==83,'Only83 has a manually reviewed luminous orb as part of its persistent identity'
  prompt+=' Preserve the ONE existing luminous fire orb continuously in the original RIGHT palm; LEFT palm may support this same orb. Preserve original warm core/rim and costume mane/tail tip. This existing held identity object must never be extinguished, multiplied, thrown or detached. No extra light shapes or second orb.'
 g=json.loads(json.dumps(template));g['4']['inputs']['image']=files['idle'];g['5']['inputs']['image']=files['attack'];g['6']['inputs']['image']=files['skill'];g['7']['inputs']['prompt']=prompt
 if a.base_steps:
  g['19']['inputs']['model']=['1',0];del g['11'];g['12']['inputs']['steps']=a.base_steps
 g['14']['inputs']['noise_seed']=202610290000+hid;g['18']['inputs']['filename_prefix']=f'street-reskin/hero{hid:03}_body';g['20']['inputs']['filename_prefix']=f'street-reskin/hero{hid:03}_body_video'
 g['14']['inputs']['noise_seed']+=a.revision*10000
 for node,positive,frame,image in [('21','7',8,'idle'),('22','8',24,'attack'),('23','22',30,'idle'),('24','9',44,'idle'),('25','10',62,'skill'),('26','25',68,'idle')]:
  g[node]={'class_type':'MiniMaxH3AddGuide','inputs':{'positive':[positive,0],'latent':['7',1],'frame_idx':frame,'vae':['3',0],'image':[{'idle':'4','attack':'5','skill':'6'}[image],0]}}
 g['8']['inputs']['positive']=['21',0];g['9']['inputs']['positive']=['23',0];g['10']['inputs']['positive']=['24',0];g['13']['inputs']['conditioning']=['26',0]
 if a.dense_guides:
  # Keep persistent two-hand props constrained through every latent interval.
  # MiniMax still synthesizes all73 frames; this is guide conditioning, not a still-frame montage.
  prior='7';guideSchedule=[]
  for n,frame in enumerate(range(4,73,4),100):
   kind='attack' if 12<=frame<=24 else 'skill' if 48<=frame<=64 else 'idle';node=str(n)
   g[node]={'class_type':'MiniMaxH3AddGuide','inputs':{'positive':[prior,0],'latent':['7',1],'frame_idx':frame,'vae':['3',0],'image':[{'idle':'4','attack':'5','skill':'6'}[kind],0]}};prior=node;guideSchedule.append({'frame':frame,'image':kind})
  g['13']['inputs']['conditioning']=[prior,0]
 if a.sparse_guides:
  # First/last plus attack, recovery, skill only. Dense references were observed
  # to freeze almost every temporal token and produce pose jumps, not motion.
  for node,previous in [('8','7'),('9','8'),('10','9')]:g[node]['inputs']['positive']=[previous,0]
  g['13']['inputs']['conditioning']=['10',0]
  for node in list(g):
   if int(node)>=21:del g[node]
  g['7']['inputs']['prompt']+=' Every transition must be continuously animated through intermediate anatomy. Never cut, dissolve, teleport or switch instantly between held reference stills. Show anticipation, extension, follow-through and continuous recovery for each action.'
  if a.length==124:
   g['7']['inputs']['length']=124
   for node,frame in [('8',28),('9',62),('10',92)]:g[node]['inputs']['frame_idx']=frame
   g['7']['inputs']['prompt']+=' Both actions face viewer RIGHT only. Never turn or strike toward viewer LEFT. Anticipation is a small backward elbow/body compression, never a mirrored opposite-facing reference pose. No second face, no blended duplicate eyes, horns or muzzle.'
 if choreography:g=apply_choreography(g,choreography,rows)
 folder=submit(g,name,front=not a.queue_tail)
 (folder/'body-design.json').write_text(json.dumps({'heroId':hid,'inputs':inputs,'actions':{k:{'sourceFrames':([0,35] if k=='attack' else [36,72]) if a.length==73 else ([0,61] if k=='attack' else [62,123]),'guideImpactFrame':(16 if k=='attack' else 54) if a.length==73 else (28 if k=='attack' else 92),'native':rows[k]} for k in rows},'length':a.length,'nativeClockMustBeRetained':True,'manualVideoReview':'pending','runtimeIntegrated':False},ensure_ascii=False,indent=2),'utf8')
 if a.dense_guides:
  file=folder/'body-design.json';record=json.loads(file.read_text('utf8'));record['denseGuideSchedule']=guideSchedule;file.write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
 if a.sparse_guides:
  file=folder/'body-design.json';record=json.loads(file.read_text('utf8'));schedule=[(0,'idle'),(16,'attack'),(36,'idle'),(54,'skill'),(72,'idle')] if a.length==73 else [(0,'idle'),(28,'attack'),(62,'idle'),(92,'skill'),(123,'idle')];record['sparseGuideSchedule']=[{'frame':n,'image':k} for n,k in schedule];record['temporalReviewRequired']=True;file.write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')

 if choreography:
  file=folder/'body-design.json';record=json.loads(file.read_text('utf8'));record['choreography']=choreography;record['sparseGuideSchedule']=choreography['guideSchedule'];record['choreographyVisualReviewRequired']=True;file.write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
