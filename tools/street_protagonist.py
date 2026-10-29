"""Prepare two separately generated protagonist compositions with original layout bounds."""
import json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
manifest=json.loads((GAME/'resource/default.res_49784.json').read_text('utf8'));resources={r['name']:r for r in manifest['resources']}
folder=ROOT/'art-migration/generation/repair-captain-full-matte-v1';job=json.loads((folder/'job.json').read_text('utf8'));assert job['status']=='generated-unreviewed'
full=Image.open(GAME/'assets/street/ui/repair-captain-full-source.png').convert('RGB').convert('RGBA');alpha=Image.open(ROOT/job['outputs'][0]['path']).getchannel('A');full.putalpha(alpha.point(lambda a:0 if a<9 else a))
sources={'main_img_zhujue_png':Image.open(GAME/'assets/street/ui/repair-captain-source.png').convert('RGBA'),'wj_img_zhujue_png':full,'_hero_m_json.wujiang_img_renwu':Image.open(GAME/'assets/street/ui/repair-captain-source.png').convert('RGBA')}
records=[]
for key,im in sources.items():
 if '.' in key:
  sheetKey,region=key.split('.');sheetPath=resources[sheetKey]['url'];sheet=json.loads((GAME/'resource'/sheetPath).read_text('utf8'));f=sheet['frames'][region];original=GAME/'resource'/resources[sheetKey[:-5]+'_png']['url'];old=Image.open(original).convert('RGBA').crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']))
 else:original=GAME/'resource'/resources[key]['url'];old=Image.open(original).convert('RGBA')
 box=old.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
 if key=='_hero_m_json.wujiang_img_renwu':box=(48,8,old.width-12,old.height)
 crop=im.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();im=im.crop(crop);im.thumbnail((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
 target=Image.new('RGBA',old.size);target.alpha_composite(im,(round((box[0]+box[2]-im.width)/2),box[3]-im.height));out=GAME/f'assets/street/ui/{key}.png';target.save(out)
 record={'originalKey':key,'originalPath':original.relative_to(GAME).as_posix(),'originalSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'targetKey':'street_captain_'+key.replace('.','_'),'targetPath':out.relative_to(GAME).as_posix(),'targetSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'size':old.size,'status':'prepared-unreviewed','generation':{'provider':'official-built-in-image_gen','source':'assets/street/ui/repair-captain-full-source.png' if key.startswith('wj') else 'assets/street/ui/repair-captain-source.png','matte':'local-RMBG-1.4' if key.startswith('wj') else 'official-alpha','prompt':'art-migration/prompts/repair-captain.txt'},'originalBounds':box,'targetBounds':target.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()}
 record['generation']['sourceSha256']=hashlib.sha256((GAME/record['generation']['source']).read_bytes()).hexdigest()
 if '.' in key:record.update(originalRegion=region,extraAliases=[region+'_png'],originalBounds=old.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox(),safeLayoutBounds=box)
 records.append(record)
 for bg in ['#f3dfb3','#203c48']:
  preview=Image.new('RGBA',target.size,bg);preview.alpha_composite(target);preview.convert('RGB').save(ROOT/f'outputs/street-reskin/{key}-{bg[1:]}.jpg',quality=95)
p=GAME/'street-art-data.js';data=json.loads(p.read_text('utf8').split('=',1)[1].strip().rstrip(';'));data['version']='0.27.0';data['resources']=[r for r in data['resources'] if r['originalKey'] not in sources]+records;p.write_text('window.StreetArtData='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n','utf8');print(json.dumps(records))
