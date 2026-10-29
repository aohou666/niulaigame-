"""Bind reviewed generated panel cells to exact original sheet regions and aliases."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--version',required=True);a=p.parse_args()
groupPath=ROOT/f'art-migration/ui-groups/{a.name}.json';group=json.loads(groupPath.read_text('utf8'));assert group['manualReview']=='approved'
job=json.loads((ROOT/group['matteJob']/'job.json').read_text('utf8'));assert len(job['outputs'])==len(group['entries'])
regions={r['key']:r for r in map(json.loads,(ROOT/'art-migration/ui-regions.jsonl').read_text('utf8').splitlines())}
out=GAME/f'assets/street/ui/{a.name}';out.mkdir(exist_ok=True);records=[]
for i,entry in enumerate(group['entries']):
 r=regions[entry['key']];f=r['frame'];raw=Image.open(ROOT/entry['prepared']).convert('RGBA');alpha=Image.open(ROOT/job['outputs'][i]['path']).getchannel('A');assert raw.size==alpha.size
 alpha=alpha.point(lambda v:0 if v<9 else v);box=alpha.point(lambda v:255 if v>16 else 0).getbbox();assert box and min(box[0],box[1],raw.width-box[2],raw.height-box[3])>2
 raw.putalpha(alpha);tile=raw.crop(box);size=[f['w'],f['h']];tile=tile.resize((size[0]-2,size[1]-2),Image.Resampling.LANCZOS);target=Image.new('RGBA',size);target.alpha_composite(tile,(1,1));path=out/(entry['bareKey']+'.png');target.save(path)
 original=GAME/r['atlasPath'];key=entry['key'];records.append({'originalKey':key,'originalPath':r['atlasPath'],'originalSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'originalRegion':key.split('.',1)[1],'targetKey':'street_'+a.name.replace('-','_')+'_'+entry['bareKey'],'targetPath':path.relative_to(GAME).as_posix(),'targetSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'extraAliases':[entry['bareKey']],'size':size,'status':'prepared-runtime-pending','generation':{'provider':'official-built-in-image_gen','source':group['source'].replace('local_game/','',1),'sourceSha256':hashlib.sha256((ROOT/group['source']).read_bytes()).hexdigest(),'sourceBox':entry['sourceBox'],'matte':'local-RMBG-1.4','matteJob':group['matteJob'],'prompt':'art-migration/prompts/'+a.name+'.txt'},'manualNotes':group['manualSourceReview']})
p=GAME/'street-art-data.js';d=json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'));keys={r['originalKey'] for r in records};d['resources']=[r for r in d['resources'] if r['originalKey'] not in keys]+records;d['version']=a.version;p.write_text('window.StreetArtData='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n','utf8')
print(json.dumps({'bindings':len(records),'keys':sorted(keys)}))
