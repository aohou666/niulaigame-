"""Matte only explicitly reviewed body motion; raw source RGB stays separate."""
import argparse,json,shutil
from pathlib import Path
from street_comfy import ROOT,COMFY,submit
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();base=ROOT/'art-migration/generation';source=base/a.name
qa=json.loads((source/'body-qa.json').read_text('utf8'));assert qa['manualVideoReview']=='approved-for-matting'
job=json.loads((source/'job.json').read_text('utf8'));design=json.loads((source/'body-design.json').read_text('utf8'));hid=design['heroId'];inputdir=COMFY/'input'/('street_matte_'+a.name);inputdir.mkdir(exist_ok=True)
for i,r in enumerate(job['outputs']):shutil.copy2(ROOT/r['path'],inputdir/f'{i:04}.png')
g={'1':{'class_type':'LoadImagesFromFolderKJ','inputs':{'folder':str(inputdir),'width':512,'height':512,'keep_aspect_ratio':'pad','image_load_cap':len(job['outputs']),'start_index':0,'include_subfolders':False}},'2':{'class_type':'SplitImageWithAlpha','inputs':{'image':['1',0]}},'3':{'class_type':'easy imageRemBg','inputs':{'images':['2',0],'rem_mode':'RMBG-1.4','image_output':'Hide','save_prefix':'street-reskin/matte','add_background':'none','torchscript_jit':False,'refine_foreground':False}},'4':{'class_type':'SaveImage','inputs':{'images':['3',0],'filename_prefix':f'street-reskin/hero{hid:03}_body_alpha'}}}
folder=submit(g,a.name.replace('minimax','matte'),front=True);design.update(sourceBodyJob=source.relative_to(ROOT).as_posix(),sourceFrameOrder=[r['path'] for r in job['outputs']],manualVideoReview='approved-for-matting');(folder/'body-design.json').write_text(json.dumps(design,ensure_ascii=False,indent=2),'utf8')
