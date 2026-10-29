import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
d=json.loads((GAME/'character-idle-atlas-data.js').read_text('utf8').split('=',1)[1].strip().rstrip(';'))
idle=json.loads((GAME/'character-idle-data.js').read_text('utf8').split('=',1)[1].strip().rstrip(';'))
for hid,cfg in idle['heroes'].items():
 if cfg.get('atlas') is not None:d['heroes'][hid]=cfg['atlas']
errors=[];checked=0;pages=0
for hid,h in d['heroes'].items():
 for profile,pack in h['profiles'].items():
  if len(pack['frames'])!=h['frameCount']:errors.append([hid,profile,'frame count'])
  for pageid,p in enumerate(pack['pages']):
   path=GAME/p['url'];pages+=1
   if hashlib.sha256(path.read_bytes()).hexdigest()!=p['sha256']:errors.append([hid,profile,pageid,'hash'])
   with Image.open(path) as image:
    if image.size!=(p['width'],p['height']) or 'A' not in image.getbands():errors.append([hid,profile,pageid,'size or alpha'])
    for f in pack['frames']:
     if f['page']!=pageid:continue
     checked+=1
     if f['x']<2 or f['y']<2 or f['x']+f['w']>image.width-2 or f['y']+f['h']>image.height-2:errors.append([hid,profile,checked,'bounds'])
     if image.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h'])).getchannel('A').getbbox() is None:errors.append([hid,profile,checked,'empty'])
report={'characters':len(d['heroes']),'pages':pages,'framesAcrossTwoProfiles':checked,'errors':errors}
(ROOT/'art-migration/idle-atlas-verification.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))
if errors:raise SystemExit(1)
