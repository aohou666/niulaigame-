"""Pack new flight/13 impact phases/glow, with a single impact scale."""
import io,json,struct,zlib
from pathlib import Path
from PIL import Image
from street_packed_fx import chunks,sha,verify_container
from street_packed_inventory import decode
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
SOURCE=ROOT/'art-migration/generation/skin100201-active15-official-v1'
OUT=ROOT/'art-migration/generation/skin100201-active15-native-v3'
assert not OUT.exists(),'Use a distinct revision, never overwrite failed art'
OUT.mkdir(parents=True)
source=json.loads((SOURCE/'source-qa.json').read_text('utf8'));tiles=[]
for row in source['cells']:
 index=row['index'];name='飞行' if index==0 else '光晕' if index==14 else '碰撞'+str(index)
 image=Image.open(ROOT/row['path']).convert('RGBA');image.putalpha(image.getchannel('A').point(lambda a:0 if a<=8 else a));
 if index==14:image.putalpha(image.getchannel('A').point(lambda a:round(a*.18) if a>8 else 0))
 p=OUT/f'texture-{index:02}.png';image.save(p)
 tiles.append({'name':name,'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes()),'index':index})
normal=decode(GAME/'resource/assets/effect/common_newskill_simayi_01_1_f59b3318.bin')
lookup={r['name']:r for r in normal['atlas']['SubTexture']}
ez=decode(GAME/'resource/assets/effect/common_newskill_simayi_01_1_ez_7169a33c.bin');ezLookup={r['name']:r for r in ez['atlas']['SubTexture']}
def fits(tile,r,scale):
 sized=tile.resize((round(tile.width*scale),round(tile.height*scale)),Image.Resampling.LANCZOS)
 cx=r.get('frameWidth',r['width'])/2+r.get('frameX',0);cy=r.get('frameHeight',r['height'])/2+r.get('frameY',0)
 x=round(cx-sized.width/2);y=round(cy-sized.height/2);b=sized.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
 return bool(b and x+b[0]>=0 and y+b[1]>=0 and x+b[2]<=r['width'] and y+b[3]<=r['height']),sized,x,y
# No per-phase bounding-box normalization. Pick one scale that fits all13.
impactScale=1.3
while not all(fits(Image.open(ROOT/r['path']).convert('RGBA'),regions[r['name']],impactScale*factor)[0] for regions,factor in [(lookup,1),(ezLookup,.5)] for r in tiles if 1<=r['index']<=13):impactScale-=.01
assert impactScale>.4,'Unexpected late-phase alignment; review source instead of shrinking everything'
qa={'manualReview':'approved-texture-sequence-for-native-trial','sourceTextures':15,'tiles':tiles,'commonImpactScaleNormal':impactScale,'technicalGlowAlphaScale':.18,'perPhaseBoundsNormalization':False,'productionIntegrated':False,'scope':'Flight/13 independent shell-burst phases/glow, new source sequence; native62@24 skeletal effect retained. Full skin not complete.'}
qaPath=OUT/'qa.json';qaPath.write_text(json.dumps(qa,ensure_ascii=False,indent=2),'utf8')
entries=[]
for model,filename,factor in [('common_newskill_simayi_01_1','common_newskill_simayi_01_1_f59b3318.bin',1),('common_newskill_simayi_01_1_ez','common_newskill_simayi_01_1_ez_7169a33c.bin',.5)]:
 original=GAME/'resource/assets/effect'/filename;d=decode(original);atlas=Image.open(io.BytesIO(d['image'])).convert('RGBA');regions={r['name']:r for r in d['atlas']['SubTexture']}
 assert set(regions)=={r['name'] for r in tiles}
 for row in tiles:
  tile=Image.open(ROOT/row['path']).convert('RGBA');r=regions[row['name']]
  scale=(1.0 if row['index']==0 else .65 if row['index']==14 else impactScale)*factor
  ok,sized,x,y=fits(tile,r,scale);assert ok,(model,row['name'],scale)
  replacement=Image.new('RGBA',(r['width'],r['height']));replacement.alpha_composite(sized,(x,y));atlas.paste(replacement,(r['x'],r['y']))
 buffer=io.BytesIO();atlas.save(buffer,format='PNG');blob=original.read_bytes();parts=chunks(blob);comp=zlib.compressobj(9,zlib.DEFLATED,-15);parts[2]=comp.compress(buffer.getvalue())+comp.flush();packed=blob[:12]+b''.join(struct.pack('<I',len(p))+p for p in parts)
 target=GAME/f'assets/street/skins/100201/native-fx/{model}-walnut-flight-{sha(packed)[:16]}.bin';target.write_bytes(packed)
 entry={'originalKey':model+'_bin','originalPath':original.relative_to(GAME).as_posix(),'originalSha256':sha(blob),'targetKey':'street_'+model+'_walnut_flight_bin','targetPath':target.relative_to(GAME).as_posix(),'targetSha256':sha(packed),'type':'bin','skinCode':100201,'changedRegions':[r['name'] for r in tiles],'regionReviewPath':qaPath.relative_to(ROOT).as_posix(),'regionReviewSha256':sha(qaPath.read_bytes()),'nativeAnimationReplacement':'common_newskill_simayi_01_1','completeContainerReplaced':True,'scope':'All15 textures of shared native active-skill flight/burst effect; no whole skin claim.'}
 entry['verification']=verify_container(entry);entries.append(entry)
(OUT/'candidate-containers.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'containers':2,'regionsEach':15,'commonImpactScaleNormal':impactScale,'technicalGlowAlphaScale':.18,'productionIntegrated':False}))
