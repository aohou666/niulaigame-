"""Extend one independent skin with a fully drawn action, preserving older tiles."""
import argparse,copy,hashlib,io,json,math
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
def read(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def loadjs(p):return json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'))
def prepare(a):
 plan=read(ROOT/a.plan);action=plan['action'];count=plan['nativeFrames'];assert count==45 and action=='gongji' and plan['nativeMapping']==list(range(count))
 folder=ROOT/a.out;assert not (folder/'candidate.json').exists(),'Preserve an already built candidate'
 data=loadjs(GAME/'street-body-data.js');runtimeOld=data['skins']['100201'];old=read(ROOT/a.base) if a.base else runtimeOld;assert set(old['actions'])=={'shouji'} and old['armature']=='hero_skin_002_01'
 assert sha(GAME/old['atlas'])==old['atlasSha256'];oldAlpha=read(ROOT/old['source']/'alpha-qa.json');assert oldAlpha['manualReview']=='approved';assert oldAlpha['atlasSha256']==old['atlasSha256']
 with Image.open(GAME/old['atlas']) as atlas:previous=[atlas.convert('RGBA').crop((r['x'],r['y'],r['x']+r['w'],r['y']+r['h'])) for r in old['frames']]
 images=[];sourceRows=[];bounds=[]
 for index in range(count):
  sourceRef=plan['frameSources'][index] if plan.get('frameSources') else {'folder':plan['sourceFrameFolders'][index] if plan.get('sourceFrameFolders') else plan['sourceFolders'][index//7],'frame':index};sourceIndex=sourceRef['frame'];srcFolder=ROOT/sourceRef['folder'];q=read(srcFolder/'strip-qa.json');assert q['manualReview']=='approved-drawn-source-for-native-trial';assert sha(srcFolder/'official-source.png')==q['sourceSha256']
  row=next(r for r in q['frames'] if r['frame']==sourceIndex);path=srcFolder/f'frame-{sourceIndex:02}.png';im=Image.open(path).convert('RGBA');assert im.size==(768,768) and row['preparedFoot']==plan['root'];assert hashlib.sha256(im.tobytes()).hexdigest()==row['rgbaSha256']
  im.putalpha(im.getchannel('A').point(lambda n:0 if n<9 else n));box=im.getchannel('A').point(lambda n:255 if n>16 else 0).getbbox();assert box;images.append(im);bounds.append(box);sourceRows.append({'action':action,'sourceFrame':sourceIndex,'nativeFrame':index,'atlasFrame':len(previous)+index,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'stripReviewSha256':sha(srcFolder/'strip-qa.json')})
 box=[min(b[0] for b in bounds)-2,min(b[1] for b in bounds)-2,max(b[2] for b in bounds)+2,max(b[3] for b in bounds)+2];assert box[0]>4 and box[1]>4 and box[2]<764 and box[3]<764
 size=(round((box[2]-box[0])*256/(box[3]-box[1])),256);tiles=previous+[im.crop(box).resize(size,Image.Resampling.LANCZOS) for im in images]
 columns=8;cw=max(im.width for im in tiles)+4;ch=max(im.height for im in tiles)+4;atlas=Image.new('RGBA',(columns*cw,math.ceil(len(tiles)/columns)*ch));rects=[]
 for index,tile in enumerate(tiles):
  x=index%columns*cw+2;y=index//columns*ch+2;atlas.paste(tile,(x,y));rects.append({'x':x,'y':y,'w':tile.width,'h':tile.height})
 output=io.BytesIO();atlas.save(output,format='WEBP',lossless=True,method=6,exact=True);blob=output.getvalue();digest=hashlib.sha256(blob).hexdigest();decoded=Image.open(io.BytesIO(blob)).convert('RGBA')
 for r,im in zip(rects,previous):assert decoded.crop((r['x'],r['y'],r['x']+r['w'],r['y']+r['h'])).tobytes()==im.tobytes(),'Older approved action pixels changed'
 sources=[dict(row,action='shouji',atlasFrame=i) for i,row in enumerate(oldAlpha['sourceFrames'])]+sourceRows;assert len({r['sha256'] for r in sources})==len(tiles)
 signature=hashlib.sha256(''.join(r['sha256'] for r in sources).encode()).hexdigest();folder.mkdir(parents=True,exist_ok=True);target=GAME/f'assets/street/skins/100201/actions/shouji-gongji-{digest[:16]}.webp';target.write_bytes(blob)
 alpha={'manualReview':'approved','scope':'Source matte/props inspected; all drawn source frames only. Native timing/event/battle approval is separate. Earlier shouji tiles copied pixel-exact.','sourceFrames':sources,'sourceSignature':signature,'atlasSha256':digest,'inheritedAtlas':old['atlas'],'inheritedAtlasSha256':old['atlasSha256'],'inheritedTileCount':len(previous),'runtimeIntegrated':False};(folder/'alpha-qa.json').write_text(json.dumps(alpha,indent=2)+'\n','utf8')
 cfg=copy.deepcopy(old);cfg['inheritedBody']=old
 if runtimeOld['atlasSha256']!=old['atlasSha256']:cfg.update(supersededDraftAtlasSha256=runtimeOld['atlasSha256'],supersededDraftAtlas=runtimeOld['atlas'])
 for key in ['nativeRuntimeAuditPath','nativeRuntimeAuditSha256','battleRuntimeAuditPath','battleRuntimeAuditSha256']:cfg.pop(key,None)
 cfg.update(atlas=target.relative_to(GAME).as_posix(),atlasSha256=digest,frames=rects,source=folder.relative_to(ROOT).as_posix(),alphaReviewSha256=sha(folder/'alpha-qa.json'),sourceSignature=signature,review='independent-actions-native-trial-required',completeSkin=False)
 audit=read(ROOT/cfg['nativeEventAuditPath']);native=[r for r in audit['records'] if r['action']==action];assert len(native)==2 and {r['durationFrames'] for r in native}=={count} and all(r['events']==native[0]['events'] for r in native);offset=len(previous)
 cfg['actions'][action]={'fps':30,'nativeDurationFrames':count,'frameMap':list(range(offset,offset+count)),'nativeEvents':native[0]['events'],'nativeImpactFrame':18,'sourceImpactFrame':offset+18,'nativeRecoveryFrame':plan.get('recoveryNativeFrame',44),'sourceRecoveryFrame':offset+plan.get('recoveryNativeFrame',44),'geometry':{'root':plan['root'],'crop':box,'bodyHeight':plan['bodyHeight']}}
 (folder/'candidate.json').write_text(json.dumps(cfg,indent=2)+'\n','utf8');(folder/'assembly.json').write_text(json.dumps({'action':action,'nativeFrames':count,'newSourceFrames':count,'inheritedFrames':len(previous),'atlasSize':list(atlas.size),'decodedBytes':atlas.width*atlas.height*4,'candidateSha256':sha(folder/'candidate.json'),'sourceSignature':signature,'unusedSourceTail':plan['unusedTailFrames'],'oldTilesByteIdentical':True,'runtimeIntegrated':False},indent=2)+'\n','utf8');print(json.dumps({'candidate':str(folder/'candidate.json'),'frames':len(tiles),'newFrames':count,'decodedBytes':atlas.width*atlas.height*4}))
def publish(a):
 folder=ROOT/a.out;cfg=read(folder/'candidate.json');proof=read(ROOT/a.proof);assert proof['pass'] and proof['manualVideoReview']=='approved-continuous-native-actions';assert proof['candidateSha256']==sha(folder/'candidate.json') and proof['atlasSha256']==cfg['atlasSha256'];assert set(proof['actions'])==set(cfg['actions'])
 dataPath=GAME/'street-body-data.js';data=loadjs(dataPath);assert data['skins']['100201']['atlasSha256'] in [cfg['inheritedBody']['atlasSha256'],cfg.get('supersededDraftAtlasSha256')],'Runtime base changed since candidate preparation';assert set(data['skins']['100201']['actions'])<=set(cfg['actions']),'Publishing would erase an existing action';before=json.dumps(data['characters'],sort_keys=True);cfg.update(nativeRuntimeAuditPath=a.proof,nativeRuntimeAuditSha256=sha(ROOT/a.proof),review='approved-native-actions-independent-skin-incomplete');data['skins']['100201']=cfg;data['version']=a.version;assert json.dumps(data['characters'],sort_keys=True)==before;dataPath.write_text('window.StreetBodyData='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n','utf8');print(json.dumps({'published':100201,'actions':list(cfg['actions']),'completeSkin':False}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','publish']);p.add_argument('--plan');p.add_argument('--base');p.add_argument('--out',required=True);p.add_argument('--proof');p.add_argument('--version');a=p.parse_args();(prepare if a.mode=='prepare' else publish)(a)
