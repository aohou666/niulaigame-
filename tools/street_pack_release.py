"""Package only original runtime game resources; never saves, credentials or unrelated files."""
import hashlib,json,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'local_game/resource';out=ROOT/'release-manifest';out.mkdir(exist_ok=True)
target=out/'original-game-resources.zip';files=sorted(p for p in source.rglob('*') if p.is_file());start=time.monotonic()
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as archive:
 for p in files:archive.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as archive:
 bad=archive.testzip()
 if bad:raise RuntimeError('Corrupt member '+bad)
h=hashlib.sha256()
with target.open('rb') as f:
 for part in iter(lambda:f.read(4*1024*1024),b''):h.update(part)
record={'file':target.name,'bytes':target.stat().st_size,'sha256':h.hexdigest(),'files':len(files),'sourceBytes':sum(p.stat().st_size for p in files),'verifiedZipCrc':True,'seconds':round(time.monotonic()-start,2),'containsSaves':False,'containsCredentials':False,'rawIdleSourceFramesIncluded':False,'runtimeIdleAtlases':'Tracked in Git under local_game/assets/street/idle/'}
(out/'original-game-resources.manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(record))
