"""Verify exact source-to-native-region coverage, without granting visual approval."""
import argparse,json,io,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from street_packed_inventory import decode
from street_packed_fx import chunks
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--folder',required=True);p.add_argument('--require-production',action='store_true');args=p.parse_args();folder=ROOT/args.folder
 entries=json.loads((folder/'candidate-containers.json').read_text('utf8'));live=json.loads((GAME/'street-art-data.js').read_text('utf8').split('=',1)[1].strip().rstrip(';'));reports=[]
 for e in entries:
  base=GAME/e['baseTargetPath'];target=GAME/e['targetPath'];assert sha(base.read_bytes())==e['baseTargetSha256'];assert sha(target.read_bytes())==e['targetSha256'];assert chunks(base.read_bytes())[:2]==chunks(target.read_bytes())[:2]
  originalEntry=next(r for r in live['containers'] if r['originalKey']==e['originalKey']);original=GAME/originalEntry['originalPath'];assert chunks(original.read_bytes())[:2]==chunks(target.read_bytes())[:2]
  a=decode(base);b=decode(target);o=decode(original);assert a['atlas']==b['atlas']==o['atlas'];old=Image.open(io.BytesIO(a['image'])).convert('RGBA');new=Image.open(io.BytesIO(b['image'])).convert('RGBA');orig=Image.open(io.BytesIO(o['image'])).convert('RGBA');assert old.size==new.size==orig.size
  changed=[];changedOriginal=[];mask=np.zeros((new.height,new.width),bool);unlisted=0;bodyNames=set(e['newBodyRegions'])
  for r in a['atlas']['SubTexture']:
   rect=(r['x'],r['y'],r['x']+r['width'],r['y']+r['height']);mask[rect[1]:rect[3],rect[0]:rect[2]]=True;before=old.crop(rect).tobytes();after=new.crop(rect).tobytes()
   if before!=after:changed.append(r['name']);assert new.crop(rect).getchannel('A').getbbox(),'Empty replacement'
   if orig.crop(rect).tobytes()!=after:changedOriginal.append(r['name'])
   if r['name'] not in bodyNames:assert before==after,'Earlier FX/unlisted body changed';unlisted+=1
  assert set(changed)==bodyNames
  sources=e['bodySources'];assert {s['nativeRegion'] for s in sources}==bodyNames;assert len({s['sourceSha256'] for s in sources})==len(sources)
  for s in sources:
   assert sha((ROOT/s['sourcePath']).read_bytes())==s['sourceSha256'];assert sha(new.crop(s['targetRect']).tobytes())==s['targetRgbaSha256']
  background=np.asarray(new)[~mask]
  if e.get('technicalUnownedPaddingClear'):assert not background.any(),'Legacy unowned atlas pixels remain'
  else:assert np.array_equal(background,np.asarray(old)[~mask])
  bound=any(r['originalKey']==e['originalKey'] and r['targetSha256']==e['targetSha256'] for r in live['containers'])
  if args.require_production:assert bound,'Candidate not bound in production data'
  reports.append({'originalKey':e['originalKey'],'targetSha256':e['targetSha256'],'newBodyRegions':len(changed),'sourceHashesAndROIsVerified':len(sources),'remainingOriginalBodyRegions':107-len(changed),'retainedOtherRegions':unlisted,'changedRegionsFromOriginal':len(changedOriginal),'totalAtlasRegions':len(a['atlas']['SubTexture']),'skeletonAtlasBytesIdentical':True,'unownedNonzeroAlphaPixels':int((background[:,3]>0).sum()),'unownedPaddingCleared':e.get('technicalUnownedPaddingClear',False),'productionBindingPresent':bound,'visualApproval':'not-established-by-this-technical-verifier'})
 result={'pass':True,'scope':'Physical native texture/provenance coverage only; not body/skin/character visual or gameplay completion.','models':reports};(folder/'trial-body-regions-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(result))
if __name__=='__main__':main()
