"""Fit two independently drawn walnut ground layers to unchanged native regions."""
import io,json,struct,zlib
from pathlib import Path
from PIL import Image
from street_packed_fx import chunks,sha,verify_container
from street_packed_inventory import decode
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
SOURCE=ROOT/'art-migration/generation/skin100201-active-ground2-official-v1'
OUT=ROOT/'art-migration/generation/skin100201-active-ground2-native-v1'
assert not OUT.exists(),'Preserve previous candidate revisions'
OUT.mkdir(parents=True)
im=Image.open(SOURCE/'official-source.png').convert('RGBA')
tiles=[]
for name,box in [('扩散波',(0,0,1024,768)),('地裂',(0,768,1024,1536))]:
 tile=im.crop(box);tile.putalpha(tile.getchannel('A').point(lambda a:0 if a<=8 else a));bounds=tile.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();assert bounds
 tile=tile.crop(bounds);path=OUT/('ring.png' if name=='扩散波' else 'ground.png');tile.save(path)
 tiles.append({'name':name,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes()),'sourceCrop':box,'alphaBoundsInCrop':bounds})
qa={'manualReview':'approved-texture-sequence-for-native-trial','sourceTextures':2,'tiles':tiles,'runtimeIntegrated':False,'scope':'Two independent source layers, not two held poses for a full animation. Ring: walnut shell/ivory dust, ground: split walnut and cracked pavement. Native placement/motion retained; no old artwork RGB reused.','technicalAlphaThreshold':8}
qaPath=OUT/'qa.json';qaPath.write_text(json.dumps(qa,ensure_ascii=False,indent=2),'utf8')
entries=[]
for model,filename in [('common_newskill_simayi_01_3','common_newskill_simayi_01_3_9cb0595f.bin'),('common_newskill_simayi_01_3_ez','common_newskill_simayi_01_3_ez_46abeba9.bin')]:
 original=GAME/'resource/assets/effect'/filename;data=decode(original);atlas=Image.open(io.BytesIO(data['image'])).convert('RGBA');regions={r['name']:r for r in data['atlas']['SubTexture']};assert set(regions)=={t['name'] for t in tiles}
 for row in tiles:
  r=regions[row['name']];source=Image.open(ROOT/row['path']).convert('RGBA');source.thumbnail((r['width']-4,r['height']-4),Image.Resampling.LANCZOS);tile=Image.new('RGBA',(r['width'],r['height']));tile.alpha_composite(source,((tile.width-source.width)//2,(tile.height-source.height)//2));atlas.paste(tile,(r['x'],r['y']))
 buf=io.BytesIO();atlas.save(buf,format='PNG');blob=original.read_bytes();parts=chunks(blob);comp=zlib.compressobj(9,zlib.DEFLATED,-15);parts[2]=comp.compress(buf.getvalue())+comp.flush();packed=blob[:12]+b''.join(struct.pack('<I',len(p))+p for p in parts)
 target=GAME/f'assets/street/skins/100201/native-fx/{model}-walnut-ground-{sha(packed)[:16]}.bin';target.write_bytes(packed)
 cfg={'originalKey':model+'_bin','originalPath':original.relative_to(GAME).as_posix(),'originalSha256':sha(blob),'targetKey':'street_'+model+'_walnut_ground_bin','targetPath':target.relative_to(GAME).as_posix(),'targetSha256':sha(packed),'type':'bin','skinCode':100201,'changedRegions':[t['name'] for t in tiles],'regionReviewPath':qaPath.relative_to(ROOT).as_posix(),'regionReviewSha256':sha(qaPath.read_bytes()),'nativeAnimationReplacement':'common_newskill_simayi_01_3','completeContainerReplaced':True,'scope':'Shared sibling ground effect, actual active-skill dependency use still under audit. Full skin not complete.'}
 cfg['verification']=verify_container(cfg);entries.append(cfg)
(OUT/'candidate-containers.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'containers':len(entries),'regionsEach':2,'productionIntegrated':False}))
