"""Cover sheet-qualified variants of already generated UI art without changing native extents."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';p=argparse.ArgumentParser();p.add_argument('--version',required=True);a=p.parse_args()
path=GAME/'street-art-data.js';d=json.loads(path.read_text('utf8').split('=',1)[1].strip().rstrip(';'));lookup={r['originalKey']:r for r in d['resources']};records=[]
for row in map(json.loads,(ROOT/'art-migration/ui-regions.jsonl').read_text('utf8').splitlines()):
 if row['key'] in lookup or row['bareKey'] not in lookup:continue
 source=lookup[row['bareKey']];f=row['frame'];size=[f.get('sourceW',f['w']),f.get('sourceH',f['h'])];image=Image.open(GAME/source['targetPath']).convert('RGBA')
 if list(image.size)!=size:
  box=image.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();image=image.crop(box);image.thumbnail((size[0]-2,size[1]-2),Image.Resampling.LANCZOS);target=Image.new('RGBA',size);target.alpha_composite(image,((size[0]-image.width)//2,(size[1]-image.height)//2));image=target
 folder=GAME/'assets/street/ui/sheet-variants';folder.mkdir(exist_ok=True);out=folder/(row['key']+'.png');image.save(out)
 records.append({'originalKey':row['key'],'originalPath':row['atlasPath'],'originalRegion':row['key'].split('.',1)[1],'originalFrame':f,'originalSha256':hashlib.sha256((GAME/row['atlasPath']).read_bytes()).hexdigest(),'targetKey':'street_sheet_'+row['key'].replace('.','_'),'targetPath':out.relative_to(GAME).as_posix(),'targetSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'size':size,'status':'prepared-runtime-pending','generation':dict(source['generation'],inheritedFrom=source['originalKey'],nativeSheetExtentPreserved=True)})
d['resources']+=records;d['version']=a.version;path.write_text('window.StreetArtData='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n','utf8');print(json.dumps({'bindingsAdded':len(records),'keys':[r['originalKey'] for r in records]}))
