"""Pack thirteen independently drawn impact textures on the unchanged native rig.

A common scale and the original logical texture origins preserve the growth/fade.
Never normalize each frame to its own bounding box, which would inflate the tail.
"""
import io,json,struct,zlib
from pathlib import Path
from PIL import Image
from street_packed_inventory import decode
from street_packed_fx import chunks,sha,verify_container
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'

def main():
 source=ROOT/'art-migration/generation/skin100201-impact-official13-v1'
 out=ROOT/'art-migration/generation/skin100201-impact-native-packed-v1'
 assert not out.exists(),'Preserve prior candidate evidence; use a new revision'
 review=json.loads((source/'alpha-qa.json').read_text('utf8'));assert len(review['frames'])==13
 out.mkdir(parents=True);tiles=[]
 for row in review['frames']:
  image=Image.open(ROOT/row['path']).convert('RGBA');image.putalpha(image.getchannel('A').point(lambda a:0 if a<=8 else a))
  path=out/f'frame-{row["frame"]:02}.png';image.save(path)
  tiles.append({'name':f'元件 {row["frame"]+1}','path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())})
 qa={'manualReview':'approved-texture-sequence-for-native-trial','sourceTextures':13,'effect':'common_newskill_simayi_02','nativeFrames':13,'nativeFps':24,'tiles':tiles,'runtimeIntegrated':False,'visualReview':'All thirteen independent official source cells viewed on light/dark; one ivory/copper flash expands into grooved brown shell chips and fades, no retained rainbow confetti. Native temporal trial still required.','technicalAlphaThreshold':8,'commonScaleNormal':1.14,'commonScaleEZ':0.57,'perFrameBoundsNormalization':False}
 qaPath=out/'qa.json';qaPath.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf8')
 inputs=[source/'official-source.png',ROOT/'art-migration/generation/skin100201-qiu-hybrid-alpha-v1/official-alpha.png',ROOT/'outputs/street-reskin/skin100201-projectile-audit-v95/impact-native13/original-native13-reference.png']
 provenance={'method':'Official independent thirteen-frame redraw; original native burst rhythm and new Qwen/official walnut material references. Rejected MiniMax output not integrated.','referenceInputs':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())} for p in inputs]};provPath=out/'provenance.json';provPath.write_text(json.dumps(provenance,indent=2)+'\n','utf8')
 entries=[]
 for model,filename,scale in [('common_newskill_simayi_02','common_newskill_simayi_02_3ccb6b44.bin',1.14),('common_newskill_simayi_02_ez','common_newskill_simayi_02_ez_5e420eaf.bin',0.57)]:
  original=GAME/'resource/assets/effect'/filename;data=decode(original);image=Image.open(io.BytesIO(data['image'])).convert('RGBA');regions={r['name']:r for r in data['atlas']['SubTexture']};assert set(regions)=={r['name'] for r in tiles}
  for row in tiles:
   r=regions[row['name']];tile=Image.open(ROOT/row['path']).convert('RGBA');resized=tile.resize((round(tile.width*scale),round(tile.height*scale)),Image.Resampling.LANCZOS)
   cx=r.get('frameWidth',r['width'])/2+r.get('frameX',0);cy=r.get('frameHeight',r['height'])/2+r.get('frameY',0);x=round(cx-resized.width/2);y=round(cy-resized.height/2)
   b=resized.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox();assert b and min(x+b[0],y+b[1])>=0 and x+b[2]<=r['width'] and y+b[3]<=r['height'],'Visible source would be clipped'
   replacement=Image.new('RGBA',(r['width'],r['height']));replacement.alpha_composite(resized,(x,y));image.paste(replacement,(r['x'],r['y']))
  buf=io.BytesIO();image.save(buf,format='PNG');blob=original.read_bytes();parts=chunks(blob);compress=zlib.compressobj(9,zlib.DEFLATED,-15);parts[2]=compress.compress(buf.getvalue())+compress.flush();packed=blob[:12]+b''.join(struct.pack('<I',len(p))+p for p in parts)
  target=GAME/f'assets/street/skins/100201/native-fx/{model}-walnut-impact-{sha(packed)[:16]}.bin';target.write_bytes(packed)
  entry={'originalKey':model+'_bin','originalPath':original.relative_to(GAME).as_posix(),'originalSha256':sha(blob),'targetKey':'street_'+model+'_walnut_impact_bin','targetPath':target.relative_to(GAME).as_posix(),'targetSha256':sha(packed),'type':'bin','skinCode':100201,'changedRegions':[r['name'] for r in tiles],'regionReviewPath':qaPath.relative_to(ROOT).as_posix(),'regionReviewSha256':sha(qaPath.read_bytes()),'sourceProvenancePath':provPath.relative_to(ROOT).as_posix(),'sourceProvenanceSha256':sha(provPath.read_bytes()),'nativeAnimationReplacement':'common_newskill_simayi_02','completeContainerReplaced':True,'scope':'All13 texture regions of the shared SimaYi impact resource; original13@24 timeline/skeleton/atlas unchanged, not complete skin/character.','technicalCommonScale':scale}
  entry['verification']=verify_container(entry);entries.append(entry)
 (out/'candidate-containers.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'candidateContainers':len(entries),'regionsPerContainer':13,'nativeTrialPending':True}))

if __name__=='__main__':main()
