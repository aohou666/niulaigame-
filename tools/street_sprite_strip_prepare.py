"""Technically split seven drawn consecutive frames; no pose interpolation or approval."""
import argparse, hashlib, json, shutil
from pathlib import Path
import numpy as np
from PIL import Image

p=argparse.ArgumentParser()
p.add_argument('--source',required=True);p.add_argument('--out',required=True)
p.add_argument('--start',type=int,required=True)
p.add_argument('--source-count',type=int,default=7)
p.add_argument('--order',help='Comma-separated unique source-cell order for selected drawn frames; no interpolation.')
p.add_argument('--take',type=int,default=7,help='Use only the selected prefix of a seven-cell source; unselected cells are not approved frames.')
p.add_argument('--scale',type=float,required=True,help='One reviewed common scale for this strip; never normalize every pose height.')
p.add_argument('--components',action='store_true',help='Separate seven disjoint full figures whose horizontal bounds overlap; never reconstruct missing pixels.')
p.add_argument('--auto-columns',action='store_true',help='Use seven separated alpha silhouettes when generated cell spacing is uneven; reject touching silhouettes.')
a=p.parse_args();src=Path(a.source);out=Path(a.out)
assert not out.exists(),'Preserve prior candidates in a distinct folder'
assert 0<a.scale<10 and 1<=a.take<=a.source_count
image=Image.open(src).convert('RGBA');assert image.getchannel('A').getextrema()[0]<64,'Opaque sheet is not approved transparent art'
columns=[round(i*image.width/a.source_count) for i in range(a.source_count+1)]
cells=[columns[i:i+2] for i in range(a.source_count)]
if a.auto_columns:
 mask=(np.asarray(image.getchannel('A'))>64).any(0)
 indices=np.where(mask)[0];assert len(indices),'Empty sheet'
 spans=[];start=previous=int(indices[0])
 for column in indices[1:]:
  if column-previous>3:spans.append([start,previous+1]);start=int(column)
  previous=int(column)
 spans.append([start,previous+1])
 assert len(spans)==a.source_count,f'Need seven separate silhouettes, got{len(spans)}. Regenerate overlapping/extra figures.'
 # Crops may share transparent gap pixels, never silhouette pixels. A shared
 # midpoint needlessly halves a narrow but genuinely empty source gap.
 cells=[[max(0,span[0]-12,spans[i-1][1]+1 if i else 0),min(image.width,span[1]+12,spans[i+1][0]-1 if i<a.source_count-1 else image.width)] for i,span in enumerate(spans)]
isolated=None
if a.components:
 import cv2
 assert not a.auto_columns
 rgba=np.asarray(image);alpha=rgba[:,:,3];count,labels,stats,centroids=cv2.connectedComponentsWithStats((alpha>64).astype('uint8'),8)
 major=sorted([i for i in range(1,count) if stats[i,4]>5000],key=lambda i:stats[i,0]);assert len(major)==a.source_count,'Need seven fully disjoint figures, not overlapping painted bodies'
 mask=np.isin(labels,major);distance,nearest=cv2.distanceTransformWithLabels((~mask).astype('uint8'),cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_CCOMP)
 assert not np.any((alpha>8)&(distance>24)),'Detached source fragments require manual inspection, not silent deletion'
 isolated=[];cells=[]
 for label in major:
  yy,xx=np.where(labels==label);owner=nearest[yy[0],xx[0]];copy=rgba.copy();copy[:,:,3]=np.where(nearest==owner,alpha,0);isolated.append(Image.fromarray(copy,'RGBA'))
  left=int(xx.min());right=int(xx.max())+1;cells.append([max(0,left-12),min(image.width,right+12)])
 assert all(np.all(nearest[labels==label]==nearest[np.where(labels==label)[0][0],np.where(labels==label)[1][0]]) for label in major)
order=[int(n) for n in a.order.split(',')] if a.order else list(range(a.take));assert len(order)==a.take and len(set(order))==a.take and all(0<=n<a.source_count for n in order)
records=[];prepared=[]
for i in range(a.take):
 sourceIndex=order[i]
 x0,x1=cells[sourceIndex]
 tile=(isolated[sourceIndex] if isolated else image).crop((x0,0,x1,image.height));alpha=np.asarray(tile.getchannel('A'))
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
 prepared.append(canvas);records.append({'frame':a.start+i,'sourceCellIndex':sourceIndex,'sourceCell':[x0,0,x1,image.height],'sourceAlphaBounds':box,'sourceFoot':[footX,footY],'sourceMargin':margin,'scale':a.scale,'preparedFoot':[384,680],'preparedOffset':offset,'rgbaSha256':hashlib.sha256(canvas.tobytes()).hexdigest()})
assert len({r['rgbaSha256'] for r in records})==a.take,'Duplicated source content cannot count as independently drawn frames'
out.mkdir(parents=True);shutil.copy2(src,out/'official-source.png')
for record,im in zip(records,prepared):im.save(out/f"frame-{record['frame']:02}.png")
(out/'strip-qa.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sourceSize':list(image.size),'selectedSourceCells':order,'unusedSourceCells':[n for n in range(a.source_count) if n not in order],'technicalSegmentation':'seven disjoint alpha components, original source pixels retained; no pose reconstruction' if isolated else 'separated columns','frames':records,'manualReview':'pending','scope':'Seven individually drawn source cells, root aligned with common strip scale. No creative edits/interpolation; neither complete21-frame animation nor manual approval.','runtimeIntegrated':False},indent=2)+'\n','utf8')
print(json.dumps({'out':str(out),'frames':[r['frame'] for r in records],'manualReview':'pending'}))
