"""Generate motion only from manually reviewed identity poses. No automatic art approval."""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image
from street_comfy import ROOT,COMFY,submit
p=argparse.ArgumentParser();p.add_argument('ids',nargs='+',type=int);p.add_argument('--revision',type=int,default=1);p.add_argument('--height',type=int,default=620);a=p.parse_args()
base=ROOT/'art-migration/generation'
plan=json.loads((ROOT/'outputs/combat-action-plan-20261022/combat-action-plan.json').read_text('utf8'))['rows']
template=json.loads((base/'hero001-body-actions-minimax-v3-fastdecode/workflow.json').read_text('utf8'))
overrides=json.loads((ROOT/'art-migration/prop-continuity-overrides.json').read_text('utf8'))
def normalize(source,out,name,hid):
 with Image.open(source) as image:
  image=image.convert('RGBA');box=image.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();image=image.crop(box)
  scale=min(a.height/image.height,700/image.width);image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
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
 for kind,source in {'idle':ROOT/f'local_game/assets/street/characters/{hid:03}/portrait.png',**poses}.items():files[kind],inputs[kind]=normalize(source,out,kind,hid)
 prompt=f'''One fixed-camera production sprite animation of the EXACT character shown in the guide images. Same identity, face, horns, hair, outfit, colors, anatomy and ALL held props throughout. Premium tactile 2.5D semi-realistic semi-cartoon absurd neighborhood game style. Full body, head, feet and weapon visible with generous safe margins on all sides. Pure black featureless background. No camera movement, no environment, no other person, no duplicate limbs, no invented weapon, no VFX; never lose a held prop.
 The three-second clip has exactly TWO separate coherent actions. Frames0-35: start in provided idle, perform ONE normal attack matching the attack guide around frame16, smoothly recover to idle at frame36. Normal action intent: {rows['attack']['bodyDesign']}; prop/body observation: {rows['attack']['weaponObservation']}. Frames36-72: perform ONE distinct special-skill gesture matching the skill guide around frame54, recover to original idle by frame72. Skill action intent: {rows['skill']['bodyDesign']}; purpose {rows['skill']['purpose']}; target {rows['skill']['targetSide']}; {rows['skill']['weaponObservation']}. Respect the provided props: if playing an instrument, animate playing it; if casting or supporting, animate the gesture rather than inventing a melee punch. No repeated attacks. The game handles travel separately: keep foot/root position fixed; no walking, sliding, or body scale drift. Natural shoulder/elbow mechanics and cloth follow-through; crisp readable silhouette without motion blur.'''
 if str(hid) in overrides:prompt+='\nCRITICAL actual-reference override, takes priority over contradictory plan text: '+json.dumps(overrides[str(hid)],ensure_ascii=False)
 g=json.loads(json.dumps(template));g['4']['inputs']['image']=files['idle'];g['5']['inputs']['image']=files['attack'];g['6']['inputs']['image']=files['skill'];g['7']['inputs']['prompt']=prompt
 g['14']['inputs']['noise_seed']=202610290000+hid;g['18']['inputs']['filename_prefix']=f'street-reskin/hero{hid:03}_body';g['20']['inputs']['filename_prefix']=f'street-reskin/hero{hid:03}_body_video'
 folder=submit(g,name,front=True)
 (folder/'body-design.json').write_text(json.dumps({'heroId':hid,'inputs':inputs,'actions':{k:{'sourceFrames':[0,35] if k=='attack' else [36,72],'guideImpactFrame':16 if k=='attack' else 54,'native':rows[k]} for k in rows},'length':73,'nativeClockMustBeRetained':True,'manualVideoReview':'pending','runtimeIntegrated':False},ensure_ascii=False,indent=2),'utf8')
