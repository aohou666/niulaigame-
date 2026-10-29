"""Install one generated environmental plate with exact key, dimensions and provenance."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
p=argparse.ArgumentParser();p.add_argument('--key',required=True);p.add_argument('--source',required=True);p.add_argument('--target',required=True);p.add_argument('--prompt',required=True);p.add_argument('--version',required=True);a=p.parse_args()
manifest=json.loads((GAME/'resource/default.res_49784.json').read_text('utf8'));r=next(r for r in manifest['resources'] if r['name']==a.key);original=GAME/'resource'/r['url'];size=Image.open(original).size;source=GAME/a.source;target=GAME/a.target;target.parent.mkdir(parents=True,exist_ok=True)
im=ImageOps.fit(Image.open(source).convert('RGB'),size,Image.Resampling.LANCZOS);im.save(target,quality=94,subsampling=0)
entry={'originalKey':a.key,'originalPath':original.relative_to(GAME).as_posix(),'originalSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'targetKey':'street_environment_'+a.key,'targetPath':a.target,'targetSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'size':size,'status':'prepared-unreviewed','generation':{'provider':'official-built-in-image_gen','source':a.source,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'prompt':a.prompt}}
p=GAME/'street-art-data.js';d=json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'));d['version']=a.version;d['resources']=[r for r in d['resources'] if r['originalKey']!=a.key]+[entry];p.write_text('window.StreetArtData='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n','utf8');print(json.dumps(entry))
