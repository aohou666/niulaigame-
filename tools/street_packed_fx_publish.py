"""Publish SHA-bound native region replacements without erasing earlier work."""
import argparse,hashlib,json
from pathlib import Path
from street_packed_fx import ROOT,GAME,verify_container
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--runtime',required=True);p.add_argument('--version',required=True);a=p.parse_args()
runtime=ROOT/a.runtime;proof=json.loads(runtime.read_text('utf8'));assert proof['pass'] and proof['manualReview']=='approved-complete-native-loop'
entries=json.loads((ROOT/a.candidate).read_text('utf8'));dataPath=GAME/'street-art-data.js';data=json.loads(dataPath.read_text('utf8').split('=',1)[1].strip().rstrip(';'));existing={r['originalKey']:r for r in data.get('containers',[])}
for entry in entries:
 verify_container(entry)
 observed=next(r for r in proof['resourceDigests'] if r['key']==entry['originalKey']);assert observed['digest']==entry['targetSha256'],'Native trial loaded a different package'
 old=existing.get(entry['originalKey']);assert not old or set(old['changedRegions'])<=set(entry['changedRegions']),'New package would erase previously replaced regions'
 entry['nativeRuntimeAuditPath']=a.runtime;entry['nativeRuntimeAuditSha256']=hashlib.sha256(runtime.read_bytes()).hexdigest();entry['nativeAnimationReplacement']=json.loads((ROOT/entry['regionReviewPath']).read_text('utf8'))['effect'];entry['review']='approved-native-timeline-FX-retexture';entry['fullSkinComplete']=False
 source=ROOT/entry['regionReviewPath'];provenance=source.parent/'provenance.json';assert provenance.exists();entry['sourceProvenancePath']=provenance.relative_to(ROOT).as_posix();entry['sourceProvenanceSha256']=hashlib.sha256(provenance.read_bytes()).hexdigest()
 existing[entry['originalKey']]=entry
data['containers']=list(existing.values());data['version']=a.version;dataPath.write_text('window.StreetArtData='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n','utf8')
print(json.dumps({'publishedContainers':len(entries),'physicalRegions':sum(len(e['changedRegions']) for e in entries),'logicalSkin':100201,'logicalEffect':entries[0]['nativeAnimationReplacement'],'completeSkin':False}))
