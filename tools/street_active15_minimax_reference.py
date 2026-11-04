"""Request local MiniMax motion/material guidance; never auto-approve its frames."""
import json,hashlib,shutil,subprocess
from pathlib import Path
from street_comfy import ROOT,COMFY,submit,request
queue=request('/queue');assert not queue.get('queue_running') and not queue.get('queue_pending'),'Leave existing Comfy work undisturbed'
frames=ROOT/'art-migration/generation/skin100201-active15-native-v2/native'
video=ROOT/'outputs/street-reskin/skin100201-active15-original62.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-start_number','0','-i',str(frames/'baseline-common_newskill_simayi_01_1_bin-%02d.png'),'-frames:v','62','-vf','scale=512:512','-c:v','libx264','-pix_fmt','yuv420p','-crf','16',str(video)],check=True)
inputVideo=COMFY/'input/street_skin100201_active15_original62.mp4';shutil.copy2(video,inputVideo)
guide=ROOT/'art-migration/generation/skin100201-active15-official-v1/impact3.png'
inputGuide=COMFY/'input/street_skin100201_active15_new_walnut.png';shutil.copy2(guide,inputGuide)
g=json.loads((ROOT/'art-migration/generation/skin100201-impact-minimax-v1/workflow.json').read_text('utf8'))
g['4']['inputs'].update(video=inputVideo.name,frame_load_cap=62,force_rate=24)
g['15']['inputs']['image']=inputGuide.name
prompt='''Generate a NEW isolated physical walnut-smash game VFX for the absurd contemporary neighborhood nightmarket juggler. Use <Image 1> as the EXACT new tactile brown walnut-shell/ivory flour/copper spark material and palette. <Video 1> supplies ONLY original motion direction, spatial rhythm and burst-decay timing, NEVER its old purple/red/rainbow colors. A whole deeply grooved walnut flies from left toward center, ONE impact splits it into brown shell pieces with compact ivory flour flash, chips spread and settle, sparse tiny copper sparks fade fully to black. No repeated impact or regeneration of shell pieces; late frames smoothly decay and become empty. Semi-realistic semi-cartoon2.5D game art. Fixed locked camera, pure BLACK RGB0,0,0 background, no floor/environment/text/character. Keep all visible action in central60% of frame with generous safety margins, no long offscreen jet. Five-second24fps guidance clip; one anticipation, one peak, complete decay. Do not copy old magical confetti, red aura or violet glow. This generated clip is a motion/material reference and will be reviewed before any game use.'''
g['5']['inputs'].update(prompt=prompt,length=124,width=512,height=512)
g['10']['inputs']['noise_seed']=202610300115
g['14']['inputs']['filename_prefix']='street-reskin/skin100201_active15_reference'
folder=submit(g,'skin100201-active15-minimax-v1')
shutil.copy2(video,folder/'native-reference.mp4')
proof={'purpose':'Local MiniMax motion/material guidance only; no automatic approval or production binding.','nativeReferenceFrames':62,'nativeReferenceFPS':24,'nativeReferenceSeconds':62/24,'referenceNotRetimed':True,'referenceVideoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'artGuidePath':guide.relative_to(ROOT).as_posix(),'artGuideSha256':hashlib.sha256(guide.read_bytes()).hexdigest(),'prompt':prompt,'generatedFramesRequested':124,'manualReview':'pending','productionIntegrated':False}
(folder/'effect-design.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),'utf8')
