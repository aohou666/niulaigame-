"""Bind measured per-model native effect clocks; never alter DragonBones events."""
import argparse,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--version',required=True);a=p.parse_args();auditPath=ROOT/'art-migration/versions'/a.version/'effect-native-events.json';audit=json.loads(auditPath.read_text('utf8'));assert audit['complete'];lookup={r['model']:r for r in audit['records']};path=ROOT/'local_game/street-effects-data.js';d=json.loads(path.read_text('utf8').split('=',1)[1].strip().rstrip(';'));different=[]
for cfg in d['effects']:
 cfg['nativeEventAuditPath']=auditPath.relative_to(ROOT).as_posix();cfg['nativeEventAuditSha256']=hashlib.sha256(auditPath.read_bytes()).hexdigest();cfg['nativeModels']={name:lookup[name] for name in cfg['models']};overrides={}
 for name in cfg['models']:
  r=lookup[name]
  if r['durationFrames']!=cfg['frameCount'] or abs(r['fps']-cfg['fps'])>1e-5:
   count=r['durationFrames'];basePeak=cfg.get('retargetPeakFrame',cfg['originalPeakFrame']);nativePeak=round(basePeak*(count-1)/(cfg['frameCount']-1));knots=sorted({0:0,count-1:cfg['frameCount']-1,nativePeak:basePeak}.items());mapping=[]
   for i in range(count):
    left,right=next((x,y) for x,y in zip(knots,knots[1:]) if x[0]<=i<=y[0]);mapping.append(round(left[1]+(right[1]-left[1])*(i-left[0])/(right[0]-left[0])))
   overrides[name]={'fps':r['fps'],'frameCount':count,'frameMap':mapping,'visualPeakFrame':nativePeak};different.append({'model':name,'nativeFrames':r['durationFrames'],'atlasFrames':cfg['frameCount']})
 if overrides:cfg['modelOverrides']=overrides
 else:cfg.pop('modelOverrides',None)
path.write_text('window.StreetEffectsData='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n','utf8');print(json.dumps({'measuredModels':len(lookup),'differences':different}))
