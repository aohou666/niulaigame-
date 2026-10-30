"""Require every enabled generated runtime dependency to exist in the Git index/commit."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
def js(name):return json.loads((GAME/name).read_text('utf8').split('=',1)[1].strip().rstrip(';'))
def dependencies():
 result=set()
 def collect(value):
  if isinstance(value,dict):
   for v in value.values():collect(v)
  elif isinstance(value,list):
   for v in value:collect(v)
  elif isinstance(value,str) and value.startswith('assets/street/'):result.add('local_game/'+value)
 for name in ['character-art-data.js','character-idle-data.js','character-idle-atlas-data.js','street-art-data.js','street-body-data.js','street-effects-data.js']:
  collect(js(name));result.add('local_game/'+name)
 idle=js('character-idle-data.js')
 for cfg in list(idle['heroes'].values())+list(idle.get('skins',{}).values()):
  if cfg.get('baseUrl','').startswith('assets/street/'):
   result.update('local_game/'+cfg['baseUrl']+name for name in cfg['files'])
 # baseUrl is a directory, not a standalone dependency.
 result={p for p in result if not p.endswith('/')}
 html=GAME/'index_bh_lite3zbtest_andr.html';result.add(html.relative_to(ROOT).as_posix())
 for url in re.findall(r'(?:src|href)=["\']([^"\']+)',html.read_text('utf8')):
  path=url.split('?',1)[0]
  if path and not re.match(r'^(?:https?:|data:|#|//)',path) and (GAME/path).is_file():result.add((GAME/path).relative_to(ROOT).as_posix())
 return sorted(result)
def verify(tree=None):
 paths=dependencies();entries={}
 if tree:
  raw=subprocess.check_output(['git','ls-tree','-rz',tree],cwd=ROOT)
  for entry in raw.split(b'\0'):
   if entry:
    meta,name=entry.split(b'\t',1);entries[name.decode('utf8')]=meta.split()[2].decode()
 else:
  raw=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT)
  for entry in raw.split(b'\0'):
   if entry:
    meta,name=entry.split(b'\t',1);entries[name.decode('utf8')]=meta.split()[1].decode()
 missing=[];different=[]
 for path in paths:
  file=ROOT/path
  if path not in entries or not file.is_file():missing.append(path);continue
  value=file.read_bytes();blob=hashlib.sha1(b'blob '+str(len(value)).encode()+b'\0'+value).hexdigest()
  # Text assets may be normalized to LF by Git; binary images must match byte-for-byte.
  if blob!=entries[path] and file.suffix.lower() in ['.webp','.png','.jpg','.jpeg','.bin','.dbbin']:different.append(path)
 return {'pass':not missing and not different,'scope':'Enabled generated assets, all85 portrait/idle mappings, and static HTML dependencies; original resource package remains a separate release dependency.','tree':tree or 'index','checked':len(paths),'missing':missing,'binaryContentDiffers':different}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--tree');p.add_argument('--report');a=p.parse_args();r=verify(a.tree)
 if a.report:(ROOT/a.report).write_text(json.dumps(r,indent=2)+'\n','utf8')
 print(json.dumps(r));raise SystemExit(not r['pass'])
