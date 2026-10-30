"""Pack21 drawn skin hit frames; publish only after a SHA-bound native trial."""
import argparse, hashlib, io, json, math
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
def read(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');a=p.parse_args()
folder=ROOT/'art-migration/generation/skin100201-shouji-official21-v1'
if a.publish:
 cfg=read(folder/'candidate.json');proof=read(ROOT/'art-migration/versions/0.88.0/skin-hit-native-runtime.json')
 assert proof['pass'] and proof['candidateSha256']==sha(folder/'candidate.json')
 assert proof['manualVideoReview']=='approved-continuous-single-hit-and-recovery'
 assert sha(GAME/cfg['atlas'])==cfg['atlasSha256']
 cfg['review']='native-ordinary-ez-21frame-hit-validated; actual-battle-trigger-pending'
 cfg['nativeRuntimeAuditPath']='art-migration/versions/0.88.0/skin-hit-native-runtime.json'
 cfg['nativeRuntimeAuditSha256']=sha(ROOT/cfg['nativeRuntimeAuditPath'])
 dataPath=GAME/'street-body-data.js';d=json.loads(dataPath.read_text('utf8').split('=',1)[1].strip().rstrip(';'))
 old=next(c for c in d['characters'] if c['id']==2);before=json.dumps(old,sort_keys=True)
 d.setdefault('skins',{})['100201']=cfg;d['version']='0.88.0'
 assert json.dumps(next(c for c in d['characters'] if c['id']==2),sort_keys=True)==before
 dataPath.write_text('window.StreetBodyData='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n','utf8')
 print(json.dumps({'published':100201,'action':'shouji','baseHero2Unchanged':True}));raise SystemExit()
assert not folder.exists(),'Keep existing candidate immutable; review or use a new revision'
plan=read(ROOT/'outputs/street-reskin/skin100201-shouji-official21-review/assembly-plan.json')
assert plan['sourceFrames']==plan['nativeFrames']==21 and plan['mapping']==list(range(21))
images=[];sources=[];bounds=[]
for index in range(21):
 srcFolder=ROOT/plan['sources'][index//7];review=read(srcFolder/'strip-qa.json')
 assert review['manualReview']=='approved-drawn-source-for-native-trial'
 assert sha(srcFolder/'official-source.png')==review['sourceSha256']
 path=srcFolder/f'frame-{index:02}.png';im=Image.open(path).convert('RGBA')
 row=next(r for r in review['frames'] if r['frame']==index)
 assert hashlib.sha256(im.tobytes()).hexdigest()==row['rgbaSha256']
 assert row['preparedFoot']==[384,680] and im.size==(768,768)
 # Remove only nearly transparent export noise; preserve the generated matte.
 im.putalpha(im.getchannel('A').point(lambda v:0 if v<9 else v))
 box=im.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();assert box
 images.append(im);bounds.append(box);sources.append({'frame':index,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'stripReviewSha256':sha(srcFolder/'strip-qa.json')})
assert len({r['sha256'] for r in sources})==21
box=[min(b[0] for b in bounds)-2,min(b[1] for b in bounds)-2,max(b[2] for b in bounds)+2,max(b[3] for b in bounds)+2]
assert box[0]>4 and box[1]>4 and box[2]<764 and box[3]<764
size=[round((box[2]-box[0])*256/(box[3]-box[1])),256]
atlas=Image.new('RGBA',(7*(size[0]+4),3*(size[1]+4)));rects=[]
for i,im in enumerate(images):
 tile=im.crop(box).resize(size,Image.Resampling.LANCZOS);x=i%7*(size[0]+4)+2;y=i//7*(size[1]+4)+2
 atlas.paste(tile,(x,y));rects.append({'x':x,'y':y,'w':size[0],'h':size[1]})
encoded=io.BytesIO();atlas.save(encoded,format='WEBP',lossless=True,method=6);digest=hashlib.sha256(encoded.getvalue()).hexdigest()
target=GAME/f'assets/street/skins/100201/actions/shouji-{digest[:16]}.webp';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(encoded.getvalue())
folder.mkdir();sourceSignature=hashlib.sha256(''.join(r['sha256'] for r in sources).encode()).hexdigest()
alpha={'manualReview':'approved','scope':'All21 official transparent source frames inspected on light/dark contacts, generated alpha preserved with only<9 noise removal. No native motion/battle approval.','sourceSignature':sourceSignature,'sourceFrames':sources,'atlasSha256':digest,'runtimeIntegrated':False}
(folder/'alpha-qa.json').write_text(json.dumps(alpha,indent=2)+'\n','utf8')
audit=ROOT/'art-migration/skin-migration/100201/native-events.json';native=[r for r in read(audit)['records'] if r['action']=='shouji']
assert len(native)==2 and all(r['durationFrames']==21 and abs(r['fps']-30)<.00001 and not r['events'] for r in native)
cfg={'id':100201,'heroId':2,'skinCode':100201,'armature':'hero_skin_002_01','models':[r['model'] for r in native],'atlas':target.relative_to(GAME).as_posix(),'atlasSha256':digest,'frames':rects,'root':[384,680],'crop':box,'bodyHeight':520,'actions':{'shouji':{'fps':30,'nativeDurationFrames':21,'frameMap':list(range(21)),'nativeEvents':[]}},'source':folder.relative_to(ROOT).as_posix(),'alphaReviewSha256':sha(folder/'alpha-qa.json'),'nativeEventAuditPath':audit.relative_to(ROOT).as_posix(),'nativeEventAuditSha256':sha(audit),'sourceSignature':sourceSignature,'review':'independent-hit-native-trial-required','completeSkin':False}
(folder/'candidate.json').write_text(json.dumps(cfg,indent=2)+'\n','utf8')
(folder/'assembly.json').write_text(json.dumps({'skinCode':100201,'sources':sources,'atlasSize':list(atlas.size),'decodedBytes':atlas.width*atlas.height*4,'sourceFrames':21,'nativeFrames':21,'frameMap':list(range(21)),'sourceSignature':sourceSignature,'candidateSha256':sha(folder/'candidate.json'),'runtimeIntegrated':False},indent=2)+'\n','utf8')
print(json.dumps({'candidate':str(folder/'candidate.json'),'atlas':str(target),'atlasSize':list(atlas.size),'decodedBytes':atlas.width*atlas.height*4}))
