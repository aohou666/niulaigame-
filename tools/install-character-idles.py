"""Install the workbook's 85 full PNG idle sequences without editing source images."""
from pathlib import Path
import json,shutil,hashlib,concurrent.futures
from PIL import Image
import numpy as np,cv2

ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';OUT=ROOT/'outputs/game_idle_rollout';OUT.mkdir(exist_ok=True)
BOOK=ROOT/'outputs/01a1354a-366c-7060-9fca-5633500e0780/rematch/unified/角色换皮资产表_两轮素材重匹配与立绘对照.xlsx'
SOURCE=Path(r'D:\参考图片\角色待机_抠像成品\各角色待机动作')
rows=json.loads((OUT/'workbook_mapping.json').read_text(encoding='utf-8'))
assert [r['id'] for r in rows if not r['materialId']]==[13]
backup=OUT/'backup';backup.mkdir(exist_ok=True)
for name in ['index_bh_lite3zbtest_andr.html','character-reskin.js','character-reskin-data.js']:
 if not(backup/name).exists():shutil.copy2(GAME/name,backup/name)

def export_role(row):
 src=SOURCE/row['materialId'];files=sorted(src.glob('frame_*.png'));assert files
 dest=GAME/'assets/character_idle'/row['materialId'];dest.mkdir(parents=True,exist_ok=True);bounds=[];main=[];size=None
 for i,p in enumerate(files):
  with Image.open(p) as im:
   assert im.mode=='RGBA';size=im.size if size is None else size;assert im.size==size
   alpha=im.getchannel('A');box=alpha.point(lambda a:255 if a>8 else 0).getbbox();assert box;bounds.append(box)
   if i in [0,len(files)//2,len(files)-1]:
    a=np.asarray(alpha);n,labels,stats,_=cv2.connectedComponentsWithStats((a>100).astype('uint8'),8);j=1+np.argmax(stats[1:,4]);main.append(stats[j,:4].tolist())
  target=dest/p.name;shutil.copy2(p,target)
  assert hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(p.read_bytes()).digest()
 crop=[min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)]
 center=float(np.median([b[0]+b[2]/2 for b in main]));foot=float(np.median([b[1]+b[3] for b in main]));height=float(np.median([b[3] for b in main]))
 return {**row,'fps':24,'frameCount':len(files),'width':size[0],'height':size[1],'crop':[crop[0],crop[1],crop[2]-crop[0],crop[3]-crop[1]],'centerX':center,'footY':foot,'bodyHeight':height,'baseUrl':'assets/character_idle/'+row['materialId']+'/','files':[p.name for p in files]}

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:heroes=list(pool.map(export_role,[r for r in rows if r['materialId']]))
data={'version':'2026-10-21-full-idle-v1','fps':24,'excludedOriginalIds':[13],'sourceFolder':str(SOURCE),'heroes':{str(r['id']):r for r in heroes}}
(GAME/'character-idle-data.js').write_text('window.CharacterIdleData='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
path=GAME/'character-reskin-data.js';text=path.read_text(encoding='utf-8');old=json.loads(text[text.index('=')+1:].strip().rstrip(';'))
for r in heroes:
 h=old['heroes'][str(r['id'])];h.update(name=r['name'],materialId=r['materialId'],idle=r['materialId'],portraitStatus='完整待机序列 · 24帧/秒')
old['idleVersion']=data['version'];path.write_text('window.CharacterReskinData='+json.dumps(old,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
(OUT/'installed_manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'installedHeroes':len(heroes),'frames':sum(h['frameCount'] for h in heroes),'excluded':[13],'source':str(SOURCE)},ensure_ascii=False),flush=True)
