"""Prepare an explicit one-region native projectile replacement for visual trial."""
import io,json,struct,zlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
from street_packed_inventory import decode
from street_packed_fx import chunks,sha,verify_container
ROOT=Path(__file__).resolve().parents[1]; GAME=ROOT/'local_game'

def main():
 source=ROOT/'art-migration/generation/skin100201-qiu-hybrid-alpha-v1/official-alpha.png'
 out=ROOT/'art-migration/generation/skin100201-qiu-native-packed-v1'
 assert not out.exists(),'Use a new revision instead of overwriting evidence'
 out.mkdir(parents=True)
 im=Image.open(source).convert('RGBA'); alpha=im.getchannel('A'); box=alpha.point(lambda v:255 if v>16 else 0).getbbox()
 assert box and min(box[0],box[1],im.width-box[2],im.height-box[3])>=6
 tile=im.crop(box); tile.save(out/'walnut.png')
 review={'sourceTextures':1,'effect':'qiu','nativeFrames':1,'nativeFps':30,'manualReview':'pending','runtimeIntegrated':False,'tiles':[{'name':'qiu','path':(out/'walnut.png').relative_to(ROOT).as_posix(),'sha256':sha((out/'walnut.png').read_bytes())}], 'scope':'One newly drawn static projectile texture; not a newly animated sequence or a complete skin.'}
 (out/'qa.json').write_text(json.dumps(review,indent=2)+'\n','utf8')
 entries=[];sheet=Image.new('RGB',(640,480),'#d9d9d9');draw=ImageDraw.Draw(sheet)
 inventory=json.loads((ROOT/'outputs/street-reskin/skin100201-projectile-audit-v95/inventory.json').read_text('utf8'))
 for i,row in enumerate(r for r in inventory if '_qiu_' in r['key']):
  original=ROOT/row['path'];data=decode(original);image=Image.open(io.BytesIO(data['image'])).convert('RGBA');regions=data['atlas']['SubTexture'];assert len(regions)==1
  r=regions[0];assert r['name']=='qiu';rect=(r['x'],r['y'],r['x']+r['width'],r['y']+r['height']);old=image.crop(rect)
  footprint=old.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();assert footprint
  new=tile.copy();new.thumbnail((footprint[2]-footprint[0],footprint[3]-footprint[1]),Image.Resampling.LANCZOS)
  replacement=Image.new('RGBA',old.size);replacement.alpha_composite(new,(footprint[0]+(footprint[2]-footprint[0]-new.width)//2,footprint[1]+(footprint[3]-footprint[1]-new.height)//2));image.paste(replacement,(r['x'],r['y']))
  replacement.save(out/(row['key']+'-tile.png'))
  for j,bg in enumerate(['#f2ead8','#233238']):
   cell=Image.new('RGBA',(320,210),bg);cell.alpha_composite(replacement,((320-replacement.width)//2,20));sheet.paste(cell.convert('RGB'),(j*320,i*240));draw.text((j*320+8,i*240+216),row['key'],fill='black')
  buf=io.BytesIO();image.save(buf,format='PNG');blob=original.read_bytes();parts=chunks(blob);compress=zlib.compressobj(9,zlib.DEFLATED,-15);parts[2]=compress.compress(buf.getvalue())+compress.flush();packed=blob[:12]+b''.join(struct.pack('<I',len(p))+p for p in parts)
  target=GAME/f'assets/street/skins/100201/native-fx/{row["key"]}-walnut-{sha(packed)[:16]}.bin';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(packed)
  entries.append({'originalKey':row['key'],'originalPath':original.relative_to(GAME).as_posix(),'originalSha256':sha(blob),'targetKey':'street_'+row['key']+'_walnut','targetPath':target.relative_to(GAME).as_posix(),'targetSha256':sha(packed),'type':'bin','skinCode':100201,'changedRegions':['qiu'],'regionReviewPath':(out/'qa.json').relative_to(ROOT).as_posix(),'regionReviewSha256':sha((out/'qa.json').read_bytes()),'completeContainerReplaced':True,'nativeAnimationReplacement':'common_newskill_simayi_02_qiu','scope':'Shared original SimaYi projectile resource, including all original consumers; ordinary/EZ are resolutions, not independent skins.'})
 sheet.save(out/'native-size-light-dark.png')
 (out/'candidate-containers.json').write_text(json.dumps(entries,indent=2)+'\n','utf8');print(json.dumps({'prepared':len(entries),'pendingManualReview':True}))

if __name__=='__main__':main()
