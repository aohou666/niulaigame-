"""Generate motion only from manually reviewed identity poses. No automatic art approval."""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image
from street_comfy import ROOT,COMFY,submit
p=argparse.ArgumentParser();p.add_argument('ids',nargs='+',type=int);p.add_argument('--revision',type=int,default=1);p.add_argument('--height',type=int,default=560);p.add_argument('--length',type=int,choices=[73,124],default=73);p.add_argument('--base-steps',type=int,choices=[16,24,32]);guides=p.add_mutually_exclusive_group();guides.add_argument('--dense-guides',action='store_true');guides.add_argument('--sparse-guides',action='store_true');p.add_argument('--queue-tail',action='store_true');p.add_argument('--retain-lit-prop',action='store_true');a=p.parse_args()
assert a.length==73 or a.sparse_guides,'Longer trained-range pilot uses sparse guides only'
base=ROOT/'art-migration/generation'
plan=json.loads((ROOT/'outputs/combat-action-plan-20261022/combat-action-plan.json').read_text('utf8'))['rows']
template=json.loads((base/'hero001-body-actions-minimax-v3-fastdecode/workflow.json').read_text('utf8'))
overrides=json.loads((ROOT/'art-migration/prop-continuity-overrides.json').read_text('utf8'))
def normalize(source,out,name,hid):
 with Image.open(source) as image:
  image=image.convert('RGBA');box=image.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();image=image.crop(box)
  scale=min(normalHeight/image.height,560/image.width);image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
  foot=image.getchannel('A').crop((0,int(image.height*.88),image.width,image.height));pixels=list(foot.getdata());anchor=sum((i%image.width)*v for i,v in enumerate(pixels))/max(1,sum(pixels))
  x=max(12,min(756-image.width,round(384-anchor)));canvas=Image.new('RGBA',(768,768));canvas.alpha_composite(image,(x,700-image.height));target=out/(name+'.png');canvas.save(target)
  inputname=f'street_body{hid:03}_{name}_v{a.revision}.png';shutil.copy2(target,COMFY/'input'/inputname)
  return inputname,{'source':source.relative_to(ROOT).as_posix(),'prepared':target.relative_to(ROOT).as_posix(),'foot':[round(x+anchor,2),700],'size':image.size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
for hid in reversed(a.ids):
 name=f'hero{hid:03}-body-actions-minimax-v{a.revision}'
 if (base/name).exists():continue
 poses={};rows={kind:next(r for r in plan if r['heroId']==hid and r['slot']==slot) for kind,slot in [('attack','普攻'),('skill','大招')]}
 for kind in ['attack','skill']:
  candidates=sorted(base.glob(f'hero{hid:03}-{kind}-v*'),reverse=True)
  folder=next((f for f in candidates if (f/'qa.json').exists() and json.loads((f/'qa.json').read_text('utf8'))['manualReview']=='approved'),None)
  if not folder:raise RuntimeError(f'{hid} {kind} has no manually approved pose')
  poses[kind]=ROOT/json.loads((folder/'qa.json').read_text('utf8'))['image']
 out=ROOT/(f'art-migration/references/body-{hid:03}'+(f'-v{a.revision}' if a.revision>1 else ''));out.mkdir(parents=True,exist_ok=True)
 inputs={};files={}
 sourceImages={'idle':ROOT/f'local_game/assets/street/characters/{hid:03}/portrait.png',**poses};limits=[]
 for sourceImage in sourceImages.values():
  with Image.open(sourceImage) as image:
   box=image.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();limits.append(560*(box[3]-box[1])/(box[2]-box[0]))
 normalHeight=min(a.height,*limits)
 for kind,source in sourceImages.items():files[kind],inputs[kind]=normalize(source,out,kind,hid)
 if str(hid) in overrides:
  actual=overrides[str(hid)]
  for kind in rows:rows[kind]=dict(rows[kind],bodyDesign=actual[kind],weaponObservation=actual['prop'])
 prompt=f'''One fixed-camera production sprite animation of the EXACT character shown in the guide images. Same identity, face, horns, hair, outfit, colors, anatomy and ALL held props throughout. Premium tactile 2.5D semi-realistic semi-cartoon absurd neighborhood game style. Full body, head, feet and weapon visible with generous safe margins on all sides. Pure black featureless background. No camera movement, no environment, no other person, no duplicate limbs, no invented weapon, no VFX; never lose a held prop.
 The three-second clip has exactly TWO separate coherent actions. Frames0-35: start in provided idle, perform ONE normal attack matching the attack guide around frame16, smoothly recover to idle at frame36. Normal action intent: {rows['attack']['bodyDesign']}; prop/body observation: {rows['attack']['weaponObservation']}. Frames36-72: perform ONE distinct special-skill gesture matching the skill guide around frame54, recover to original idle by frame72. Skill physical movement: {rows['skill']['bodyDesign']}; actual prop observation: {rows['skill']['weaponObservation']}. Respect the provided props: if playing an instrument, animate playing it; if casting or supporting, animate the gesture rather than inventing a melee punch. No repeated attacks. The game handles travel separately: keep foot/root position fixed; no walking, sliding, or body scale drift. Natural shoulder/elbow mechanics and cloth follow-through; crisp readable silhouette without motion blur.'''
 prompt+='\nThis is a NONMAGICAL motion-capture rehearsal of body mechanics only. The separate game layer renders all energy. No visible light, flame, smoke, particles, slash trail, shockwave, glow, energy ball or secondary animation may appear. Maintain physical props at constant length. After reaching each guide pose, HOLD it briefly and then recover exactly to idle; do not add a second strike. Movements stay inside central70% of the canvas.'
 if a.retain_lit_prop:
  assert hid==83,'Only83 has a manually reviewed luminous orb as part of its persistent identity'
  prompt=prompt.replace('This is a NONMAGICAL motion-capture rehearsal of body mechanics only. The separate game layer renders all energy. No visible light, flame, smoke, particles, slash trail, shockwave, glow, energy ball or secondary animation may appear.','This is a physical rehearsal without added combat effects. Preserve the ONE existing luminous fire orb continuously in the original RIGHT palm; LEFT palm may support it in the attack guide. Preserve its original warm core/rim and the original costume mane/tail-tip appearance. The held reference orb is an identity prop, not an outgoing attack effect. Never extinguish, multiply, throw or detach this existing orb. Do not add beams, trails, smoke, particles, flashes, explosions or any second orb.')
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
   g['7']['inputs']['prompt']=g['7']['inputs']['prompt'].replace('three-second','five-second').replace('Frames0-35','Frames0-61').replace('frame16','frame28').replace('frame36','frame62').replace('Frames36-72','Frames62-123').replace('frame54','frame92').replace('frame72','frame123')
   for node,frame in [('8',28),('9',62),('10',92)]:g[node]['inputs']['frame_idx']=frame
   g['7']['inputs']['prompt']+=' Both actions face viewer RIGHT only. Never turn or strike toward viewer LEFT. Anticipation is a small backward elbow/body compression, never a mirrored opposite-facing reference pose. No second face, no blended duplicate eyes, horns or muzzle.'
 folder=submit(g,name,front=not a.queue_tail)
 (folder/'body-design.json').write_text(json.dumps({'heroId':hid,'inputs':inputs,'actions':{k:{'sourceFrames':([0,35] if k=='attack' else [36,72]) if a.length==73 else ([0,61] if k=='attack' else [62,123]),'guideImpactFrame':(16 if k=='attack' else 54) if a.length==73 else (28 if k=='attack' else 92),'native':rows[k]} for k in rows},'length':a.length,'nativeClockMustBeRetained':True,'manualVideoReview':'pending','runtimeIntegrated':False},ensure_ascii=False,indent=2),'utf8')
 if a.dense_guides:
  file=folder/'body-design.json';record=json.loads(file.read_text('utf8'));record['denseGuideSchedule']=guideSchedule;file.write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
 if a.sparse_guides:
  file=folder/'body-design.json';record=json.loads(file.read_text('utf8'));schedule=[(0,'idle'),(16,'attack'),(36,'idle'),(54,'skill'),(72,'idle')] if a.length==73 else [(0,'idle'),(28,'attack'),(62,'idle'),(92,'skill'),(123,'idle')];record['sparseGuideSchedule']=[{'frame':n,'image':k} for n,k in schedule];record['temporalReviewRequired']=True;file.write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
