"""Bind three separately generated hero-detail textures, preserving original dimensions."""
import json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';folder=GAME/'assets/street/ui/hero-details';manifest={r['name']:r for r in json.loads((GAME/'resource/default.res_49784.json').read_text('utf8'))['resources']};region=next(r for r in map(json.loads,(ROOT/'art-migration/ui-regions.jsonl').read_text('utf8').splitlines()) if r['key']=='_hero_m_json.wujiang_txt_wjyc');records=[]
for key,name,kind in [('wujiang_img_bg1_png','workshop','opaque'),('common_img_dakuang_10_png','panel','frame'),('_hero_m_json.wujiang_txt_wjyc','title','title')]:
 source=folder/({'workshop':'workshop-source.png','panel':'panel-source-v2.png','title':'title-source.png'}[name]);im=Image.open(source).convert('RGBA');original=GAME/region['atlasPath'] if name=='title' else GAME/'resource'/manifest[key]['url'];size=[231,79] if name=='title' else list(Image.open(original).size);box=None
 if kind=='opaque':
  target=im.resize(size,Image.Resampling.LANCZOS);rgba=np.asarray(target).copy();t=np.clip((np.arange(size[1])/(size[1]-1)-.72)/.22,0,1);opacity=1-t*t*(3-2*t);rgba[:,:,3]=np.rint(rgba[:,:,3]*opacity[:,None]).astype(np.uint8);target=Image.fromarray(rgba,'RGBA')
 else:
  alpha=im.getchannel('A').point(lambda v:0 if v<9 else v);im.putalpha(alpha);box=alpha.point(lambda v:255 if v>16 else 0).getbbox();assert box and min(box[0],box[1],im.width-box[2],im.height-box[3])>8;tile=im.crop(box);target=Image.new('RGBA',size)
  if kind=='frame':tile=tile.resize((size[0]-2,size[1]-2),Image.Resampling.LANCZOS)
  else:tile.thumbnail((size[0]-2,size[1]-2),Image.Resampling.LANCZOS)
  target.alpha_composite(tile,((size[0]-tile.width)//2,(size[1]-tile.height)//2))
 path=folder/(name+'.png');target.save(path,optimize=True);r={'originalKey':key,'originalPath':original.relative_to(GAME).as_posix(),'originalSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'targetKey':'street_hero_details_'+name,'targetPath':path.relative_to(GAME).as_posix(),'targetSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':size,'status':'prepared-runtime-pending','generation':{'provider':'official-built-in-image_gen','source':source.relative_to(GAME).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'prompt':'art-migration/prompts/hero-details-'+name+'.txt','sourceBounds':box,'alphaPolicy':'Generated alpha retained with<9 noise cleanup; no learned matte needed.' if kind!='opaque' else 'Deterministic opacity-only UI edge fade from72percent to94percent height; generated RGB unchanged, prevents hard rectangular seam over native panel. No artwork synthesized.'},'manualNotes':{'workshop':'Full new maintenance bay/workshop/wood platform, no old celestial sky, magic circle or braziers. Center clear for character, quiet lower stats area.','panel':'Initial frame had clipped top, rejected; separately editedv2 complete board with transparent margins approved. No old red scroll/cloud/tassels.','title':'Viewed exact four generated simplified Chinese glyphs 街坊档案, no extra text, clean alpha and margins.'}[name]}
 if name=='title':r.update(originalRegion='wujiang_txt_wjyc',originalFrame=region['frame'],extraAliases=['wujiang_txt_wjyc','wujiang_txt_wjyc_png'])
 records.append(r)
p=GAME/'street-art-data.js';d=json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'));keys={r['originalKey'] for r in records};d['resources']=[r for r in d['resources'] if r['originalKey'] not in keys]+records;d['version']='0.41.0';p.write_text('window.StreetArtData='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n','utf8');(ROOT/'art-migration/ui-groups/hero-details.json').write_text(json.dumps({'version':'0.41.0','manualReview':'approved-source-runtime-pending','records':records},ensure_ascii=False,indent=2)+'\n','utf8')
p=GAME/'index_bh_lite3zbtest_andr.html';s=p.read_text('utf8');import re
s=re.sub(r'street-art-data.js\?v=[^"\s]+','street-art-data.js?v=0.41.0',s);p.write_text(s,'utf8');print(json.dumps({'bindingsAdded':len(records),'total':len(d['resources'])}))
