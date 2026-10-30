"""Build an isolated three-head native rig candidate, never publish it."""
import sys,io,json,struct,zlib,argparse
from pathlib import Path
from PIL import Image
from street_packed_inventory import decode
from street_packed_fx import chunks,sha
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--clothing',action='store_true');parser.add_argument('--parts',action='append',default=[]);parser.add_argument('--out');args=parser.parse_args()
 folder=ROOT/'art-migration/generation/skin100201-native-head3-official-v1'
 out=ROOT/(args.out or ('art-migration/generation/skin100201-native-head3-clothing18-packed-trial-v1' if args.clothing else 'art-migration/generation/skin100201-native-head3-packed-trial-v1'));assert not out.exists();out.mkdir()
 qa=json.loads((folder/'source-qa.json').read_text('utf8'));heads=qa['heads'];boxes=[h['alphaBounds'] for h in heads]
 union=(min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes))
 live=json.loads((GAME/'street-art-data.js').read_text('utf8').split('=',1)[1].strip().rstrip(';'));entries=[]
 clothing=[]
 if args.clothing:
  q=json.loads((ROOT/'art-migration/generation/skin100201-native-clothing18-official-v1/component-qa.json').read_text('utf8'));assert q['manualReview']=='approved-drawn-components-for-isolated-native-fit';clothing=q['parts'];assert len(clothing)==18
 for reviewPath in args.parts:
  q=json.loads((ROOT/reviewPath).read_text('utf8'));assert q['manualReview']=='approved-drawn-components-for-isolated-native-fit';clothing.extend(q['parts'])
 names=[h['nativeRegion'] for h in heads]+[p['nativeRegion'] for p in clothing];assert len(names)==len(set(names)),'Duplicate native part assignment'
 for model in ['hero_skin_002_01','hero_skin_002_01_ez']:
  base=next(e for e in live['containers'] if e['originalKey']==model+'_bin');path=GAME/base['targetPath'];data=decode(path);image=Image.open(io.BytesIO(data['image'])).convert('RGBA');regions={r['name']:r for r in data['atlas']['SubTexture']}
  size=(min(regions[h['nativeRegion']]['width'] for h in heads),min(regions[h['nativeRegion']]['height'] for h in heads));scale=min(size[0]/(union[2]-union[0]),size[1]/(union[3]-union[1]));targetSize=(round((union[2]-union[0])*scale),round((union[3]-union[1])*scale))
  for h in heads:
   source=ROOT/h['path'];assert sha(source.read_bytes())==h['sha256'];tile=Image.open(source).convert('RGBA').crop(union).resize(targetSize,Image.Resampling.LANCZOS);r=regions[h['nativeRegion']];replacement=Image.new('RGBA',(r['width'],r['height']));replacement.alpha_composite(tile,((r['width']-tile.width)//2,r['height']-tile.height));image.paste(replacement,(r['x'],r['y']))
  for part in clothing:
   source=ROOT/part['path'];assert sha(source.read_bytes())==part['sha256'];tile=Image.open(source).convert('RGBA');b=tile.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();assert b;tile=tile.crop(b);r=regions[part['nativeRegion']]
   rect=(r['x'],r['y'],r['x']+r['width'],r['y']+r['height']);old=image.crop(rect);footprint=old.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();assert footprint
   tile.thumbnail((footprint[2]-footprint[0],footprint[3]-footprint[1]),Image.Resampling.LANCZOS);opacity=part.get('technicalAlphaScale',1);assert 0<opacity<=1
   if opacity!=1:tile.putalpha(tile.getchannel('A').point(lambda a:round(a*opacity)))
   replacement=Image.new('RGBA',old.size);replacement.alpha_composite(tile,(footprint[0]+(footprint[2]-footprint[0]-tile.width)//2,footprint[1]+(footprint[3]-footprint[1]-tile.height)//2));image.paste(replacement,(r['x'],r['y']))
  paddingCleared=False;oldUnownedAlphaPixels=0
  if len(names)==107:
   assert set(names)=={n for n in regions if n.startswith('hero_skin_002_01/')}
   assert len(base['changedRegions'])==40 and len(regions)==147,'Full body candidate must preserve all40 approved FX textures'
   unowned=image.getchannel('A');clean=Image.new('RGBA',image.size)
   for r in regions.values():
    rect=(r['x'],r['y'],r['x']+r['width'],r['y']+r['height']);unowned.paste(0,rect);clean.paste(image.crop(rect),(r['x'],r['y']))
   oldUnownedAlphaPixels=sum(unowned.histogram()[1:]);image=clean;paddingCleared=True
  buf=io.BytesIO();image.save(buf,format='PNG');blob=path.read_bytes();parts=chunks(blob);comp=zlib.compressobj(9,zlib.DEFLATED,-15);parts[2]=comp.compress(buf.getvalue())+comp.flush();packed=blob[:12]+b''.join(struct.pack('<I',len(p))+p for p in parts)
  target=GAME/f'assets/street/skins/100201/native-body-trial/{model}-head3-{sha(packed)[:16]}.bin';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(packed)
  assert chunks(packed)[:2]==chunks(blob)[:2]
  changed=[h['nativeRegion'] for h in heads]+[c['nativeRegion'] for c in clothing]
  before=Image.open(io.BytesIO(data['image'])).convert('RGBA')
  for name,r in regions.items():
   if name not in changed:
    rect=(r['x'],r['y'],r['x']+r['width'],r['y']+r['height']);assert before.crop(rect).tobytes()==image.crop(rect).tobytes(),'Unlisted native texture changed'
  sources=[]
  for part in heads+clothing:
   r=regions[part['nativeRegion']];rect=(r['x'],r['y'],r['x']+r['width'],r['y']+r['height']);sources.append({'nativeRegion':part['nativeRegion'],'sourcePath':part['path'],'sourceSha256':part['sha256'],'targetRect':rect,'targetRgbaSha256':sha(image.crop(rect).tobytes()),'technicalAlphaScale':part.get('technicalAlphaScale',1)})
  entries.append({'originalKey':base['originalKey'],'targetKey':'trial_'+model+'_head3_bin','targetPath':target.relative_to(GAME).as_posix(),'targetSha256':sha(packed),'type':'bin','trialOnly':True,'baseTargetPath':base['targetPath'],'baseTargetSha256':base['targetSha256'],'newBodyRegions':changed,'bodySources':sources,'remainingOriginalBodyRegions':107-len(changed),'commonCrop':union,'commonScale':scale,'technicalUnownedPaddingClear':paddingCleared,'clearedUnownedAlphaPixels':oldUnownedAlphaPixels,'scope':'Isolated new native body parts; inspect complete styling/joins before production. Texture coverage is not full skin/animation approval.'})
 (out/'candidate-containers.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'trialContainers':2,'newBodyRegions':len(changed),'remainingOriginalBodyRegions':107-len(changed),'productionIntegrated':False}))

if __name__=='__main__':main()
