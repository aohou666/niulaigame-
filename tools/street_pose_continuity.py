"""Correct guide props using actual identity images, overriding mistaken plan observations."""
import argparse,json
from PIL import Image,ImageOps
from street_comfy import ROOT,qwen,submit
p=argparse.ArgumentParser();p.add_argument('ids',nargs='+',type=int);p.add_argument('--actions',nargs='+',choices=['attack','skill'],default=['attack','skill']);p.add_argument('--square',action='store_true');p.add_argument('--revision',type=int,default=3);a=p.parse_args();base=ROOT/'art-migration/generation';overrides=json.loads((ROOT/'art-migration/prop-continuity-overrides.json').read_text('utf8'))
for hid in a.ids:
 detail=overrides[str(hid)]
 for kind in a.actions:
  old=base/f'hero{hid:03}-{kind}-v{a.revision-1}';qfile=old/'qa.json';q=json.loads(qfile.read_text('utf8'));q['manualReview']='rejected';q['manualNotes']='Follow-up side-by-side comparison with actual idle reference revealed missing/changed props or skin color. Correct with explicit actual-reference override before video.';qfile.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf8')
  name=f'hero{hid:03}-{kind}-v{a.revision}'
  if (base/name).exists():continue
  prompt=f'''Create ONE production full-body {kind} key pose of the EXACT character in the reference image. Preserve face, hair, horns, species, exact garment colors, all props and which hand holds each prop. Actual reference continuity requirements: {detail['prop']}. Requested action: {detail[kind]}. The character identity picture takes priority over any earlier action plan. Use slightly right-facing three-quarter pose but do not mirror the reference, swap hands or hide essential held objects. Fixed body root, entire horns, tools, feet and hands inside generous safe margins. Same tactile 2.5D semi-realistic semi-cartoon absurd modern neighborhood game rendering, same soft lighting and material palette as reference. Crisp silhouette, no motion blur, no VFX, no target, no setting, no UI, no lettering, no watermark. Plain solid white background for clean alpha matting. Do not replace an existing object with a different object.'''
  reference=ROOT/f'local_game/assets/street/characters/{hid:03}/portrait.png'
  if a.square:
   target=ROOT/f'art-migration/references/hero{hid:03}-square.png';im=Image.open(reference).convert('RGBA');im=im.crop(im.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox());im.thumbnail((640,640),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(768,768));canvas.alpha_composite(im,((768-im.width)//2,(768-im.height)//2));canvas.save(target);reference=target
  g=qwen(prompt,reference,768,28,202610290000+a.revision*1000+hid*2+(kind=='skill'));g['11']={'class_type':'SplitImageWithAlpha','inputs':{'image':['6',0]}};g['9']={'class_type':'easy imageRemBg','inputs':{'images':['11',0],'rem_mode':'RMBG-1.4','image_output':'Hide','save_prefix':'street-reskin/matte','add_background':'none','torchscript_jit':False,'refine_foreground':False}};g['10']={'class_type':'SaveImage','inputs':{'images':['9',0],'filename_prefix':f'street-reskin/hero{hid:03}_{kind}_continuity_alpha'}}
  folder=submit(g,name,front=True);d=json.loads((old/'design.json').read_text('utf8'));d['revisionReason']='actual-reference prop/color continuity';d['actualReferenceOverride']=detail;(folder/'design.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
