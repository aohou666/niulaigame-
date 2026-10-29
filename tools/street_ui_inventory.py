"""Inventory every UI sheet region, preserving reviewed replacement status on rerun."""
import collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';OUT=ROOT/'art-migration'
p=OUT/'ui-regions.jsonl';prior={r['key']:r for r in (json.loads(x) for x in p.read_text('utf8').splitlines())} if p.exists() else {}
manifest=json.loads((GAME/'resource/default.res_49784.json').read_text('utf8'));byName={r['name']:r for r in manifest['resources']};rows=[]
for r in manifest['resources']:
 if r['type']!='sheet':continue
 sheet=json.loads((GAME/'resource'/r['url']).read_text('utf8'));imageKey=r['name'][:-5]+'_png';image=byName[imageKey]
 for name,frame in sheet['frames'].items():
  key=r['name']+'.'+name;row={'key':key,'bareKey':name+'_png','sheetKey':r['name'],'sheetPath':'resource/'+r['url'],'atlasPath':'resource/'+image['url'],'frame':frame,'status':'pending'}
  if key in prior:row.update({k:v for k,v in prior[key].items() if k in ['status','replacement','evidence']})
  rows.append(row)
p.write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows),'utf8');print(json.dumps({'sheets':len(set(r['sheetKey'] for r in rows)),'regions':len(rows),'statuses':dict(collections.Counter(r['status'] for r in rows))}))
