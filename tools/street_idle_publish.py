"""Publish reviewed candidate pixels first, then one coherent idle configuration."""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image
from street_atomic import atomic_write_text,atomic_write_bytes
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('--version',required=True);a=p.parse_args()
c=json.loads((a.candidate/'candidate.json').read_text('utf8'));hid=str(c['heroId'])
for name in ['verification.json','native-runtime.json','native-raw-runtime.json','native-atlas-formation-runtime.json']:
 assert json.loads((a.candidate/name).read_text('utf8'))['pass'],name
dest=GAME/f"assets/street/idle/{int(hid):03d}/revision-{c['sourceSignature'][:16]}";dest.mkdir(parents=True,exist_ok=True)
profiles=c['profiles']
for entry in c['fallback']+[p for pack in profiles.values() for p in pack['pages']]:
 payload=(a.candidate/entry['file']).read_bytes();assert hashlib.sha256(payload).hexdigest()==entry['sha256']
 atomic_write_bytes(dest/entry['file'],payload)
for pack in profiles.values():
 for page in pack['pages']:page['url']=(dest/page.pop('file')).relative_to(GAME).as_posix()
 pack['decodedBytes']=sum(p['width']*p['height']*4 for p in pack['pages'])
def load(name):return json.loads((GAME/name).read_text('utf8').split('=',1)[1].strip().rstrip(';'))
def save(name,var,data):atomic_write_text(GAME/name,'window.'+var+'='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
idle=load('character-idle-data.js');cfg=idle['heroes'][hid]
cfg.update(frameCount=c['frameCount'],width=512,height=512,crop=c['crop'],bodyHeight=c['crop'][3],fps=24,
           baseUrl=dest.relative_to(GAME).as_posix()+'/',files=[r['file'] for r in c['fallback']],
           atlas={'profiles':profiles,'frameCount':c['frameCount'],'crop':c['crop'],'sourceSequenceSha256':c['sourceSignature']})
idle['version']=a.version
# Generate every portrait binding from the same reviewed first idle frame.
art=load('character-art-data.js');hero=art['heroes'][hid]
im=Image.open(dest/c['fallback'][0]['file']).convert('RGBA');x,y,w,h=c['crop'];im=im.crop((x,y,x+w,y+h))
upper=im.crop((0,0,im.width,max(1,min(im.height,int(im.width*1.05),int(im.height*.6)))))
artdir=GAME/f"assets/street/characters/{int(hid):03d}/revision-{c['sourceSignature'][:16]}";artdir.mkdir(parents=True,exist_ok=True)
portrait=im.copy();portrait.thumbnail((512,768),Image.Resampling.LANCZOS);portrait.save(artdir/'portrait.png')
avatar=Image.new('RGBA',(160,160));head=upper.copy();head.thumbnail((160,160),Image.Resampling.LANCZOS);avatar.alpha_composite(head,((160-head.width)//2,(160-head.height)//2));avatar.save(artdir/'avatar.png')
for key,binding in hero['bindings'].items():
 size=tuple(binding['size']);canvas=Image.new('RGBA',size);part=(upper if binding['field'] in ['avatar','avatar2','halfPic'] else im).copy();part.thumbnail(size,Image.Resampling.LANCZOS)
 canvas.alpha_composite(part,(0 if binding['field']=='halfPic' else (size[0]-part.width)//2,size[1]-part.height));name='bind_'+key+'.png';canvas.save(artdir/name);binding['url']=(artdir/name).relative_to(GAME).as_posix()
hero.update(portrait=(artdir/'portrait.png').relative_to(GAME).as_posix(),avatar=(artdir/'avatar.png').relative_to(GAME).as_posix(),source=(dest/c['fallback'][0]['file']).relative_to(GAME).as_posix(),sourceSha256=c['fallback'][0]['sha256'],origin='official-reference-local-minimax-reviewed-idle',review='runtime-validation-pending')
art['version']=a.version;reskin=load('character-reskin-data.js');reskin['heroes'][hid]['portrait']=hero['portrait'];reskin['version']=a.version
save('character-idle-data.js','CharacterIdleData',idle)
save('character-art-data.js','CharacterArtData',art)
save('character-reskin-data.js','CharacterReskinData',reskin)
print(json.dumps({'hero':hid,'frames':c['frameCount'],'atlasPages':sum(len(p['pages']) for p in profiles.values()),'portraitBindings':len(hero['bindings']),'runtimeValidation':'pending'}))
