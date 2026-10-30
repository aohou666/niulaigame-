"""Replace explicit native FX texture regions; preserve every skeleton/atlas byte."""
import argparse,hashlib,io,json,struct,zlib
from pathlib import Path
import numpy as np
from PIL import Image
from street_packed_inventory import decode
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
def sha(data):return hashlib.sha256(data).hexdigest()
def chunks(blob):
 assert blob[:3]==bytes([219,189,30]) and blob[6]==0,'Only audited PNG DB bundles supported'
 result=[];pos=12
 for _ in range(3):
  count=struct.unpack_from('<I',blob,pos)[0];pos+=4;result.append(blob[pos:pos+count]);pos+=count
 assert pos==len(blob),'Unexpected extra bundle data'
 return result
def raw(blob,part):return zlib.decompress(part,-15) if blob[4] else part
def verify_container(cfg):
 original=GAME/cfg['originalPath'];target=GAME/cfg['targetPath'];old=original.read_bytes();new=target.read_bytes()
 assert sha(old)==cfg['originalSha256'] and sha(new)==cfg['targetSha256'],'Packed bundle digest differs'
 a=chunks(old);b=chunks(new);assert old[:12]==new[:12] and a[:2]==b[:2],'Native skeleton/atlas bytes changed'
 oldData=decode(original);newData=decode(target);assert oldData['atlas']==newData['atlas']
 oldIm=Image.open(io.BytesIO(oldData['image'])).convert('RGBA');newIm=Image.open(io.BytesIO(newData['image'])).convert('RGBA');assert oldIm.size==newIm.size
 changed=[];regions=oldData['atlas']['SubTexture'];allowed=np.zeros((oldIm.height,oldIm.width),bool)
 for r in regions:
  rect=(r['x'],r['y'],r['x']+r['width'],r['y']+r['height'])
  if oldIm.crop(rect).tobytes()!=newIm.crop(rect).tobytes():changed.append(r['name'])
  if r['name'] in cfg['changedRegions']:
   allowed[rect[1]:rect[3],rect[0]:rect[2]]=True;assert newIm.crop(rect).getchannel('A').getbbox(),'Empty replacement region'
 assert set(changed)==set(cfg['changedRegions']),'Missing or unexpected changed texture region'
 assert np.array_equal(np.asarray(oldIm)[~allowed],np.asarray(newIm)[~allowed]),'Pixels outside declared regions changed'
 for previous in cfg.get('inheritedReplacements',[]):
  verify_container(previous)
  previousImage=Image.open(io.BytesIO(decode(GAME/previous['targetPath'])['image'])).convert('RGBA')
  for name in previous['changedRegions']:
   r=next(r for r in regions if r['name']==name);rect=(r['x'],r['y'],r['x']+r['width'],r['y']+r['height']);assert newIm.crop(rect).tobytes()==previousImage.crop(rect).tobytes(),'Earlier replacement changed'
 qa=ROOT/cfg['regionReviewPath'];assert sha(qa.read_bytes())==cfg['regionReviewSha256'];review=json.loads(qa.read_text('utf8'));assert review['manualReview']=='approved-texture-sequence-for-native-trial'
 for row in review['tiles']:assert sha((ROOT/row['path']).read_bytes())==row['sha256'],'Reviewed source tile changed'
 if cfg.get('nativeRuntimeAuditSha256'):
  proofFile=ROOT/cfg['nativeRuntimeAuditPath'];assert sha(proofFile.read_bytes())==cfg['nativeRuntimeAuditSha256'],'Packed native proof changed';proof=json.loads(proofFile.read_text('utf8'));assert proof['pass'] and proof['manualReview']=='approved-complete-native-loop','Packed animation not manually approved'
  assert any(r['key']==cfg['originalKey'] and r['digest']==cfg['targetSha256'] for r in proof['resourceDigests']),'Native trial did not load this bundle'
 if cfg.get('nativeAnimationReplacement'):
  arm=next(a for a in oldData['skeleton']['armature'] if a['name']==cfg['nativeAnimationReplacement']);textures={display.get('path') or display['name'] for skin in arm.get('skin',[]) for slot in skin.get('slot',[]) for display in slot.get('display',[])}
  assert textures<=set(cfg['changedRegions']),'Animation still references unreplaced textures'
 if cfg.get('sourceProvenanceSha256'):
  provenance=ROOT/cfg['sourceProvenancePath'];assert sha(provenance.read_bytes())==cfg['sourceProvenanceSha256'],'Packed art provenance changed'
  for source in json.loads(provenance.read_text('utf8'))['referenceInputs']:assert sha((ROOT/source['path']).read_bytes())==source['sha256'],'Packed art reference changed'
 if cfg.get('battleRuntimeAuditSha256'):
  proofFile=ROOT/cfg['battleRuntimeAuditPath'];assert sha(proofFile.read_bytes())==cfg['battleRuntimeAuditSha256'],'Packed battle proof changed';proof=json.loads(proofFile.read_text('utf8'));assert proof['pass'] and proof['mainSaveUnchanged'] and proof['isolatedSaveRestored'],'Packed battle proof incomplete'
  assert any(e['dermaCode']==cfg['skinCode'] for e in proof['payload']['allies']),'Packed effect skin not actually equipped'
  assert {name for row in proof['samples'] for name in row['active']}==set(row['name'] for row in review['tiles']),'Actual battle did not visit every replaced texture'
 if cfg.get('projectileBattleRuntimeAuditSha256'):
  proofFile=ROOT/cfg['projectileBattleRuntimeAuditPath'];assert sha(proofFile.read_bytes())==cfg['projectileBattleRuntimeAuditSha256'],'Projectile battle proof changed'
  proof=json.loads(proofFile.read_text('utf8'));assert proof['pass'] and proof['mainSaveUnchanged'] and proof['isolatedSaveRestored']
  assert any(e['dermaCode']==cfg['skinCode'] for e in proof['payload']['allies']),'Projectile skin was not equipped'
  assert any(r['visible'] and r['onStage'] and 'qiu' in r['slots'] for r in proof['projectileSamples']),'Projectile never visible in actual battle'
  assert any(r['key']==cfg['originalKey'] and r['digest']==cfg['targetSha256'] for r in proof['projectileResourceDigests']),'Battle projectile bytes differ'
 complete=set(changed)=={r['name'] for r in regions}
 assert not cfg.get('completeContainerReplaced') or complete,'Claimed whole container still has original textures'
 return {'originalKey':cfg['originalKey'],'imageSize':list(newIm.size),'decodedBytes':newIm.width*newIm.height*4,'changedRegions':changed,'unchangedRegions':len(regions)-len(changed),'skeletonAndAtlasByteIdentical':True,'nativeAnimations':[(arm['name'],[(anim['name'],anim.get('duration',0)) for anim in arm.get('animation',[])]) for arm in oldData['skeleton']['armature']],'completeContainerReplaced':complete}

def prepare(args):
 source=Path(args.source);out=ROOT/args.out;assert not out.exists(),'Use a separate source revision'
 im=Image.open(source).convert('RGBA');assert im.getchannel('A').getextrema()[0]<64
 tiles=[];images=[]
 count=20 if args.effect=='effect_3' else 10;rows=count//5
 for i in range(count):
  x0=round(i%5*im.width/5);x1=round((i%5+1)*im.width/5);y0=round(i//5*im.height/rows);y1=round((i//5+1)*im.height/rows)
  tile=im.crop((x0,y0,x1,y1));alpha=tile.getchannel('A').point(lambda v:0 if v<9 else v);tile.putalpha(alpha);box=alpha.point(lambda v:255 if v>32 else 0).getbbox();assert box
  assert min(box[0],box[1],tile.width-box[2],tile.height-box[3])>=5,f'Tile{i+1} touches edge'
  images.append(tile);tiles.append({'name':f'{args.effect}/{args.effect}_{i+1:02}','sourceCell':[x0,y0,x1,y1],'alphaBounds':list(box)})
 out.mkdir(parents=True);(out/'official-source.png').write_bytes(source.read_bytes())
 for row,tile in zip(tiles,images):
  path=out/(row['name'].split('/')[-1]+'.png');tile.save(path);row['path']=path.relative_to(ROOT).as_posix();row['sha256']=sha(path.read_bytes())
 assert len({r['sha256'] for r in tiles})==count
 review={'skinCode':100201,'effect':args.effect,'nativeFrames':count*2-1,'nativeFps':30,'sourceTextures':count,'sourceSha256':sha(source.read_bytes()),'tiles':tiles,'manualReview':'pending','runtimeIntegrated':False,'provenance':'Official independently drawn ten-texture sequence, native ten-pose composition and local MiniMax material reference. MiniMax full clip rejected, not reused as an approved animation.'}
 (out/'qa.json').write_text(json.dumps(review,indent=2)+'\n','utf8');print(json.dumps({'prepared':str(out),'textures':len(tiles)}))

def build(args):
 qaPath=ROOT/args.review;review=json.loads(qaPath.read_text('utf8'));assert review['manualReview']=='approved-texture-sequence-for-native-trial';assert len(review['tiles'])==review['sourceTextures']
 folder=ROOT/args.out;assert not folder.exists();folder.mkdir(parents=True);entries=[]
 for model,filename in [('hero_skin_002_01','hero_skin_002_01_44129895.bin'),('hero_skin_002_01_ez','hero_skin_002_01_ez_cdeed9df.bin')]:
  original=GAME/'resource/assets/model'/filename;data=decode(original);base=next((e for e in json.loads((ROOT/args.base).read_text('utf8')) if e['originalKey']==model+'_bin'),None) if args.base else None
  if base:verify_container(base)
  baseData=decode(GAME/base['targetPath']) if base else data;image=Image.open(io.BytesIO(baseData['image'])).convert('RGBA');lookup={r['name']:r for r in data['atlas']['SubTexture']};changed=list(base['changedRegions']) if base else []
  for row in review['tiles']:
   source=ROOT/row['path'];assert sha(source.read_bytes())==row['sha256'];tile=Image.open(source).convert('RGBA');tile=tile.crop(tile.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox());r=lookup[row['name']]
   # Native region size/slot transforms remain exact. Fit new art into the old
   # alpha footprint with a bottom anchor; no color filters or invented frames.
   old=Image.open(io.BytesIO(data['image'])).convert('RGBA').crop((r['x'],r['y'],r['x']+r['width'],r['y']+r['height']));box=old.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();assert box
   tile.thumbnail((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS);tile.putalpha(tile.getchannel('A').point(lambda value:round(value*args.opacity)));replacement=Image.new('RGBA',old.size);replacement.alpha_composite(tile,(box[0]+(box[2]-box[0]-tile.width)//2,box[3]-tile.height));image.paste(replacement,(r['x'],r['y']));changed.append(r['name'])
  buf=io.BytesIO();image.save(buf,format='PNG');originalBytes=original.read_bytes();parts=chunks(originalBytes)
  comp=zlib.compressobj(9,zlib.DEFLATED,-15);newImage=comp.compress(buf.getvalue())+comp.flush() if originalBytes[4] else buf.getvalue();newParts=parts[:2]+[newImage]
  packed=originalBytes[:12]+b''.join(struct.pack('<I',len(part))+part for part in newParts);digest=sha(packed);target=GAME/f'assets/street/skins/100201/native-fx/{model}-{review['effect']}-{digest[:16]}.bin';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(packed)
  entry={'originalKey':model+'_bin','originalPath':original.relative_to(GAME).as_posix(),'originalSha256':sha(originalBytes),'targetKey':'street_'+model+'_'+review['effect']+'_bin','targetPath':target.relative_to(GAME).as_posix(),'targetSha256':digest,'type':'bin','skinCode':100201,'technicalAlphaScale':args.opacity,'changedRegions':changed,'regionReviewPath':qaPath.relative_to(ROOT).as_posix(),'regionReviewSha256':sha(qaPath.read_bytes()),'completeContainerReplaced':False,'scope':'Only explicitly listed FX textures; native skeleton/atlas bytes and other regions retained. Original body regions remain unreplaced.'}
  if base:entry['inheritedReplacements']=[base]
  entry['verification']=verify_container(entry);entries.append(entry)
 (folder/'candidate-containers.json').write_text(json.dumps(entries,indent=2)+'\n','utf8');print(json.dumps({'containers':len(entries),'changedPerContainer':[len(e['changedRegions']) for e in entries]}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','build']);p.add_argument('--source');p.add_argument('--review');p.add_argument('--out',required=True);p.add_argument('--effect',choices=['effect_1','effect_2','effect_3'],default='effect_1');p.add_argument('--base');p.add_argument('--opacity',type=float,default=1);args=p.parse_args();assert 0<args.opacity<=1;(prepare if args.mode=='prepare' else build)(args)
