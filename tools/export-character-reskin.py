"""从最终换皮表编制纯展示层补丁，原数值配置与原美术文件不写入。"""
import json, hashlib, re
from pathlib import Path
from PIL import Image
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'outputs/01a1354a-366c-7060-9fca-5633500e0780/rematch/unified/角色换皮资产表_两轮素材重匹配与立绘对照.xlsx'
OUT=ROOT/'outputs/reskin-v020'
ART=ROOT/'local_game/reskin'
OUT.mkdir(parents=True,exist_ok=True);ART.mkdir(exist_ok=True)
w=openpyxl.load_workbook(SOURCE,data_only=True)
main=list(w['角色资产总表'].values)[9:]
oldnames=sorted({r[1] for r in main if r[1]!='未知'},key=len,reverse=True)
meta=re.compile(r'原(?:人物|角色|包|槽位|'+ '|'.join(re.escape(n) for n in oldnames)+r')|(?:关系|身份).*(?:保持|保留|不变|不改|沿用|新增|补造)|(?:立绘|素材).*(?:待补|暂配|补做|暂拟|未提供)|这段只是原创|不另造|槽位|(?:技能|机制|效果|数值).*(?:保持|保留|不变|不因|原样|迁入|增加)')
def clean_intro(text):
    parts=[s for s in str(text or '').split('。') if s.strip() and not meta.search(s)]
    return '。'.join(parts)+('。' if parts else '')
def player_synopsis(text):
    lines=str(text or '').split('\n')
    if not lines:return ''
    return '\n'.join([clean_intro(lines[0])]+[s for s in lines[1:] if '原包未提供' not in s])
def player_story(text):
    pieces=str(text or '').split('\n\n',1)
    return clean_intro(pieces[0])+('\n\n'+pieces[1] if len(pieces)>1 else '')
summary={r[0]:r for r in list(w['角色换皮汇总'].values)[7:]}
heroes={}
def make_art(path,dest):
    im=Image.open(path).convert('RGBA')
    if 'idle_' in Path(path).name:
        a=im.getchannel('A').resize((180,104));v=list(a.getdata());left={i for i,x in enumerate(v) if x>32};best=[]
        while left:
            q=[left.pop()];part=[]
            while q:
                p=q.pop();part.append(p);x=p%180;y=p//180
                for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    n=ny*180+nx
                    if 0<=nx<180 and 0<=ny<104 and n in left:left.remove(n);q.append(n)
            if len(part)>len(best):best=part
        if best:
            x0=max(0,min(i%180 for i in best)-2);x1=min(180,max(i%180 for i in best)+3)
            y0=max(0,min(i//180 for i in best)-2);y1=min(104,max(i//180 for i in best)+3)
            im=im.crop((int(x0*im.width/180),int(y0*im.height/104),int(x1*im.width/180),int(y1*im.height/104)))
    im.thumbnail((540,760),Image.Resampling.LANCZOS)
    im.save(dest,optimize=True)
    return im.size
for r in main:
    hid=r[0];s=summary[hid];matched=bool(r[25]);path=s[17] if matched else ''
    portrait=''
    if path and Path(path).exists():
        dest=ART/f'hero_{hid:03}.png';size=make_art(path,dest);portrait='reskin/'+dest.name
    heroes[str(hid)]={'id':hid,'originalName':r[1],'name':r[26] if matched else r[1],
        'matched':matched,'materialId':r[25] or '', 'portrait':portrait,
        'portraitStatus':'待机帧立绘' if portrait and 'idle_' in str(path) else '原创立绘' if portrait else '立绘待补' if matched else '原角色保留',
        'definition':clean_intro(str(r[33] or '').split('\n')[0]) if matched else r[9],
        'synopsis':player_synopsis(r[33]) if matched else '', 'identity':s[6],'story':{},'skills':{},'pictureKey':r[23]}
for r in list(w['背景故事'].values)[4:]:
    h=heroes[str(r[0])];seg=r[3]
    if seg in (1,2,3) and r[6]=='有':h['story'][f'storyTitle{seg}']=r[9];h['story'][f'storyDesc{seg}']=player_story(r[10]) if h['matched'] else r[10]
for r in list(w['技能明细'].values)[4:]:
    h=heroes[str(r[0])]
    if not h['matched']:continue
    assert re.findall(r'\d+(?:\.\d+)?',str(r[8]))==re.findall(r'\d+(?:\.\d+)?',str(r[24]))
    h['skills'][str(r[3])]={'id':r[3],'slot':r[2],'name':r[23],'desc':r[24],'level':r[5]}
    if r[2]=='怒气技能' and r[5]==1:h['activeSkillDesc']=str(r[23])+'：'+str(r[24])
payload={'version':'0.20.0','sourceWorkbook':SOURCE.name,'heroes':heroes}
intro_overrides={
 '77':'凤羽静候余火散去，把灰烬留给新芽。每一片绿意都像一句轻声的承诺：伙伴还在，春天便不会结束。',
 '78':'离烬披上黑白衣装，把炽烈的声音收进低低的夜语。愈是众声喧嚷，他愈会停下来，听清风从哪里吹来。',
 '79':'寒渊披上沉重的幽甲，旧铜的光色里藏着不肯退后的倔强。站到同伴面前时，他把最锋利的部分都朝向了来敌。',
 '82':'藏绮以墨色正装掩住幽焰，笑意和心里的算盘隔着一层雾。狐火照见的是旧愿，也是她始终不肯交出的心。',
}
for hid,intro in intro_overrides.items():
    h=heroes[hid];h['definition']=intro
    lines=h['synopsis'].split('\n');h['synopsis']='\n'.join([intro]+lines[1:])
    for k in h['story']:
        if k.startswith('storyDesc'):
            parts=h['story'][k].split('\n\n',1);h['story'][k]=intro+('\n\n'+parts[1] if len(parts)>1 else '')
assert all(h['definition'] for h in heroes.values() if h['matched']),[h['id'] for h in heroes.values() if h['matched'] and not h['definition']]
(ROOT/'local_game/character-reskin-data.js').write_text('window.CharacterReskinData='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
manifest={'workbookSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'heroSlots':len(heroes),
    'matched':sum(h['matched'] for h in heroes.values()),'portraits':sum(bool(h['portrait']) for h in heroes.values()),
    'missingPortraits':[h['id'] for h in heroes.values() if h['matched'] and not h['portrait']],
    'unmatched':[h['id'] for h in heroes.values() if not h['matched']],
    'allowedHeroFields':['name','definition','activeSkillDesc','storyTitle1','storyTitle2','storyTitle3','storyDesc1','storyDesc2','storyDesc3'],
    'allowedSkillFields':['name','desc'],'originalAssetsOverwritten':0}
(OUT/'asset-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False))
