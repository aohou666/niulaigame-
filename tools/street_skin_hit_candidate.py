"""Independent skin hit reaction, full native motion reference; never auto publish."""
import json, hashlib, shutil, argparse
from pathlib import Path
from street_comfy import ROOT, COMFY, submit

def read(p): return json.loads(p.read_text('utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

parser=argparse.ArgumentParser();parser.add_argument('--revision',type=int,required=True);parser.add_argument('--reference',required=True);args=parser.parse_args()
name=f'skin100201-shouji-minimax-v{args.revision}'
assert not (ROOT/'art-migration/generation'/name).exists(), 'Collect existing job, never duplicate'
ref=ROOT/args.reference
meta=read(ref/'reference.json')
assert meta['manualReview']=='approved-original-reference' and meta['nativeFrames']==21
assert len(meta['sourceFiles'])==21
for row in meta['sourceFiles']: assert sha(ROOT/row['path'])==row['sha256']
guideFolder=ROOT/'art-migration/generation/skin100201-shouji-guide-official-v1'
guide=read(guideFolder/'qa.json');assert guide['manualReview']=='approved' and sha(ROOT/guide['image'])==guide['sha256']
idle=ROOT/'art-migration/references/skin100201-idle-minimax-v1/idle.png'
audit=ROOT/'art-migration/skin-migration/100201/native-events.json'
rows=[r for r in read(audit)['records'] if r['action']=='shouji']
assert len(rows)==2 and all(r['durationFrames']==21 and not r['events'] for r in rows)
g=read(ROOT/'art-migration/generation/skin100201-effect3-minimax-v3/workflow.json')
videoName=name+'-native-reference.mp4';shutil.copy2(ref/'native-reference.mp4',COMFY/'input'/videoName)
g['4']['inputs'].update(video=videoName,frame_load_cap=39)
for node,path in [('30',idle),('31',ROOT/guide['image'])]:
 filename=name+'-'+node+'.png';shutil.copy2(path,COMFY/'input'/filename)
 g[node]={'class_type':'LoadImage','inputs':{'image':filename}}
g['5']['inputs'].update(length=39,ref_image_size='max',prompt='''Create ONE complete hit reaction for the EXACT golden bull street-circus unicyclist of <Image 1>. <Image 2> shows his recoil pose and matching costume, not another character. <Video 1> is ONLY the original single hit-recoil-and-recovery motion reference, NOT the visual identity or props. Across this entire1.625second clip: start upright on unicycle, quickly flinch and bend upper body toward viewer left with shoulders/head recoiling once, then smoothly recover to the SAME upright balance and settle. Recoil begins immediately; no long frozen opening. Exactly ONE hit and ONE recovery, no repeated bobbing. Golden bull, black eye mask, short black hair, teal jacket purple lapels, cream ruffles, purple pants, teal shoes, SAME single unicycle, right hand(viewer left)holds ONE walnut and left hand(viewer right)holds exactly TWO red-white balls THROUGHOUT. No tossing or dropping props. Preserve body proportions and materials. Ground contact fixed, wheel stays in place with only small balancing rotation. Fixed full-body camera with all horns, hands, props and tire visible, black RGB0 background, no scene, text, trails, extra limbs, extra balls or hit flashes. 2.5D half-realistic half-cartoon absurd neighborhood style.''')
g['5']['inputs']['ref_images.ref_image_1']=['30',0]
g['5']['inputs']['ref_images.ref_image_2']=['31',0]
g['8']['inputs']['steps']=24;g['10']['inputs']['noise_seed']=2026103010020121
g['14']['inputs']['filename_prefix']='street-reskin/'+name
for node in g.values():
 if node['class_type']=='VHS_VideoCombine':node['inputs']['filename_prefix']='street-reskin/'+name+'-preview'
folder=submit(g,name,front=False)
shutil.copy2(ref/'native-reference.mp4',folder/'native-reference.mp4')
shutil.copy2(ref/'reference.json',folder/'reference.json')
(folder/'action-design.json').write_text(json.dumps({'skinCode':100201,'heroId':2,'action':'shouji','models':[r['model'] for r in rows],'nativeFrames':21,'nativeFps':30,'nativeAuditSha256':sha(audit),'sourceFrames':39,'guideSha256':guide['sha256'],'idleSha256':sha(idle),'referenceVideoSha256':sha(ref/'native-reference.mp4'),'scope':'Independent skin shouji only. Reference is retimed native motion; other actions remain incomplete.','manualReview':'pending','runtimeIntegrated':False,'requiredBeforeRuntime':['all39 full-frame visual review','one continuous recoil/recovery identity and props','native21-frame0.7s mapping','alpha and geometry','ordinary/EZ replay','actual battle hit trigger']},indent=2)+'\n','utf8')
