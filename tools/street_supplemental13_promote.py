"""Promote supplemental13 independent idle and actions without changing85 target roster."""
import json,hashlib,math,subprocess,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';BASE=ROOT/'art-migration/generation'
subprocess.run([sys.executable,str(ROOT/'tools/street_body_promote.py'),'hero013-body-actions-matte-v2','--attack-anchor=16','--version=0.38.0'],check=True)
def loadjs(p):return json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'))
images=[];bounds=[]
for name in ['hero013-body-actions-matte-v2','hero013-idle-matte-v1']:
 folder=BASE/name;j=json.loads((folder/'job.json').read_text('utf8'));design=json.loads((folder/('body-design.json' if (folder/'body-design.json').exists() else 'idle-design.json')).read_text('utf8'));assert len(j['outputs'])==73
 for raw,entry in zip(design['sourceFrameOrder'],j['outputs']):
  im=Image.open(ROOT/raw).convert('RGB').convert('RGBA');alpha=Image.open(ROOT/entry['path']).getchannel('A').point(lambda v:0 if v<9 else v);im.putalpha(alpha);box=alpha.point(lambda v:255 if v>16 else 0).getbbox();assert box and min(box[0],box[1],512-box[2],512-box[3])>2;images.append(im);bounds.append(box)
box=[min(b[0] for b in bounds)-2,min(b[1] for b in bounds)-2,max(b[2] for b in bounds)+2,max(b[3] for b in bounds)+2];size=[round((box[2]-box[0])*192/max(box[2]-box[0],box[3]-box[1])),round((box[3]-box[1])*192/max(box[2]-box[0],box[3]-box[1]))];atlas=Image.new('RGBA',(10*(size[0]+2),math.ceil(len(images)/10)*(size[1]+2)));rects=[]
for i,im in enumerate(images):
 tile=im.crop(box).resize(size,Image.Resampling.LANCZOS);x=i%10*(size[0]+2);y=i//10*(size[1]+2);atlas.paste(tile,(x,y));rects.append(dict(x=x,y=y,w=size[0],h=size[1]))
p=GAME/'street-body-data.js';d=loadjs(p);cfg=next(c for c in d['characters'] if c['id']==13);out=GAME/cfg['atlas'];atlas.save(out,lossless=True,method=6);cfg.update(frames=rects,crop=box,atlasSha256=hashlib.sha256(out.read_bytes()).hexdigest(),supplemental=True,targetRoster85=False,independentIdleSource='art-migration/generation/hero013-idle-matte-v1')
auditPath=ROOT/'art-migration/versions/0.38.0/supplemental-native-idle.json';audit=json.loads(auditPath.read_text('utf8'));assert audit['complete'];seqs={}
for r in audit['records']:
 assert not r['events'];seqs[r['model']]={'fps':r['fps'],'frameMap':[73+round(n*72/(r['durationFrames']-1)) for n in range(r['durationFrames'])],'nativeEvents':[],'nativeImpactFrame':None,'sourceImpactFrame':None,'nativeDurationFrames':r['durationFrames']}
cfg['actions']['daiji']=seqs[cfg['models'][0]]
for model in cfg['models'][1:]:
 if seqs[model]!=cfg['actions']['daiji']:cfg.setdefault('modelActionOverrides',{}).setdefault(model,{})['daiji']=seqs[model]
cfg['supplementalNativeActionAuditPath']=auditPath.relative_to(ROOT).as_posix();cfg['supplementalNativeActionAuditSha256']=hashlib.sha256(auditPath.read_bytes()).hexdigest();p.write_text('window.StreetBodyData='+json.dumps(d,separators=(',',':'))+';\n','utf8')
# Exact original image dimensions. Skin image keys receive the canonical identity, never counted as independently generated skins.
baseline=json.loads((ROOT/'art-migration/original-runtime-baseline.json').read_text('utf8'));resources={r['name']:r for r in json.loads((GAME/'resource/default.res_49784.json').read_text('utf8'))['resources']};folder=GAME/'assets/street/characters/013';im=Image.open(folder/'portrait.png').convert('RGBA');upperBox=[0,0,im.width,min(im.height,int(im.width*1.05),int(im.height*.6))];upper=im.crop(upperBox);avatar=upper.copy();avatar.thumbnail((160,160),Image.Resampling.LANCZOS);av=Image.new('RGBA',(160,160));av.alpha_composite(avatar,((160-avatar.width)//2,(160-avatar.height)//2));av.save(folder/'avatar.png');bindings={}
for row in baseline['heroes']+baseline['skins']:
 if row['subType']!=13:continue
 for field in ['avatar','avatar2','halfPic','pictureDraw','dermaPic']:
  if not row.get(field):continue
  key=row[field]+'_png';original=resources.get(key);size=Image.open(GAME/'resource'/original['url']).size if original else (160,160) if field.startswith('avatar') else (221,130) if field=='halfPic' else (132,257);art=(upper if field in ['avatar','avatar2','halfPic'] else im).copy();art.thumbnail(size,Image.Resampling.LANCZOS);target=Image.new('RGBA',size);target.alpha_composite(art,(0 if field=='halfPic' else (size[0]-art.width)//2,size[1]-art.height));filename='bind_'+key+'.png';target.save(folder/filename,optimize=True);bindings[key]={'name':'street_13_'+key,'url':'assets/street/characters/013/'+filename,'size':size,'field':field,'originalExists':bool(original)}
p=GAME/'character-art-data.js';d=loadjs(p);d['supplementalHeroes']={'13':{'id':13,'name':'街区安全员','portrait':'assets/street/characters/013/portrait.png','avatar':'assets/street/characters/013/avatar.png','bindings':bindings,'origin':'official-new-three-pose-image and local MiniMax independent idle/action clips','supplemental':True,'independentSkinsComplete':False}};d['version']='0.38.0';p.write_text('window.CharacterArtData='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n','utf8')
p=GAME/'character-reskin-data.js';d=loadjs(p);d['supplementalHeroes']={'13':{'id':13,'originalName':'于禁','name':'街区安全员','matched':True,'definition':'白盔橙背心，手里的红对讲机从不离身。路口一抬掌，连横冲直撞的送餐车都肯等一等。','portrait':'assets/street/characters/013/portrait.png','story':{'storyTitle1':'停一下','storyDesc1':'他每天练习最简单的手势，让街区最着急的人也能平安经过。','storyTitle2':'红色对讲机','storyDesc2':'频道里总有人找不到路，他记得每一家门牌，也记得哪条巷口正在修路。','storyTitle3':'最后一盏灯','storyDesc3':'最后一班车过去，他才摘下安全帽，把路锥摆回墙边。'},'skills':{},'supplemental':True}};d['version']='0.38.0';p.write_text('window.CharacterReskinData='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n','utf8');print(json.dumps({'supplemental':13,'atlasFrames':146,'independentIdleFrames':73,'portraitBindings':len(bindings)}))
