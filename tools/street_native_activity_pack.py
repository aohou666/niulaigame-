"""Technical composition of native-rendered frames over an approved new map.

No generative painting or original battle screenshot pixels are used.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'art-migration/generation/skin100201-native-activity-preview-v1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
capture = json.loads((OUT / 'capture.json').read_text('utf8'))
assert capture['pass'] and len(capture['frames']) == 19
original = ROOT / 'local_game/resource/assets/effect_f/common_activity_simayi_new01_mc_865a4da.json'
protocol = json.loads(original.read_text('utf8'))
background = ROOT / 'local_game/assets/street/environments/cabbage-courtyard-battle-v1.jpg'
bg = ImageOps.fit(Image.open(background).convert('RGBA'), (206,257), method=Image.Resampling.LANCZOS)
atlas = Image.new('RGBA',(2048,1024))
contact = Image.new('RGB',(206*5,257*4),(45,55,60))
rows=[]
for i,frame in enumerate(protocol['mc']['common_activity_simayi_new01']['frames']):
    p=ROOT/capture['frames'][i]['path']
    assert sha(p)==capture['frames'][i]['sha256']
    actor=Image.open(p).convert('RGBA')
    assert actor.size==(206,257) and actor.getbbox()
    # Preserve the renderer's alpha, placement, scale and original MC offsets.
    composed=Image.alpha_composite(bg,actor)
    region=protocol['res'][frame['res']]
    assert (region['w'],region['h'])==composed.size
    atlas.paste(composed,(region['x'],region['y']))
    contact.paste(composed.convert('RGB'),((i%5)*206,(i//5)*257))
    rows.append({'res':frame['res'],'sourceFrame':capture['frames'][i]['sourceFrame'],'actorSha256':sha(p)})
target=OUT/'common_activity_simayi_new01_tex.png'
atlas.save(target)
contact.save(OUT/'contact.jpg',quality=92)
(OUT/'common_activity_simayi_new01_mc.json').write_text(json.dumps(protocol,ensure_ascii=False,separators=(',',':')),'utf8')
proof={'technicalPass':True,'visualApproval':'pending','productionIntegrated':False,
 'scope':'Staged native skill preview on an approved new map, not actual battle footage or independent animation generation.',
 'originalProtocolPath':original.relative_to(ROOT).as_posix(),'originalProtocolSha256':sha(original),
 'protocolSemanticallyIdentical':True,'nativeFrames':38,'fps':24,'exposures':19,
 'background':background.relative_to(ROOT).as_posix(),'backgroundSha256':sha(background),
 'targetSha256':sha(target),'frames':rows}
(OUT/'pack-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'technicalPass':True,'exposures':19,'targetSha256':sha(target)}))
