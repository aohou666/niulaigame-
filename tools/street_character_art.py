"""Prepare canonical images from user-supplied full idle frames, retaining provenance."""
import hashlib, json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
def data(name):return json.loads((GAME/name).read_text('utf8').split('=',1)[1].strip().rstrip(';'))
idle=data('character-idle-data.js');heroes=data('character-reskin-data.js')['heroes'];out={}
manifest=json.loads((GAME/'resource/default.res_49784.json').read_text('utf8'))
resources={r['name']:r for r in manifest['resources']}
baseline=json.loads((ROOT/'art-migration/original-runtime-baseline.json').read_text('utf8'))
requested={}
for row in baseline['heroes']+baseline['skins']:
    hid=str(row['subType'])
    if hid not in idle['heroes']:continue
    for field in ['avatar','avatar2','halfPic','pictureDraw','dermaPic']:
        key=row.get(field)
        if key:requested.setdefault(hid,{})[key+'_png']=field
for hid,h in idle['heroes'].items():
    source=GAME/h['baseUrl']/h['files'][0]
    with Image.open(source) as im:
        im=im.convert('RGBA');x,y,w,ht=h['crop'];im=im.crop((x,y,x+w,y+ht))
        alpha=im.getchannel('A').point(lambda n:0 if n<=8 else n);im.putalpha(alpha)
        folder=GAME/'assets/street/characters'/f'{int(hid):03d}';folder.mkdir(parents=True,exist_ok=True)
        portrait=im.copy();portrait.thumbnail((512,768),Image.Resampling.LANCZOS);portrait.save(folder/'portrait.png',optimize=True)
        # Keep the upper body and silhouette; do not distort non-humanoid subjects.
        head=im.crop((0,0,im.width,max(1,min(im.height,int(im.width*1.1),int(im.height*.6)))))
        head.thumbnail((160,160),Image.Resampling.LANCZOS)
        avatar=Image.new('RGBA',(160,160));avatar.alpha_composite(head,((160-head.width)//2,(160-head.height)//2));avatar.save(folder/'avatar.png',optimize=True)
    rel=folder.relative_to(GAME).as_posix();bindings={}
    for key,field in requested.get(hid,{}).items():
        original=resources.get(key)
        if original:
            with Image.open(GAME/'resource'/original['url']) as original_im:size=original_im.size
        else:size=(160,160) if field.startswith('avatar') else (221,130) if field=='halfPic' else (132,257)
        target=Image.new('RGBA',size)
        if field in ['avatar','avatar2','halfPic']:
            artwork=im.crop((0,0,im.width,max(1,min(im.height,int(im.width*1.05),int(im.height*.6))))).copy()
        else:artwork=im.copy()
        artwork.thumbnail(size,Image.Resampling.LANCZOS)
        x=0 if field=='halfPic' else (size[0]-artwork.width)//2
        target.alpha_composite(artwork,(x,size[1]-artwork.height))
        filename='bind_'+key+'.png';target.save(folder/filename,optimize=True)
        bindings[key]={'name':'street_'+hid+'_'+key,'url':rel+'/'+filename,'size':size,'field':field,'originalExists':bool(original)}
    out[hid]={'id':int(hid),'name':h['name'],'portrait':rel+'/portrait.png','avatar':rel+'/avatar.png','bindings':bindings,'source':source.relative_to(GAME).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'origin':'existing-user-idle-frame','review':'pending'}
    heroes[hid]['portrait']=rel+'/portrait.png'
    heroes[hid]['portraitStatus']='角色立绘'
p=data('character-reskin-data.js');p['heroes']=heroes;p['version']='0.21.0'
(GAME/'character-reskin-data.js').write_text('window.CharacterReskinData='+json.dumps(p,ensure_ascii=False,separators=(',',':'))+';\n','utf8')
(GAME/'character-art-data.js').write_text('window.CharacterArtData='+json.dumps({'version':'0.21.0','heroes':out},ensure_ascii=False,separators=(',',':'))+';\n','utf8')
(ROOT/'art-migration/character-image-provenance.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf8')
print('Prepared',len(out),'portraits and avatars from supplied idle frames; visual review pending')
