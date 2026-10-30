"""Verify every promoted street image, atlas frame, root and native frame mapping."""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
def loadjs(p):return json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'))
def verify():
 errors=[];images=0;frames=0;characters=[]
 artData=loadjs(GAME/'street-art-data.js');packedRegions=[]
 for r in artData['resources']:
  try:
   p=GAME/r['targetPath'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['targetSha256'],'digest mismatch'
   with Image.open(p) as im:assert list(im.size)==list(r['size']),'dimensions mismatch';assert im.getbbox() is not None,'empty image'
   images+=1
  except Exception as e:errors.append({'resource':r['originalKey'],'error':str(e)})
 for r in artData.get('containers',[]):
  try:
   from street_packed_fx import verify_container
   packedRegions.append(verify_container(r))
  except Exception as e:errors.append({'container':r['originalKey'],'error':str(e)})
 body=loadjs(GAME/'street-body-data.js') if (GAME/'street-body-data.js').exists() else {'characters':[]}
 auditPath=ROOT/'art-migration/native-action-events.json';nativeAudit=json.loads(auditPath.read_text('utf8')) if auditPath.exists() else None;nativeRows={(r['model'],r['action']):r for r in nativeAudit['records']} if nativeAudit else {};nativeChecks=0
 skinBodies=body.get('skins',{})
 for key,cfg in body.get('nativeSkins',{}).items():
  try:
   assert key==str(cfg['id'])==str(cfg['skinCode']) and cfg['renderer']=='native-skeletal'
   assert key not in skinBodies,'Native skin still has raster body override'
   idleData=loadjs(GAME/'character-idle-data.js');assert key not in idleData.get('skins',{}),'Native skin still has raster idle override'
   assert cfg['fps']==30 and cfg['actions']=={'daiji':198,'gongji':45,'jineng':46,'shouji':21,'paobu':16}
   assert cfg['bodyRegions']==107 and cfg['childFXRegions']==40
   for originalKey,digest in cfg['containers'].items():
    entry=next(r for r in artData['containers'] if r['originalKey']==originalKey)
    assert entry.get('nativeBodyReplacement') and entry['targetSha256']==digest
   assert set(cfg['containers'])=={m+'_bin' for m in cfg['models']}
  except Exception as e:errors.append({'nativeSkin':key,'error':str(e)})
 for key,cfg in skinBodies.items():
  if str(cfg.get('skinCode'))!=key or cfg.get('id')!=cfg.get('skinCode') or not cfg.get('armature'):
   errors.append({'skin':key,'error':'independent body requires its own id/skinCode and explicit armature'})
 for cfg in body['characters']+list(skinBodies.values()):
  try:
   if cfg.get('atlasSha256'):assert hashlib.sha256((GAME/cfg['atlas']).read_bytes()).hexdigest()==cfg['atlasSha256'],'atlas digest mismatch'
   if cfg.get('alphaReviewSha256'):
    alphaFile=ROOT/cfg['source']/'alpha-qa.json';assert hashlib.sha256(alphaFile.read_bytes()).hexdigest()==cfg['alphaReviewSha256'],'alpha review digest mismatch';assert json.loads(alphaFile.read_text('utf8'))['manualReview']=='approved','alpha sequence not manually approved'
    if cfg.get('skinCode'):
     alphaReview=json.loads(alphaFile.read_text('utf8'));assert alphaReview['sourceSignature']==cfg['sourceSignature'] and alphaReview['atlasSha256']==cfg['atlasSha256'],'independent source/atlas provenance differs'
     assert len(alphaReview['sourceFrames'])==len(cfg['frames'])==len({r['sha256'] for r in alphaReview['sourceFrames']}),'independent drawn frame count differs'
     for row in alphaReview['sourceFrames']:assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'independent source frame changed'
   if cfg.get('nativeRuntimeAuditSha256'):
    proofFile=ROOT/cfg['nativeRuntimeAuditPath'];assert hashlib.sha256(proofFile.read_bytes()).hexdigest()==cfg['nativeRuntimeAuditSha256'],'native runtime proof changed'
    proof=json.loads(proofFile.read_text('utf8'));assert proof['pass'],'independent native animation failed'
    if proof['manualVideoReview']=='approved-continuous-native-actions':
     assert proof['atlasSha256']==cfg['atlasSha256'] and set(proof['actions'])==set(cfg['actions']),'native action proof scope differs'
     for action,ref in proof['actions'].items():
      actionFile=ROOT/ref['path'];assert hashlib.sha256(actionFile.read_bytes()).hexdigest()==ref['sha256'],'native action report digest differs';actionProof=json.loads(actionFile.read_text('utf8'));assert actionProof['pass'] and actionProof['action']==action and actionProof['atlasSha256']==cfg['atlasSha256'] and actionProof['candidateSha256']==proof['candidateSha256'],'native action report package differs'
      assert actionProof['manualFrameSequenceReview']=='approved-all-native-frames-and-source-sequence' and len(actionProof['checks'])==len(cfg['actions'][action]['frameMap'])*len(cfg['models']),'native mapped frame coverage incomplete'
    else:assert proof['manualVideoReview']=='approved-continuous-single-hit-and-recovery' and set(cfg['actions'])=={'shouji'},'legacy hit-only proof cannot approve added actions'
   if cfg.get('battleRuntimeAuditSha256'):
    proofFile=ROOT/cfg['battleRuntimeAuditPath'];assert hashlib.sha256(proofFile.read_bytes()).hexdigest()==cfg['battleRuntimeAuditSha256'],'independent battle proof changed'
    proof=json.loads(proofFile.read_text('utf8'));assert proof['pass'] and proof['mainSaveUnchanged'] and proof['isolatedSaveRestored'],'isolated battle proof incomplete'
    assert proof['equip']['dermaCode']==cfg['skinCode'] and any(e['dermaCode']==cfg['skinCode'] for e in proof['payload']['allies']),'equipped skin not carried into battle'
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
    if seq.get('geometry'):
     g=seq['geometry'];assert g['bodyHeight']>0 and len(g['root'])==2 and len(g['crop'])==4 and g['crop'][2]>g['crop'][0] and g['crop'][3]>g['crop'][1],'invalid action geometry'
    if seq.get('alphaReviewSha256'):
     proof=ROOT/seq['source']/'alpha-qa.json';assert hashlib.sha256(proof.read_bytes()).hexdigest()==seq['alphaReviewSha256'] and json.loads(proof.read_text('utf8'))['manualReview']=='approved','action alpha review mismatch'
    if seq.get('battleRuntimeAuditSha256'):
     battleFile=ROOT/seq['battleRuntimeAuditPath'];assert hashlib.sha256(battleFile.read_bytes()).hexdigest()==seq['battleRuntimeAuditSha256'],'action battle report digest differs';battleProof=json.loads(battleFile.read_text('utf8'));assert battleProof['pass'] and battleProof['action']==action and battleProof['mainSaveUnchanged'] and battleProof['isolatedSaveRestored'],'action battle proof incomplete';assert battleProof['runtimeAtlas']['sha256']==cfg['atlasSha256'] and battleProof['runtimeAtlas']['path']==cfg['atlas'],'action battle loaded another atlas'
     if seq.get('nativeRecoveryFrame') is not None:assert any(r['nativeFrame']>=seq['nativeRecoveryFrame'] for r in battleProof['recoverySnapshot']),'action recovery not observed in real battle'
    if seq.get('nativeImpactFrame') is not None:assert seq['frameMap'][seq['nativeImpactFrame']]==seq['sourceImpactFrame'],'impact mapping mismatch'
    for mark in seq.get('eventAnchors',[]):assert seq['frameMap'][mark['nativeFrame']]==mark['sourceFrame'],'multi-event mapping mismatch'
   if cfg.get('nativeEventAuditSha256'):
    cfgAuditPath=ROOT/cfg.get('nativeEventAuditPath','art-migration/native-action-events.json');cfgAudit=json.loads(cfgAuditPath.read_text('utf8'));cfgNativeRows={(r['model'],r['action']):r for r in cfgAudit['records']}
    assert cfgAudit['complete'] and hashlib.sha256(cfgAuditPath.read_bytes()).hexdigest()==cfg['nativeEventAuditSha256'],'native event audit provenance mismatch'
    supplementalRows={}
    if cfg.get('supplementalNativeActionAuditPath'):
     supplementalPath=ROOT/cfg['supplementalNativeActionAuditPath'];assert hashlib.sha256(supplementalPath.read_bytes()).hexdigest()==cfg['supplementalNativeActionAuditSha256'],'supplemental audit provenance mismatch';supplementalAudit=json.loads(supplementalPath.read_text('utf8'));assert supplementalAudit['complete'];supplementalRows={(r['model'],r['action']):r for r in supplementalAudit['records']}
    for model in cfg['models']:
     for action,base in cfg['actions'].items():
      seq=cfg.get('modelActionOverrides',{}).get(model,{}).get(action,base);native=(supplementalRows if (model,action) in supplementalRows else cfgNativeRows)[(model,action)];assert len(seq['frameMap'])==native['durationFrames'] and abs(seq['fps']-native['fps'])<.0001,'native clock differs'
      assert [(e['name'],e['frame0']) for e in seq.get('nativeEvents',[])]==[(e['name'],e['frame0']) for e in native['events'] if e['name'] in ['pia','zd']],'native event metadata differs';nativeChecks+=1
   characters.append({'hero':cfg['id'],'skinCode':cfg.get('skinCode'),'frames':len(cfg['frames']),'distinctFrames':len(hashes),'actions':list(cfg['actions']),'quarantinedActions':cfg.get('qualityQuarantineActions',[]),'temporalQuality':cfg.get('temporalQuality','not-revalidated'),'supplemental':cfg.get('supplemental',False)})
  except Exception as e:errors.append({'hero':cfg['id'],'error':str(e)})
 effects=[];effectBindings=set()
 effectFile=GAME/'street-effects-data.js'
 for cfg in loadjs(effectFile)['effects'] if effectFile.exists() else []:
  try:
   for model in cfg['models']:
    binding=(model,cfg.get('armature'));assert binding not in effectBindings,'duplicate model/armature effect binding';effectBindings.add(binding)
    assert not model.startswith('hero_') or cfg.get('armature'),'character model requires explicit effect armature'
   assert hashlib.sha256((GAME/cfg['atlas']).read_bytes()).hexdigest()==cfg['atlasSha256'],'effect atlas digest mismatch'
   assert len(cfg['frames'])==len(cfg['sampling'])==cfg['frameCount']==cfg['sourceOriginalFrames'],'effect native frame count differs'
   assert cfg['nativeTimelineRetained'] and cfg['fps']>0
   assert cfg['sampling']==sorted(cfg['sampling']) and all(0<=n<cfg['sourceGeneratedFrames'] for n in cfg['sampling']),'effect source order/index invalid'
   if cfg.get('kind')!='loop' and cfg.get('originalPeakFrame') is not None:assert cfg['sampling'][cfg.get('retargetPeakFrame',cfg['originalPeakFrame'])]==cfg['generatedPeakFrame'],'effect peak phase mismatch'
   hashes=set();nonempty=0
   with Image.open(GAME/cfg['atlas']) as im:
    assert list(im.size)==cfg['atlasSize']
    for f in cfg['frames']:
     assert min(f['x'],f['y'])>=0 and f['x']+f['w']<=im.width and f['y']+f['h']<=im.height,'effect tile outside atlas'
     tile=im.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']));hashes.add(hashlib.sha256(tile.tobytes()).hexdigest());nonempty+=bool(tile.convert('RGB').getbbox())
   assert nonempty>3 and len(hashes)>4,'effect motion empty/static'
   source=ROOT/cfg['generationJob'];qa=source/'effect-qa.json'
   if qa.exists():review=json.loads(qa.read_text('utf8'));assert review['manualReview']=='approved' and not review['croppedFrames'],'unapproved/cropped effect'
   if cfg.get('nativeEventAuditPath'):
    nativeFile=ROOT/cfg['nativeEventAuditPath'];assert hashlib.sha256(nativeFile.read_bytes()).hexdigest()==cfg['nativeEventAuditSha256'],'effect native audit digest mismatch'
    nativeData=json.loads(nativeFile.read_text('utf8'));assert nativeData['complete'];nativeRows={r['model']:r for r in nativeData['records']}
    for model in cfg['models']:
     if cfg.get('armature'):
      matches=[r for r in nativeData['records'] if r['model']==model and (r.get('armature') or r.get('action'))==cfg['armature']];assert len(matches)==1,'missing/ambiguous effect armature audit';row=matches[0]
     else:row=nativeRows[model]
     seq=cfg.get('modelOverrides',{}).get(model,cfg);assert seq['frameCount']==row['durationFrames'] and abs(seq['fps']-row['fps'])<.0001,'effect variant native clock mismatch'
     assert cfg['nativeModels'][model]['events']==row['events'],'effect authored event metadata mismatch'
     mapping=seq.get('frameMap',list(range(cfg['frameCount'])));assert len(mapping)==seq['frameCount'] and mapping==sorted(mapping) and min(mapping)>=0 and max(mapping)<cfg['frameCount'],'effect variant frame mapping invalid'
   effects.append({'id':cfg['id'],'models':len(cfg['models']),'armature':cfg.get('armature'),'nativeFrames':cfg['frameCount'],'nonemptyFrames':nonempty,'distinctFrames':len(hashes)})
  except Exception as e:errors.append({'effect':cfg['id'],'error':str(e)})
 return {'images':images,'bodyAtlasFrames':frames,'bodyCharacters':characters,'nativeModelActionsChecked':nativeChecks,'effects':effects,'nativePackedRegions':packedRegions,'errors':errors}
if __name__=='__main__':
 r=verify();print(json.dumps(r));raise SystemExit(bool(r['errors']))
