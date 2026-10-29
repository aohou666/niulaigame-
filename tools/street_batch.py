"""One distinct Qwen reference workflow per hero/action; no completion-by-file-count."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from street_comfy import ROOT,qwen,submit,collect,request

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['submit','collect','status']);a=p.parse_args()
 base=ROOT/'art-migration/generation'
 if a.mode=='status':
  counts={}
  for f in base.glob('*/job.json'):
   j=json.loads(f.read_text('utf8'));counts[j['status']]=counts.get(j['status'],0)+1
  queue=request('/queue');print(json.dumps({'jobs':counts,'running':[(x[0],x[1]) for x in queue['queue_running']],'pending':len(queue['queue_pending'])}));return
 if a.mode=='collect':
  for folder in sorted(base.iterdir()):
   f=folder/'job.json'
   if f.exists() and json.loads(f.read_text('utf8'))['status']=='submitted':collect(folder)
  return
 plan=json.loads((ROOT/'outputs/combat-action-plan-20261022/combat-action-plan.json').read_text('utf8'))
 art=json.loads((ROOT/'local_game/character-art-data.js').read_text('utf8').split('=',1)[1].strip().rstrip(';'))['heroes']
 count=0
 for row in plan['rows']:
  hid=str(row['heroId'])
  if hid not in art:continue
  kind='attack' if row['taskId'].endswith('-ATK') else 'skill'
  name=f'hero{int(hid):03d}-{kind}-v1'
  if (base/name).exists():continue
  prompt=f'''Create ONE production key pose for character {row['name']}, ID {hid}. The attached image is the exact identity/outfit reference. Preserve species, face, horns/ears, hair, body proportions, clothing and the existing held props. Change the pose into a strong readable {kind} key pose, three-quarter view facing RIGHT, full body with both feet inside frame. Follow this specific action design: {row['bodyDesign']}. Observed prop/weapon: {row['weaponObservation']}; weapon category: {row['weapon']}. Purpose: {row['purpose']}. Keep the body centered, do not translate across the battlefield, the game handles root movement. This is a pose sprite, do not render the target, battlefield or screen UI. 2.5D semi-realistic semi-cartoon absurd modern neighborhood street-block game aesthetic, tactile materials, broad readable silhouette, warm soft studio light. A single character only, plain solid white background for clean alpha matting. No text, no watermark, no ancient armor unless the reference actually contains it. No extra weapons or unrequested props. Keep the pose distinctive to this character and its action. No motion blur obscuring limbs. Do not include enormous VFX; effects are a separate asset.'''
  graph=qwen(prompt,ROOT/'local_game'/art[hid]['portrait'],768,28,2026102900+int(hid)*2+(kind=='skill'))
  graph['11']={'class_type':'SplitImageWithAlpha','inputs':{'image':['6',0]}}
  graph['9']={'class_type':'easy imageRemBg','inputs':{'images':['11',0],'rem_mode':'RMBG-1.4','image_output':'Hide','save_prefix':'street-reskin/matte','add_background':'none','torchscript_jit':False,'refine_foreground':False}}
  graph['10']={'class_type':'SaveImage','inputs':{'images':['9',0],'filename_prefix':f'street-reskin/hero{int(hid):03d}_{kind}_alpha'}}
  folder=submit(graph,name)
  (folder/'design.json').write_text(json.dumps({'heroId':int(hid),'action':kind,'taskId':row['taskId'],'bodyDesign':row['bodyDesign'],'impactMs':row['impactMs'],'durationMs':row['rawDurationMs'],'sourceModel':row['model'],'sourceAction':row['action'],'review':'pending','runtimeIntegrated':False},ensure_ascii=False,indent=2),'utf8')
  count+=1
 print('Distinct submitted workflows:',count)

if __name__=='__main__':main()
