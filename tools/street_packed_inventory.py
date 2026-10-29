"""Read Egret DragonBones payloads and enumerate their actual art and timelines."""
from __future__ import annotations
import collections, hashlib, json, struct, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';OUT=ROOT/'art-migration'

def decode(path):
    b=path.read_bytes()
    if b[:3]!=bytes([219,189,30]):return None
    pos=12;parts=[]
    for i in range(3 if b[6] in [0,2] else 4):
        if pos+4>len(b):raise ValueError('truncated length')
        size=struct.unpack_from('<I',b,pos)[0];pos+=4
        if pos+size>len(b):raise ValueError('truncated payload')
        part=b[pos:pos+size];pos+=size
        parts.append(zlib.decompress(part,-15) if part and b[4] else part)
    ske=parts[0]
    if b[5]==1: skeleton=json.loads(ske)
    elif ske[:4]==b'DBDT':
        size=struct.unpack_from('<I',ske,8)[0];skeleton=json.loads(ske[12:12+size])
    else:skeleton={}
    return {'header':list(b[:12]),'skeleton':skeleton,'atlas':json.loads(parts[1]),'image':parts[2],'consumed':pos,'size':len(b)}

def main():
    rows=[];errors=[]
    for folder in ['model','effect','ui_effect']:
        for p in sorted((GAME/'resource/assets'/folder).rglob('*')):
            if p.suffix not in {'.bin','.dbbin'}:continue
            try:
                d=decode(p)
                if not d:continue
                skeleton=d['skeleton'];atlas=d['atlas'];arms=[]
                for arm in skeleton.get('armature',[]):
                    anim=[]
                    for a in arm.get('animation',[]):
                        frames=a.get('frame',[])
                        anim.append({'name':a.get('name'),'frames':a.get('duration'),'playTimes':a.get('playTimes'),'frameEvents':frames})
                    arms.append({'name':arm.get('name'),'fps':arm.get('frameRate',skeleton.get('frameRate')),'animations':anim,'bones':len(arm.get('bone',[])),'slots':len(arm.get('slot',[]))})
                rows.append({'path':p.relative_to(GAME).as_posix(),'imageSha256':hashlib.sha256(d['image']).hexdigest(),'imageFormat':d['header'][6],'atlasSize':[atlas.get('width'),atlas.get('height')],'regions':atlas.get('SubTexture',[]),'armatures':arms,'status':'pending','completePayload':d['consumed']==d['size']})
            except Exception as e:errors.append({'path':p.relative_to(GAME).as_posix(),'error':str(e)})
    with (OUT/'packed-art.jsonl').open('w',encoding='utf8') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
    summary={'containers':len(rows),'regions':sum(len(r['regions']) for r in rows),'animations':sum(len(a['animations']) for r in rows for a in r['armatures']),'errors':errors,'trailingData':[r['path'] for r in rows if not r['completePayload']]}
    (OUT/'packed-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':main()
