"""Extract existing disconnected component pixels without clipping at grid lines."""
import json,hashlib,argparse
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--folder',default='art-migration/generation/skin100201-native-clothing18-official-v1');parser.add_argument('--map',default='art-migration/skin-migration/100201/native-body-parts/clothing-vehicle-original18-map.json');parser.add_argument('--min-area',type=int,default=1000);args=parser.parse_args()
 folder=ROOT/args.folder
 document=json.loads((ROOT/args.map).read_text('utf8'));mapping=document['regions'];cols,rowCount=document['layout'];count=len(mapping)
 source=folder/'official-source.png';im=Image.open(source).convert('RGBA');pixels=np.asarray(im);alpha=pixels[:,:,3]
 n,labels,stats,centers=cv2.connectedComponentsWithStats((alpha>16).astype('uint8'),8)
 ids=[i for i in range(1,n) if stats[i,4]>args.min_area];assert len(ids)==count,(len(ids),count)
 lookup={r['cell']:r for r in mapping}
 nearest=np.zeros(alpha.shape,'int32');distance=np.full(alpha.shape,np.inf,'float32');assigned={}
 for cid in ids:
  cx,cy=centers[cid];cell=min(rowCount-1,int(cy/im.height*rowCount))*cols+min(cols-1,int(cx/im.width*cols));assert cell not in assigned;assigned[cell]=cid
  d=cv2.distanceTransform((labels!=cid).astype('uint8'),cv2.DIST_L2,5);take=d<distance;nearest[take]=cid;distance[take]=d[take]
 assert set(assigned)==set(range(count));rows=[]
 for cell in range(count):
  cid=assigned[cell];owned=(nearest==cid)&(distance<=12)&(alpha>0);selected=pixels.copy();selected[~owned]=0;obj=Image.fromarray(selected,'RGBA');box=obj.getchannel('A').getbbox();assert box and min(box[0],box[1],im.width-box[2],im.height-box[3])>5
  obj=obj.crop(box);padded=Image.new('RGBA',(obj.width+32,obj.height+32));padded.alpha_composite(obj,(16,16));path=folder/f'part-component-{cell:02}.png';padded.save(path)
  rows.append({**lookup[cell],'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sourceBounds':box,'segmentationComponent':cid,'sourceCrossedNominalCell':box[0]<cell%cols*im.width/cols or box[2]>(cell%cols+1)*im.width/cols or box[1]<cell//cols*im.height/rowCount or box[3]>(cell//cols+1)*im.height/rowCount,'visibleMargin':16})
 for bg,label in [('#f2ead8','light'),('#233238','dark')]:
  sheet=Image.new('RGB',(cols*240,rowCount*280),bg);draw=ImageDraw.Draw(sheet)
  for row in rows:
   i=row['cell'];tile=Image.open(ROOT/row['path']).convert('RGBA');tile.thumbnail((228,246));x=i%cols*240;y=i//cols*280;sheet.paste(tile,(x+(240-tile.width)//2,y),tile);draw.text((x+3,y+255),str(i)+' '+row['nativeRegion'].split('/')[-1],fill='black' if label=='light' else 'white')
  sheet.save(folder/f'source{count}-components-{label}.jpg')
 qa={'provider':'official-imagegen','manualReview':'pending-segmented-pixel-extraction-and-native-fit','runtimeIntegrated':False,'completeSkin':False,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'parts':rows,'technicalExtraction':f'{count} alpha>16 components area>{args.min_area} assigned to native cell by centroid; retain original RGBA for nearest-component pixels within12px;16px transparent output padding. No creative paint, interpolation of pose or alpha hole filling.','nativeMap':args.map,'componentCount':count}
 (folder/'component-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'components':count,'crossedCells':[r['cell'] for r in rows if r['sourceCrossedNominalCell']],'creativePixelsAdded':0}))

if __name__=='__main__':main()
