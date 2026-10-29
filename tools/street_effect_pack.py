"""Retarget reviewed MiniMax foreground VFX to the existing 53-frame native timeline."""
import hashlib,json,math
from pathlib import Path
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';folder=ROOT/'art-migration/generation/hero001-cast-minimax-v2'
job=json.loads((folder/'job.json').read_text('utf8'));assert job['status']=='generated-unreviewed'
generated=[ROOT/r['path'] for r in job['outputs']]
original=sorted((ROOT/'outputs/street-reskin/effect-reference/common_skill_caocao_02_1').glob('frame_*.png'))
def energy(path):
 with Image.open(path) as image:return sum(ImageStat.Stat(image.convert('RGB').resize((64,64))).sum)
old_energy=[energy(p) for p in original];new_energy=[energy(p) for p in generated]
old_peak=max(range(len(old_energy)),key=old_energy.__getitem__);new_peak=max(range(len(new_energy)),key=new_energy.__getitem__)
assert 0<old_peak<len(original)-1 and 0<new_peak<len(generated)-1
out=GAME/'assets/street/effects/hero001-cast';out.mkdir(parents=True,exist_ok=True)
page=Image.new('RGB',(2048,1792));frames=[];sampling=[]
for i in range(len(original)):
 if i<=old_peak:j=round(i/old_peak*new_peak)
 else:j=round(new_peak+(i-old_peak)/(len(original)-1-old_peak)*(len(generated)-1-new_peak))
 with Image.open(generated[j]) as image:frame=image.convert('RGB').resize((252,252),Image.Resampling.LANCZOS)
 x=(i%8)*256+2;y=(i//8)*256+2;page.paste(frame,(x,y));frames.append({'x':x,'y':y,'w':252,'h':252});sampling.append(j)
target=out/'cast.webp';page.save(target,lossless=True,method=4)
record={'id':'hero001-cast','models':['common_skill_caocao_02_1','common_skill_caocao_02_1_ez'],'atlas':target.relative_to(GAME).as_posix(),'atlasSize':page.size,'atlasSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'frames':frames,'fps':24,'frameCount':53,'nativeTimelineRetained':True,'blendMode':'add','render':{'x':-128,'y':-200,'width':256,'height':256,'alpha':0.72},'sourceOriginalFrames':53,'sourceGeneratedFrames':len(generated),'originalPeakFrame':old_peak,'generatedPeakFrame':new_peak,'sampling':sampling,'generationJob':str(folder.relative_to(ROOT).as_posix()),'visualReview':'reviewed all 12 contact-sheet sample points; bull emblem, one wave pulse, decay to black; game verification pending'}
(GAME/'street-effects-data.js').write_text('window.StreetEffectsData='+json.dumps({'version':'0.24.0','effects':[record]},ensure_ascii=False,separators=(',',':'))+';\n','utf8')
(ROOT/'art-migration/effect-hero001-provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({k:record[k] for k in ['id','atlasSize','frameCount','sourceGeneratedFrames','originalPeakFrame','generatedPeakFrame']}))
