"""Install a generated environment with an explicit original-resource mapping."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
manifest=json.loads((GAME/'resource/default.res_49784.json').read_text('utf8'))
original=next(r for r in manifest['resources'] if r['url']=='assets/ui/dk/dk_02/dk_02_bg_01_85eb9935.jpg')
source=GAME/'resource'/original['url'];generated=GAME/'assets/street/environments/noodle-plaza-source.png'
with Image.open(source) as im:size=im.size
target=GAME/'assets/street/environments/noodle-plaza-battle.jpg'
with Image.open(generated) as im:ImageOps.fit(im.convert('RGB'),size,method=Image.Resampling.LANCZOS).save(target,quality=95,subsampling=0,optimize=True)
record={'originalKey':original['name'],'originalPath':'resource/'+original['url'],'originalSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'targetKey':'street_noodle_plaza_battle_jpg','targetPath':target.relative_to(GAME).as_posix(),'targetSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'size':size,'generation':{'provider':'official-built-in-image_gen','prompt':'art-migration/prompts/noodle-plaza.txt','sourceSha256':hashlib.sha256(generated.read_bytes()).hexdigest()},'status':'integrated-unreviewed'}
(GAME/'street-art-data.js').write_text('window.StreetArtData='+json.dumps({'version':'0.23.0','resources':[record]},ensure_ascii=False,separators=(',',':'))+';\n','utf8')
(ROOT/'art-migration/environment-provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(record,ensure_ascii=False))
