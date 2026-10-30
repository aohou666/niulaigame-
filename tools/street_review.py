"""Version gate: inspect every binding and report all unfinished art honestly."""
import argparse,collections,hashlib,json,time
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from street_art_verify import verify as verify_street_art
from street_runtime_tracking import verify as verify_runtime_tracking
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';OUT=ROOT/'art-migration'
def loadjs(p):return json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--version',required=True);a=p.parse_args()
 artData=loadjs(GAME/'character-art-data.js');art=artData['heroes'];supplemental=artData.get('supplementalHeroes',{});errors=[];checked=0;supplementalChecked=0
 for hid,h in {**art,**supplemental}.items():
  for key,binding in h['bindings'].items():
   target=GAME/binding['url'];checked+=int(hid in art);supplementalChecked+=int(hid in supplemental)
   if not target.exists():errors.append({'id':hid,'key':key,'error':'missing'});continue
   if binding.get('targetSha256') and hashlib.sha256(target.read_bytes()).hexdigest()!=binding['targetSha256']:errors.append({'id':hid,'key':key,'error':'target digest mismatch'})
   if binding.get('sourceSha256') and hashlib.sha256((ROOT/binding['source']).read_bytes()).hexdigest()!=binding['sourceSha256']:errors.append({'id':hid,'key':key,'error':'source digest mismatch'})
   if binding.get('nativeRuntimeAuditPath'):
    proofFile=ROOT/binding['nativeRuntimeAuditPath'];proof=json.loads(proofFile.read_text('utf8'))
    if hashlib.sha256(proofFile.read_bytes()).hexdigest()!=binding['nativeRuntimeAuditSha256'] or not proof['pass'] or proof['key']!=binding['name'] or proof['url']!=binding['url']:errors.append({'id':hid,'key':key,'error':'native static binding proof mismatch'})
   with Image.open(target) as im:
    if list(im.size)!=binding['size']:errors.append({'id':hid,'key':key,'error':'wrong dimensions'})
    if 'A' not in im.getbands():errors.append({'id':hid,'key':key,'error':'missing alpha'})
    if im.getbbox() is None:errors.append({'id':hid,'key':key,'error':'empty image'})
 manifest=json.loads((GAME/'resource/default.res_49784.json').read_text('utf8'))
 missing=[r['url'] for r in manifest['resources'] if not (GAME/'resource'/r['url']).exists()]
 results_path=ROOT/'outputs/street-reskin/all-heroes-runtime.json'
 runtime=json.loads(results_path.read_text('utf8')) if results_path.exists() and results_path.stat().st_size else None
 originals=[json.loads(x) for x in (OUT/'assets.jsonl').read_text('utf8').splitlines()]
 pending=collections.Counter(r['category'] for r in originals if r['status']!='complete')
 packed=json.loads((OUT/'packed-summary.json').read_text('utf8'))
 packed_rows=[json.loads(line) for line in (OUT/'packed-art.jsonl').read_text('utf8').splitlines()]
 pending_regions=sum(len(r['regions']) for r in packed_rows if r['status']!='complete')
 pending_animations=sum(sum(1 for anim in arm['animations'] if anim['name'] not in r.get('verifiedAnimationReplacements',[])) for r in packed_rows if r['status']!='complete' for arm in r['armatures'])
 atlas_file=OUT/'idle-atlas-verification.json'
 atlas=json.loads(atlas_file.read_text('utf8')) if atlas_file.exists() else None
 browser_logs={}
 for mode,file in [('heroes','browser-log.json'),('demo','browser-log-demo.json')]:
  logfile=ROOT/'outputs/street-reskin'/file
  if logfile.exists():
   log=json.loads(logfile.read_text('utf8'));browser_logs[mode]={'exceptions':len(log['errors']),'failedResponses':log['failed']}
 report={'version':a.version,'reviewedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'characterImageBindings':checked,'supplementalCharacterImageBindings':supplementalChecked,'bindingErrors':errors,'originalManifestEntriesChecked':len(manifest['resources']),'missingOriginals':missing,'detailRuntime':runtime,'browserLogs':browser_logs,'idleAtlas':atlas,'originalArtNotYetFullyReplaced':dict(pending),'packedRegionsNotYetReplaced':pending_regions,'animationsNotYetReplaced':pending_animations,'allArtReplaced':False,'zeroBugsClaimed':False,'visualReview':'Contact sheets and key game screens; this is not a visual sign-off for every original resource.'}
 ui_file=OUT/'ui-regions.jsonl';ui_rows=[json.loads(line) for line in ui_file.read_text('utf8').splitlines()] if ui_file.exists() else []
 report['uiSheetRegionsNotYetReplaced']=sum(r['status']!='complete' for r in ui_rows)
 report['currentEquippedPresentationCounts']=dict(collections.Counter(row.get('presentation','legacy-unspecified') for row in (runtime or {}).get('results',[])))
 baseRuntimePath=OUT/'versions'/a.version/'base-heroes-runtime.json'
 report['baseHeroDetailRuntime']=json.loads(baseRuntimePath.read_text('utf8')) if baseRuntimePath.exists() else None
 report['promotedStreetArtVerification']=verify_street_art()
 containerBindings=loadjs(GAME/'street-art-data.js').get('containers',[])
 report['nativePackedRegionBindings']={'containers':[{'originalKey':r['originalKey'],'skinCode':r.get('skinCode'),'regions':r['changedRegions'],'completeContainerReplaced':False,'nativeAnimation':r.get('nativeAnimationReplacement'),'runtimeAudit':r.get('nativeRuntimeAuditPath')} for r in containerBindings],'note':'Only declared texture regions replaced; unchanged body/effect regions are still original. Ordinary/EZ are two versions of the same skin, not two independent skins.'}
 verifiedContainerKeys={r['originalKey'] for r in report['promotedStreetArtVerification'].get('nativePackedRegions',[])}
 confirmedRegions=0;confirmedAnimations=0;logicalEffects=set()
 for binding in containerBindings:
  if binding['originalKey'] not in verifiedContainerKeys:continue
  row=next((r for r in packed_rows if r['path']==binding['originalPath']),None)
  if not row or row['status']=='complete':continue
  confirmedRegions+=len({r['name'] for r in row['regions']} & set(binding['changedRegions']))
  def approved_names(cfg):
   return ({cfg['nativeAnimationReplacement']} if cfg.get('nativeAnimationReplacement') else set()).union(*(approved_names(old) for old in cfg.get('inheritedReplacements',[])))
  for name in approved_names(binding):
   confirmedAnimations+=sum(1 for arm in row['armatures'] if arm['name']==name for anim in arm['animations'] if anim['name']==name and name not in row.get('verifiedAnimationReplacements',[]));logicalEffects.add((binding.get('skinCode'),name))
 report['packedRegionsNotYetReplaced']=pending_regions-confirmedRegions;report['animationsNotYetReplaced']=pending_animations-confirmedAnimations
 report['nativePackedRegionBindings'].update(verifiedPhysicalRegions=confirmedRegions,verifiedPhysicalAnimations=confirmedAnimations,logicalSkinEffects=[{'skinCode':skin,'effect':effect} for skin,effect in sorted(logicalEffects)])
 body=loadjs(GAME/'street-body-data.js')['characters'];targets=[c for c in body if c['id']!=13]
 report['attackSkillContinuousMotionQuality']={'installedTargetMappings':len(targets),'approvedContinuousTargetMappings':sum(c.get('temporalQuality')=='approved-continuous' for c in targets),'quarantinedTargetMappings':sum(bool(c.get('qualityQuarantineActions')) for c in targets),'all85TargetsComplete':False,'note':'Installed images/native frame timing are separate from complete continuous-animation approval; unreviewed clips do not count as complete.'}
 skinStatic={}
 for hero in art.values():
  for key,binding in hero['bindings'].items():
   if binding.get('skinCode'):
    row=skinStatic.setdefault(str(binding['skinCode']),{'bindings':[],'completeSkin':False})
    row['bindings'].append({'key':key,'url':binding['url'],'review':binding.get('review'),'targetSha256':binding.get('targetSha256')})
 report['independentSkinStaticBindings']={'skins':skinStatic,'note':'Independent static art is partial progress only; this does not establish animation, effects, equip or complete-skin approval.'}
 skinIdles=loadjs(GAME/'character-idle-data.js').get('skins',{})
 report['independentSkinIdleBindings']={'skins':{key:{'heroId':cfg['heroId'],'frameCount':cfg['frameCount'],'loopSeconds':cfg['frameCount']/cfg['fps'],'review':cfg.get('review'),'completeSkin':False} for key,cfg in skinIdles.items()},'note':'Idle-only evidence; other body actions, effects, real equip and battle remain separate requirements.'}
 skinBodies=loadjs(GAME/'street-body-data.js').get('skins',{})
 report['independentSkinBodyBindings']={'skins':{key:{'heroId':cfg['heroId'],'armature':cfg['armature'],'frames':len(cfg['frames']),'actions':list(cfg['actions']),'review':cfg.get('review'),'completeSkin':False} for key,cfg in skinBodies.items()},'note':'Individual native action replacement only; missing other body states, VFX, equip/battle proof must not count as a complete independent skin.'}
 report['generatedRuntimeGitTracking']=verify_runtime_tracking()
 issues=OUT/'open-issues.json';report['knownOpenIssues']=[r for r in json.loads(issues.read_text('utf8')) if r.get('status')!='resolved'] if issues.exists() else []
 folder=OUT/'versions'/a.version;folder.mkdir(parents=True,exist_ok=True)
 (folder/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
 font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
 items=sorted(art.items(),key=lambda p:int(p[0]))
 for start in range(0,len(items),24):
  sheet=Image.new('RGB',(1200,1280),'#26373c');draw=ImageDraw.Draw(sheet)
  for i,(hid,h) in enumerate(items[start:start+24]):
   x=(i%6)*200;y=(i//6)*320
   with Image.open(GAME/h['portrait']) as im:
    im=im.convert('RGBA');im.thumbnail((184,270),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(200-im.width)//2,y+275-im.height),im)
   draw.text((x+10,y+282),hid+' '+h['name'][:7],font=font,fill='#f1e8d1')
  sheet.save(ROOT/f'outputs/street-reskin/characters-review-{start//24+1}.jpg',quality=90)
 print(json.dumps({k:v for k,v in report.items() if k not in ['detailRuntime','originalArtNotYetFullyReplaced']},ensure_ascii=False))
 if errors or missing or report['promotedStreetArtVerification']['errors'] or not report['generatedRuntimeGitTracking']['pass']:raise SystemExit(1)

if __name__=='__main__':main()
