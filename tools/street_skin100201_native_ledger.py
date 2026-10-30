"""Record only qualified production single-resource replacements, not full skins."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
def load(name):return json.loads((GAME/name).read_text('utf8').split('=',1)[1].strip().rstrip(';'))
art=load('street-art-data.js');character=load('character-art-data.js')
keys={'mjl_img_simayi_png','zd_jn_002_skin_01_png','zd_txt_002_skin_01_png','common_activity_simayi_new01_tex_png'}
for e in art['resources']:
 if e['originalKey'] in keys:
  e['skinCode']=100201
  if e['originalPath'].startswith('assets/'):e['originalPath']='resource/'+e['originalPath']
  assert (GAME/e['originalPath']).is_file(),'Original asset path must be game-relative'
path=GAME/'street-art-data.js';prefix=path.read_text('utf8').split('=',1)[0]+'='
path.write_text(prefix+json.dumps(art,ensure_ascii=False,indent=2)+';\n','utf8')
updates={e['originalPath']:e for e in art['containers'] if e.get('nativeBodyReplacement')}
updates.update({e['originalPath']:e for e in art['resources'] if e['originalKey'] in keys})
rows=[json.loads(x) for x in (ROOT/'art-migration/assets.jsonl').read_text('utf8').splitlines()]
assert len(updates)==6 and set(updates)<={r['path'] for r in rows},'All six new whole-resource replacements must match ledger rows'
for row in rows:
 if row['path'] in updates:
  entry=updates[row['path']];row.update(status='complete',replacement=entry['targetPath'],skinCode=100201,runtimeVerification='versions/0.97.0/native-battle-skill-banner/runtime.json',completionScope='Only this whole texture image/container is replaced; full skin and85-character completion remain false.')
  if 'common_activity_simayi_new01_tex' in row['path']:row['runtimeVerification']='versions/0.97.0/activity/movieclip-runtime.json'
  if 'mjl_img_simayi_' in row['path']:row['runtimeVerification']='versions/0.97.0/skin100201-static-native.json'
 for key,binding in character['heroes']['2']['bindings'].items():
  if binding.get('skinCode')==100201 and any(ref.get('name')==key for ref in row.get('references',[])):
   row.update(replacement=binding['url'],evidence='versions/0.97.0/skin100201-static-native.json')
(ROOT/'art-migration/assets.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False,separators=(',',':')) for r in rows)+'\n','utf8',newline='\n')
print(json.dumps({'completeSingleResources':sum(r['status']=='complete' for r in rows),'completeCharacters':0,'completeIndependentSkins':0}))
