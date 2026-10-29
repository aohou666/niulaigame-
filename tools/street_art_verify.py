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
 auditPath=ROOT/'art-migration/native-action-events.json';nativeAudit=json.loads(auditPath.read_text('utf8')) if auditPath.exists() else None;nativeRows={(r['model'],r['action']):r for r in nativeAudit['records']} if nativeAudit else {};nativeChecks=0
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
   for action,seq in list(cfg['actions'].items())+[(model+'/'+action,seq) for model,actions in cfg.get('modelActionOverrides',{}).items() for action,seq in actions.items()]:
    assert seq['fps']>0 and len(seq['frameMap'])>1
    assert all(isinstance(n,int) and 0<=n<len(cfg['frames']) for n in seq['frameMap']),'bad source frame index'
    if seq.get('nativeImpactFrame') is not None:assert seq['frameMap'][seq['nativeImpactFrame']]==seq['sourceImpactFrame'],'impact mapping mismatch'
    for mark in seq.get('eventAnchors',[]):assert seq['frameMap'][mark['nativeFrame']]==mark['sourceFrame'],'multi-event mapping mismatch'
   if cfg.get('nativeEventAuditSha256'):
    assert nativeAudit['complete'] and hashlib.sha256(auditPath.read_bytes()).hexdigest()==cfg['nativeEventAuditSha256'],'native event audit provenance mismatch'
    for model in cfg['models']:
     for action,base in cfg['actions'].items():
      seq=cfg.get('modelActionOverrides',{}).get(model,{}).get(action,base);native=nativeRows[(model,action)];assert len(seq['frameMap'])==native['durationFrames'] and abs(seq['fps']-native['fps'])<.0001,'native clock differs'
      assert [(e['name'],e['frame0']) for e in seq.get('nativeEvents',[])]==[(e['name'],e['frame0']) for e in native['events'] if e['name'] in ['pia','zd']],'native event metadata differs';nativeChecks+=1
   characters.append({'hero':cfg['id'],'frames':len(cfg['frames']),'distinctFrames':len(hashes),'actions':list(cfg['actions'])})
  except Exception as e:errors.append({'hero':cfg['id'],'error':str(e)})
 return {'images':images,'bodyAtlasFrames':frames,'bodyCharacters':characters,'nativeModelActionsChecked':nativeChecks,'errors':errors}
if __name__=='__main__':
 r=verify();print(json.dumps(r));raise SystemExit(bool(r['errors']))
