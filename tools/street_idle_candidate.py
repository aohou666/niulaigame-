"""Generate a reviewed candidate idle without changing any live portrait/atlas."""
import argparse, hashlib, json, shutil
from pathlib import Path
from street_comfy import ROOT, COMFY, submit

p=argparse.ArgumentParser()
p.add_argument('body_job')
p.add_argument('--revision',type=int,required=True)
a=p.parse_args()
source=ROOT/'art-migration/generation'/a.body_job
design=json.loads((source/'body-design.json').read_text('utf8'))
assert not design.get('skinCode'),'Use an explicit independent-skin workflow; base-hero naming is unsafe here'
hid=design['heroId']
name=f'hero{hid:03}-idle-minimax-v{a.revision}'
assert not (ROOT/'art-migration/generation'/name).exists(), 'Existing job must be polled, not resubmitted'
reference=ROOT/design['inputs']['idle']['prepared']
assert hashlib.sha256(reference.read_bytes()).hexdigest()==design['inputs']['idle']['sha256']
g=json.loads((source/'workflow.json').read_text('utf8'))
# Use only first/last identity conditioning; no action-guide poses in an idle.
for node in ['5','6','8','9','10']:
    g.pop(node,None)
g['13']['inputs']['conditioning']=['7',0]
g['7']['inputs']['first_frame']=['4',0]
g['7']['inputs']['last_frame']=['4',0]
g['7']['inputs']['length']=124
g['7']['inputs']['prompt']='One locked-camera 124-frame idle animation of the EXACT reference bull character, tactile 2.5D semi-realistic semi-cartoon neighborhood style. Full character and complete held object stay within the same safe margins. Gentle continuous breathing in shoulders and torso, a subtle natural blink, then return to exact first pose for a seamless loop. Feet remain planted, no walking, no gestures, no camera movement. Preserve face, outfit, original props and grip throughout. Pure matte black background and constant neutral illumination. No extra light effects, smoke, particles, duplicate limbs or objects.'
if hid==60:
    g['7']['inputs']['prompt']+=' RIGHT hand holds the same upright bamboo banner motionless with the flat cloth facing camera. The four black Chinese characters must remain exactly 今 日 卜 卦 vertically, last character left圭/right卜. Keep their strokes fixed and legible throughout; never turn, fold or wave the sign. LEFT hand stays low. Preserve sunglasses, gray robe, divination sticks and red belt ring.'
filename=f'street_idle_candidate_{hid:03}_v{a.revision}.png'
shutil.copyfile(reference,COMFY/'input'/filename)
g['4']['inputs']['image']=filename
g['14']['inputs']['noise_seed']=202610300000+hid+a.revision*1000
g['18']['inputs']['filename_prefix']=f'street-reskin/hero{hid:03}_idle_candidate'
g['20']['inputs']['filename_prefix']=f'street-reskin/hero{hid:03}_idle_candidate_video'
folder=submit(g,name,front=False)
(folder/'idle-design.json').write_text(json.dumps({'heroId':hid,'length':124,'inputs':{'idle':design['inputs']['idle']},'motionSegments':{'daiji':[0,123]},'referenceBodyJob':a.body_job,'manualVideoReview':'pending','runtimeIntegrated':False},indent=2)+'\n','utf8')
