"""Publish a verified independent skin idle without rewriting any base hero."""
import argparse, copy, hashlib, json
from pathlib import Path
from street_atomic import atomic_write_bytes, atomic_write_text
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('--native-audit',type=Path,required=True);p.add_argument('--matte-job',type=Path,required=True);p.add_argument('--version',required=True);a=p.parse_args()
def read(path):return json.loads(path.read_text('utf8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
c=read(a.candidate/'candidate.json');sid=str(c['skinCode']);hid=str(c['heroId']);fingerprint=digest(a.candidate/'candidate.json')
design=read(a.matte_job/'idle-design.json');alphaFile=a.matte_job/'alpha-qa.json';alpha=read(alphaFile);sourceQaFile=ROOT/design['sourceBodyJob']/'body-qa.json';sourceQa=read(sourceQaFile)
assert design['skinCode']==int(sid) and design['heroId']==int(hid)
assert alpha['manualReview']=='approved' and alpha['sourceSignature']==c['sourceSignature']==sourceQa['sourceSignature']
assert alpha['alphaOutputSignature']==c['alphaOutputSignature'] and sourceQa['manualTemporalReview']=='approved-continuous'
for name in ['verification.json','skin-atlas-detail-basic-runtime.json','skin-raw-detail-basic-runtime.json','skin-atlas-detail-ez-runtime.json','skin-atlas-formation-basic-runtime.json']:
 proof=read(a.candidate/name);assert proof['pass'] and proof['candidateSha256']==fingerprint,'Missing/stale proof: '+name
 assert proof['sourceSignature']==c['sourceSignature'],'Proof belongs to different motion'
audit=read(a.native_audit);assert audit['complete']
for model in c['models']:
 row=next(r for r in audit['records'] if r['model']==model and r['action']=='daiji')
 assert row['durationFrames']==c['nativeIdleFrames'] and abs(row['fps']-c['nativeFps'])<.0001 and not row['events'],'Native idle timeline differs'
assert abs(c['frameCount']/c['fps']-c['nativeIdleFrames']/c['nativeFps'])<.000001
path=GAME/'character-idle-data.js';idle=json.loads(path.read_text('utf8').split('=',1)[1].strip().rstrip(';'));base=copy.deepcopy(idle['heroes']);assert hid in base
dest=GAME/'assets/street/skins'/sid/('idle-'+c['sourceSignature'][:16]);dest.mkdir(parents=True,exist_ok=True)
for row in c['fallback']+[r for pack in c['profiles'].values() for r in pack['pages']]:
 payload=(a.candidate/row['file']).read_bytes();assert hashlib.sha256(payload).hexdigest()==row['sha256'];target=dest/row['file']
 if target.exists():assert digest(target)==row['sha256'],'Immutable asset collision'
 else:atomic_write_bytes(target,payload)
profiles=copy.deepcopy(c['profiles'])
for pack in profiles.values():
 for page in pack['pages']:page['url']=(dest/page.pop('file')).relative_to(GAME).as_posix()
 pack['decodedBytes']=sum(r['width']*r['height']*4 for r in pack['pages'])
plan=read(ROOT/'art-migration/skin-migration'/sid/'plan.json')
cfg={'id':int(sid),'skinCode':int(sid),'heroId':int(hid),'name':plan['originalName'],'models':c['models'],'materialId':'skin'+sid+'-'+c['sourceSignature'][:16],
 'frameCount':c['frameCount'],'width':512,'height':512,'crop':c['crop'],'bodyHeight':c['bodyHeight'],'fps':c['fps'],
 'baseUrl':dest.relative_to(GAME).as_posix()+'/','files':[r['file'] for r in c['fallback']],'filesSha256':[r['sha256'] for r in c['fallback']],
 'atlas':{'profiles':profiles,'frameCount':c['frameCount'],'crop':c['crop'],'sourceSequenceSha256':c['sourceSignature']},
 'sourceSequenceSha256':c['sourceSignature'],'nativeIdleFrames':c['nativeIdleFrames'],'nativeFps':c['nativeFps'],
 'nativeAuditPath':a.native_audit.relative_to(ROOT).as_posix() if a.native_audit.is_absolute() else a.native_audit.as_posix(),'nativeAuditSha256':digest(a.native_audit),
 'sourceMatteJob':a.matte_job.relative_to(ROOT).as_posix() if a.matte_job.is_absolute() else a.matte_job.as_posix(),'alphaReviewSha256':digest(alphaFile),'rawReviewSha256':digest(sourceQaFile),
 'candidateSha256':fingerprint,'review':'candidate-native-loop-validated-live-review-pending','completeSkin':False}
idle.setdefault('skins',{})[sid]=cfg;idle['version']=a.version;assert idle['heroes']==base,'Base hero changed'
atomic_write_text(path,'window.CharacterIdleData='+json.dumps(idle,ensure_ascii=False,separators=(',',':'))+';\n')
print(json.dumps({'skinCode':int(sid),'sourceFrames':c['frameCount'],'nativeLoopSeconds':c['nativeIdleFrames']/c['nativeFps'],'pages':sum(len(p['pages']) for p in profiles.values()),'baseHeroesPreserved':True,'completeSkin':False}))
