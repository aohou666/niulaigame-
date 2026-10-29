"""Verify every promoted street image, atlas frame, root and native frame mapping."""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
def loadjs(p):return json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'))
def verify():
 errors=[];images=0;frames=0;characters=[]
 for r in loadjs(GAME/'street-art-data.js')['resources']:
  try:
   p=GAME/r['targetPath'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['targetSha256'],'digest mismatch'
   with Image.open(p) as im:assert list(im.size)==list(r['size']),'dimensions mismatch';assert im.getbbox() is not None,'empty image'
   images+=1
  except Exception as e:errors.append({'resource':r['originalKey'],'error':str(e)})
 body=loadjs(GAME/'street-body-data.js') if (GAME/'street-body-data.js').exists() else {'characters':[]}
 for cfg in body['characters']:
  try:
   if cfg.get('atlasSha256'):assert hashlib.sha256((GAME/cfg['atlas']).read_bytes()).hexdigest()==cfg['atlasSha256'],'atlas digest mismatch'
   with Image.open(GAME/cfg['atlas']) as im:
    assert im.mode=='RGBA','atlas must have alpha';hashes=set()
    for f in cfg['frames']:
     assert f['x']>=0 and f['y']>=0 and f['x']+f['w']<=im.width and f['y']+f['h']<=im.height,'tile outside atlas'
     tile=im.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']));assert tile.getchannel('A').getbbox(),'empty body frame';hashes.add(hashlib.sha256(tile.tobytes()).hexdigest());frames+=1
    assert len(hashes)>4,'sequence lacks distinct motion frames'
   assert cfg['bodyHeight']>0 and len(cfg['root'])==2
   for action,seq in cfg['actions'].items():
    assert seq['fps']>0 and len(seq['frameMap'])>1
    assert all(isinstance(n,int) and 0<=n<len(cfg['frames']) for n in seq['frameMap']),'bad source frame index'
    if seq.get('nativeImpactFrame') is not None:assert seq['frameMap'][seq['nativeImpactFrame']]==seq['sourceImpactFrame'],'impact mapping mismatch'
   characters.append({'hero':cfg['id'],'frames':len(cfg['frames']),'distinctFrames':len(hashes),'actions':list(cfg['actions'])})
  except Exception as e:errors.append({'hero':cfg['id'],'error':str(e)})
 return {'images':images,'bodyAtlasFrames':frames,'bodyCharacters':characters,'errors':errors}
if __name__=='__main__':
 r=verify();print(json.dumps(r));raise SystemExit(bool(r['errors']))
