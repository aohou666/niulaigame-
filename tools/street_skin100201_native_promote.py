"""Install qualified native body/UI assets; retain explicit whole-skin gaps."""
import copy,json,shutil
from pathlib import Path
from street_packed_fx import sha,verify_container
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
OUT=ROOT/'art-migration/generation/skin100201-native-body-production-v1'
assert not (OUT/'production-before').exists(),'Do not overwrite earlier binding evidence'
def read(name):return json.loads((GAME/name).read_text('utf8').split('=',1)[1].strip().rstrip(';'))
def write(name,data):
 path=GAME/name;old=path.read_text('utf8');prefix=old[:old.index('=')+1]
 path.write_text(prefix+json.dumps(data,ensure_ascii=False,indent=2)+';\n','utf8')
names=['street-art-data.js','character-art-data.js','character-idle-data.js','street-body-data.js']
data={name:read(name) for name in names}
entries=json.loads((OUT/'candidate-containers.json').read_text('utf8'))
for e in entries:verify_container(e)
staticFolder=ROOT/'art-migration/generation/skin100201-native-static-fit-v1'
statics=json.loads((staticFolder/'candidate.json').read_text('utf8'))
assert json.loads((staticFolder/'native-static-review.json').read_text('utf8'))
bannerFolder=ROOT/'art-migration/generation/skin100201-skill-banner-native-v1'
banner=json.loads((bannerFolder/'candidate.json').read_text('utf8'))
assert banner['manualReview']=='approved-native-skill-banner-candidate'
previewFolder=ROOT/'art-migration/generation/skin100201-native-activity-preview-v1'
assert json.loads((previewFolder/'movieclip-runtime.json').read_text('utf8'))['pass']
backup=OUT/'production-before';backup.mkdir()
for name in names:shutil.copy2(GAME/name,backup/name)
art=data['street-art-data.js'];art['containers']=[e for e in art['containers'] if e['originalKey'] not in {r['originalKey'] for r in entries}]+entries
resources=copy.deepcopy(statics['resources'])+copy.deepcopy(banner['resources'])
gallery=next(e for e in resources if e['originalKey']=='mjl_img_simayi_png')
gallery['sourceInputs']=[{'path':p,'sha256':sha((ROOT/p).read_bytes())} for p in ['art-migration/generation/skin100201-native-outfit-static-official-v2/official-source.png','art-migration/generation/skin100201-native-card-frame-official-v1/official-source.png']]
for e in resources:e.update(skinCode=100201,review='qualified-native-skin-ui-art; whole-skin-incomplete')
previewPath=GAME/'assets/street/skins/100201/activity-native-v1/common_activity_simayi_new01_tex.png';previewPath.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(previewFolder/'common_activity_simayi_new01_tex.png',previewPath)
original=GAME/'resource/assets/effect_f/common_activity_simayi_new01_tex_b469b3.png'
resources.append({'originalKey':'common_activity_simayi_new01_tex_png','originalPath':original.relative_to(GAME).as_posix(),'originalSha256':sha(original.read_bytes()),'targetKey':'street_skin100201_native_activity_tex_png','targetPath':previewPath.relative_to(GAME).as_posix(),'targetSha256':sha(previewPath.read_bytes()),'size':[2048,1024],'type':'image','skinCode':100201,'scope':'19 native-rendered skill preview exposures/new background; original38@24 MC JSON/res/offset/event protocol unchanged. Staged preview, not actual battle footage.','runtimeAuditPath':(previewFolder/'movieclip-runtime.json').relative_to(ROOT).as_posix(),'runtimeAuditSha256':sha((previewFolder/'movieclip-runtime.json').read_bytes())})
art['resources']=[e for e in art['resources'] if e['originalKey'] not in {r['originalKey'] for r in resources}]+resources
character=data['character-art-data.js'];character['heroes']['2']['bindings'].update(statics['bindings']);character.setdefault('skinText',{})['100201']=statics['text']
idle=data['character-idle-data.js'];body=data['street-body-data.js']
retired={'skinCode':100201,'reason':'All107 independently drawn native body regions now retain original continuous all5 skeletal actions; raster source history retained, no independent extra skin completion claim.','idle':idle.get('skins',{}).pop('100201',None),'body':body.get('skins',{}).pop('100201',None)}
(OUT/'retired-raster-config.json').write_text(json.dumps(retired,ensure_ascii=False,indent=2),'utf8')
fit=json.loads((ROOT/'art-migration/generation/skin100201-native-body107-packed-trial-v2/native-preview-fit.json').read_text('utf8'))
idle.setdefault('nativePreviews',{})['100201']=fit
body.setdefault('nativeSkins',{})['100201']={'id':100201,'skinCode':100201,'heroId':2,'renderer':'native-skeletal','armature':'hero_skin_002_01','models':['hero_skin_002_01','hero_skin_002_01_ez'],'fps':30,'actions':{'daiji':198,'gongji':45,'jineng':46,'shouji':21,'paobu':16},'bodyRegions':107,'childFXRegions':40,'completeSkin':False,'containers':{e['originalKey']:e['targetSha256'] for e in entries},'pending':'Additional shared active-skill textures and all remaining ledger items are not approved by this body/UI binding.'}
for name,d in data.items():d['version']='0.97.0';write(name,d)
(OUT/'production-binding.json').write_text(json.dumps({'applied':True,'released':False,'version':'0.97.0','completeSkin':False,'containers':2,'newBodyRegionsPerModel':107,'retainedNewChildFXRegionsPerModel':40,'newStaticFields':4,'newGenericImages':len(resources),'retiredRasterConfig':'retired-raster-config.json'},indent=2),'utf8')
print(json.dumps({'applied':True,'released':False,'containers':2,'staticFields':4,'genericImages':len(resources),'wholeSkinComplete':False}))
