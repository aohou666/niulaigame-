"""Prepare fully sourced native-body bindings; no whole-skin completion claim."""
import copy,json,shutil
from pathlib import Path
from street_packed_fx import sha,verify_container
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
FOLDER=ROOT/'art-migration/generation/skin100201-native-body107-packed-trial-v2'
OUT=ROOT/'art-migration/generation/skin100201-native-body-production-v1'
assert not OUT.exists(),'Preserve earlier preparation revisions'
def loadjs(path):return json.loads(path.read_text('utf8').split('=',1)[1].strip().rstrip(';'))
live=loadjs(GAME/'street-art-data.js')
trial=json.loads((FOLDER/'candidate-containers.json').read_text('utf8'))
OUT.mkdir(parents=True)
sources=trial[0]['bodySources']
qa={'manualReview':'approved-native-body-parts-for-native-trial','productionIntegrated':False,'skinComplete':False,'sourceTextures':107,'tiles':[{'name':s['nativeRegion'],'path':s['sourcePath'],'sha256':s['sourceSha256']} for s in sources],'scope':'Independent head/garments/vehicle/hands/props/ornaments source parts reviewed; native motion and actual battle have separate proof. This does not approve all shared active-skill/UI assets.'}
qaPath=OUT/'body-source-review.json';qaPath.write_text(json.dumps(qa,ensure_ascii=False,indent=2),'utf8')
proofPaths={'motion':'native-motion/motion-candidate.json','baseline':'native-motion/motion-baseline.json','ui':'native-ui/native-ui-runtime.json','battle':'native-battle-skill-banner/runtime.json','hurtBattle':'native-battle/runtime.json','performance':'native-performance.json'}
proofs={k:{'path':(FOLDER/v).relative_to(ROOT).as_posix(),'sha256':sha((FOLDER/v).read_bytes())} for k,v in proofPaths.items()}
entries=[]
for candidate in trial:
 previous=next(e for e in live['containers'] if e['originalKey']==candidate['originalKey'])
 assert previous['targetSha256']==candidate['baseTargetSha256']
 model=candidate['originalKey'].removesuffix('_bin')
 target=GAME/f'assets/street/skins/100201/native-body/{model}-{candidate["targetSha256"][:16]}.bin'
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(GAME/candidate['targetPath'],target)
 cfg=copy.deepcopy(candidate);cfg.pop('trialOnly',None)
 cfg.update({'originalPath':previous['originalPath'],'originalSha256':previous['originalSha256'],'targetKey':'street_'+model+'_full_native_bin','targetPath':target.relative_to(GAME).as_posix(),'skinCode':100201,'nativeBodyReplacement':True,'completeContainerReplaced':True,'changedRegions':candidate['newBodyRegions']+previous['changedRegions'],'inheritedReplacements':[previous],'regionReviewPath':qaPath.relative_to(ROOT).as_posix(),'regionReviewSha256':sha(qaPath.read_bytes()),'nativeBodyProofs':proofs,'scope':'Full107 independently drawn body regions and retained40 new child FX on unchanged native all-five-action rig. Other shared active skill effects and independent skin UI/preview are separately tracked; whole skin remains incomplete.'})
 cfg['verification']=verify_container(cfg);entries.append(cfg)
(OUT/'candidate-containers.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'prepared':len(entries),'regionsEach':147,'bodySourcesEach':107,'productionIntegrated':False}))
