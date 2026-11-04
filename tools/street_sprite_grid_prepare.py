"""Technically split drawn grid frames; no pose interpolation or approval."""
import argparse, hashlib, json, shutil
from pathlib import Path
import numpy as np
from PIL import Image

p=argparse.ArgumentParser()
p.add_argument('--source',required=True);p.add_argument('--out',required=True)
p.add_argument('--start',type=int,required=True);p.add_argument('--columns',type=int,default=5);p.add_argument('--rows',type=int,default=3)
p.add_argument('--scale',type=float,required=True,help='One reviewed common scale for this strip; never normalize every pose height.')
p.add_argument('--auto-columns',action='store_true',help='Use seven separated alpha silhouettes when generated cell spacing is uneven; reject touching silhouettes.')
a=p.parse_args();src=Path(a.source);out=Path(a.out)
assert not out.exists(),'Preserve prior candidates in a distinct folder'
assert 0<a.scale<10
image=Image.open(src).convert('RGBA');assert image.getchannel('A').getextrema()[0]<64,'Opaque sheet is not approved transparent art'
columns=[round(i*image.width/a.columns) for i in range(a.columns+1)];rows=[round(i*image.height/a.rows) for i in range(a.rows+1)]
cells=[[columns[i%a.columns],rows[i//a.columns],columns[i%a.columns+1],rows[i//a.columns+1]] for i in range(a.columns*a.rows)]
records=[];prepared=[]
for i,cell in enumerate(cells):
 x0,y0,x1,y1=cell
 tile=image.crop(cell);alpha=np.asarray(tile.getchannel('A'))
 yy,xx=np.where(alpha>64);assert len(xx),f'Empty cell{i}'
 box=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1]
 margin=min(box[0],box[1],tile.width-box[2],tile.height-box[3])
 assert margin>=6,f'Cell{i} clips/reaches edge: bbox{box}, margin{margin}. Regenerate, do not pad missing art.'
 # The bottommost opaque tire contour is the foot anchor. Review these anchors
 # visually: extra graphics below the wheel must cause manual rejection.
 bottom=alpha[max(0,box[3]-4):box[3]].astype(float);weights=bottom.sum(0)
 footX=float(np.dot(np.arange(tile.width),weights)/weights.sum());footY=box[3]
 crop=tile.crop(box);crop=crop.resize((round(crop.width*a.scale),round(crop.height*a.scale)),Image.Resampling.LANCZOS)
 offset=[round(384+(box[0]-footX)*a.scale),round(680+(box[1]-footY)*a.scale)]
 assert offset[0]>=12 and offset[1]>=12 and offset[0]+crop.width<=756 and offset[1]+crop.height<=756,'Prepared frame exceeds safe canvas'
 canvas=Image.new('RGBA',(768,768));canvas.alpha_composite(crop,offset)
 prepared.append(canvas);records.append({'frame':a.start+i,'sourceCell':cell,'sourceAlphaBounds':box,'sourceFoot':[footX,footY],'sourceMargin':margin,'scale':a.scale,'preparedFoot':[384,680],'preparedOffset':offset,'rgbaSha256':hashlib.sha256(canvas.tobytes()).hexdigest()})
assert len({r['rgbaSha256'] for r in records})==len(cells),'Duplicated cell content is not independent drawn frames'
out.mkdir(parents=True);shutil.copy2(src,out/'official-source.png')
for record,im in zip(records,prepared):im.save(out/f"frame-{record['frame']:02}.png")
(out/'strip-qa.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sourceSize':list(image.size),'frames':records,'manualReview':'pending','scope':'Individually drawn source cells, tire root aligned with one common scale per sheet. No pose interpolation, per-pose height normalization, native action approval or complete-skin claim.','runtimeIntegrated':False},indent=2)+'\n','utf8')
print(json.dumps({'out':str(out),'frames':[r['frame'] for r in records],'manualReview':'pending'}))
