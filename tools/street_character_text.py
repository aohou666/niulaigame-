"""Install complete per-character stories and display titles without changing game mechanics."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';ART=ROOT/'art-migration'
def loadjs(p):return json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'))
data=loadjs(GAME/'character-reskin-data.js');art=loadjs(GAME/'character-art-data.js')['heroes'];idle=loadjs(GAME/'character-idle-data.js')['heroes'];baseline=json.loads((ART/'character-text-baseline.json').read_text('utf8'))
profiles={};titles={}
provenanceFile=ART/'stories/source-mapping.json';provenanceData=json.loads(provenanceFile.read_text('utf8')) if provenanceFile.exists() else {};legacyAliases=provenanceData.get('legacySelfAliases',{})
def localize_self(text,heroId,skillId,name):
 for alias,target in provenanceData.get('remainingExactReferences',{}).items():text=text.replace(alias,data['heroes'][str(target)]['name'])
 owner=str((int(skillId)//10000)%1000) if skillId else heroId
 for alias in {legacyAliases.get(heroId,''),legacyAliases.get(owner,'')}:
  if not alias:continue
  text=re.sub(re.escape(alias)+r'·[\u4e00-\u9fff]{1,12}?(?=攻击|生命|受到|死亡|本次|有|将继承)',name,text)
 return text
for p in sorted((ART/'stories').glob('stories-*.json')):
 for row in json.loads(p.read_text('utf8')):
  key=str(row['id']);assert key not in profiles,'duplicate story target';profiles[key]=row
for p in sorted((ART/'stories').glob('skills-*.json')):
 for key,value in json.loads(p.read_text('utf8')).items():assert key not in titles;assert len(value)==5;titles[key]=value
assert set(profiles)==set(titles)==set(art)==set(baseline),'must cover every one of the 85 actual targets'
slotIndex={'普通技能':0,'怒气技能':1,'被动技能1':2,'被动技能2':3,'被动技能3':4};numbers=lambda s:re.findall(r'[-+]?\d+(?:\.\d+)?%?',s or '')
originalNames={h['originalName'] for h in data['heroes'].values() if h.get('originalName')};changes=[];numericErrors=[];previousUnmatched=[];orphanDisplays=[]
generic={'普通攻击','普攻','普通技能','怒气技能','主动技能','被动技能','攻击'}
for key,profile in profiles.items():
 h=data['heroes'][key];assert h['id']==int(key);assert len(profile['definition'])>=25 and len(profile['chapters'])==3
 alltext=profile['definition']+''.join(title+text for title,text in profile['chapters'])
 assert all(len(title)>=2 and len(text)>=25 for title,text in profile['chapters'])
 assert not any(name in alltext for name in originalNames),'old canonical name in new story: '+key
 protected={field:value for field,value in h.items() if field not in ['definition','synopsis','identity','story','skills','activeSkillDesc','matched','portrait','portraitStatus','materialId']}
 if not h['matched']:previousUnmatched.append(int(key))
 h.update(matched=True,definition=profile['definition'],identity='离谱街区居民；独立经历见人物故事',synopsis=profile['definition']+'\n'+'\n'.join(str(i+1)+'.'+chapter[0] for i,chapter in enumerate(profile['chapters'])),portrait=art[key]['portrait'],portraitStatus='街区立绘已接入',materialId=idle[key]['materialId'])
 h['story']={}
 for i,(title,text) in enumerate(profile['chapters'],1):h['story']['storyTitle'+str(i)]=title;h['story']['storyDesc'+str(i)]=text
 merged={skillId:dict(row) for skillId,row in baseline[key]['skills'].items()}
 for skillId,row in h['skills'].items():
  if skillId not in merged:orphanDisplays.append({'hero':int(key),'skillId':skillId,'reason':'no authored native skill record; do not show a fictional rank'})
 replacements={}
 for skillId,s in merged.items():
  assert s['slot'] in slotIndex;newName=titles[key][slotIndex[s['slot']]];oldName=s['name']
  if oldName not in generic and len(oldName)>2:replacements[oldName]=newName
 for skillId,s in merged.items():
  before=s.get('desc','');after=before
  for old,new in sorted(replacements.items(),key=lambda p:-len(p[0])):after=after.replace(old,new)
  after=localize_self(after,key,skillId,h['name'])
  if numbers(before)!=numbers(after):numericErrors.append({'hero':key,'skill':skillId})
  s.update(name=titles[key][slotIndex[s['slot']]],desc=after)
 oldActive=h.get('activeSkillDesc') or baseline[key]['activeSkillDesc'];newActive=oldActive
 for old,new in sorted(replacements.items(),key=lambda p:-len(p[0])):newActive=newActive.replace(old,new)
 newActive=localize_self(newActive,key,None,h['name'])
 if numbers(oldActive)!=numbers(newActive):numericErrors.append({'hero':key,'field':'activeSkillDesc'})
 h.update(skills=merged,activeSkillDesc=newActive)
 assert protected=={field:value for field,value in h.items() if field not in ['definition','synopsis','identity','story','skills','activeSkillDesc','matched','portrait','portraitStatus','materialId']},'non-text mapping changed'
 changes.append({'id':int(key),'name':h['name'],'storyChapters':3,'skillDisplays':len(merged),'slots':sorted(set(s['slot'] for s in merged.values()))})
assert not numericErrors
if provenanceData:previousUnmatched=provenanceData['initialUnmatchedTargets'];orphanDisplays=provenanceData.get('initialOrphanSkillDisplays',orphanDisplays)
data['version']='0.30.0';(GAME/'character-reskin-data.js').write_text('window.CharacterReskinData='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n','utf8')
report={'version':'0.30.0','targetCharacters':len(profiles),'stories':255,'uniqueDisplayTitles':sum(len(v) for v in titles.values()),'skillDisplays':sum(r['skillDisplays'] for r in changes),'previousUnmatchedFixed':previousUnmatched,'removedOrphanSkillDisplays':orphanDisplays,'numericDescriptionChanges':numericErrors,'nativeSkillDefinitionsChanged':False,'baselineSha256':hashlib.sha256((ART/'character-text-baseline.json').read_bytes()).hexdigest(),'characters':changes,'runtimeReview':'pending'}
folder=ART/'versions/0.30.0';folder.mkdir(parents=True,exist_ok=True);(folder/'world-text-preparation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({k:v for k,v in report.items() if k!='characters'},ensure_ascii=False))
