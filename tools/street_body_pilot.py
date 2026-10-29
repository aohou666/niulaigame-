"""Create a guided MiniMax body-motion pilot; key poses alone never count as animation."""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
from street_comfy import ROOT,COMFY,submit
base=ROOT/'art-migration/generation';hero='001';out=ROOT/'art-migration/references/body-001';out.mkdir(parents=True,exist_ok=True)
def candidate(name):
 folder=base/name;qa=json.loads((folder/'qa.json').read_text('utf8'))
 if qa['manualReview']!='approved':raise RuntimeError('Pose must be manually approved: '+name)
 return ROOT/qa['image']
def normalize(source,name):
 with Image.open(source) as image:
  image=image.convert('RGBA');bbox=image.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();image=image.crop(bbox)
  scale=min(620/image.height,700/image.width);image=image.resize((max(1,round(image.width*scale)),max(1,round(image.height*scale))),Image.Resampling.LANCZOS)
  foot=image.getchannel('A').crop((0,int(image.height*.88),image.width,image.height));pixels=list(foot.getdata());weight=sum(pixels);anchor=sum((i%image.width)*a for i,a in enumerate(pixels))/max(1,weight)
  x=max(12,min(756-image.width,round(384-anchor)));y=700-image.height;canvas=Image.new('RGBA',(768,768));canvas.alpha_composite(image,(x,y));target=out/(name+'.png');canvas.save(target)
  input_name='street_body001_'+name+'.png';shutil.copy2(target,COMFY/'input'/input_name)
  return input_name,{'source':str(source.relative_to(ROOT).as_posix()),'prepared':target.relative_to(ROOT).as_posix(),'foot':[round(x+anchor,2),700],'size':image.size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
idle,mi=normalize(ROOT/'local_game/assets/street/characters/001/portrait.png','idle')
attack,ma=normalize(candidate('hero001-attack-v3'),'attack')
skill,ms=normalize(candidate('hero001-skill-v2'),'skill')
prompt='''One fixed-camera production sprite animation of the exact golden anthropomorphic bull character shown in all guide frames, same short swept blond hair, black horns, purple muzzle, navy suit, white shirt and red tie. Maintain exact identity, clothing, proportions, lighting and foot placement. Pure black featureless background; entire body and both feet visible; no environment, no other character, no camera movement, no extra body parts, no weapons or VFX.
The five-second clip has TWO separate short actions with a clear idle pose between them. Frames 0-61: from the starting idle, perform one coherent rightward straight punch, reach the provided attack guide pose around frame28, smoothly recover to the original idle by frame61. Frames62-123: one confident emphatic fist gesture as a sound-wave skill casting action, reach the provided skill guide around frame92, recover to the exact original idle at the last frame. No repeated attacks, no walking or sliding across the frame. The game handles root translation separately. Use natural shoulder, elbow, wrist and body mechanics, cloth follow-through and subtle weight shift while keeping a fixed foot/root position. Premium tactile 2.5D semi-realistic semi-cartoon absurd neighborhood mobile-game art, crisp readable silhouette, no motion blur that hides anatomy.'''
g={
 '1':{'class_type':'UNETLoader','inputs':{'unet_name':'minimax_h3_fl2va_pruned_w4a8_mixed.safetensors','weight_dtype':'default'}},
 '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_32b_minimax_h3_int4_convrot.safetensors','type':'minimax','device':'default'}},
 '3':{'class_type':'VAELoader','inputs':{'vae_name':'minimax_h3_video_vae_fp16.safetensors'}},
 '4':{'class_type':'LoadImage','inputs':{'image':idle}},'5':{'class_type':'LoadImage','inputs':{'image':attack}},'6':{'class_type':'LoadImage','inputs':{'image':skill}},
 '7':{'class_type':'MiniMaxH3ImageToVideo','inputs':{'clip':['2',0],'vae':['3',0],'prompt':prompt,'width':512,'height':512,'length':124,'first_frame':['4',0],'last_frame':['4',0]}},
 '8':{'class_type':'MiniMaxH3AddGuide','inputs':{'positive':['7',0],'latent':['7',1],'frame_idx':28,'vae':['3',0],'image':['5',0]}},
 '9':{'class_type':'MiniMaxH3AddGuide','inputs':{'positive':['8',0],'latent':['7',1],'frame_idx':61,'vae':['3',0],'image':['4',0]}},
 '10':{'class_type':'MiniMaxH3AddGuide','inputs':{'positive':['9',0],'latent':['7',1],'frame_idx':92,'vae':['3',0],'image':['6',0]}},
 '11':{'class_type':'LoraLoaderModelOnly','inputs':{'model':['1',0],'lora_name':'minimax_h3_fl2v_lightx2v_turbo_8step_v1.0_resized_avg_rank_24_bf16.safetensors','strength_model':1}},
 '12':{'class_type':'MiniMaxH3DualClockSamplerT8','inputs':{'model':['11',0],'av_latent':['7',1],'steps':8,'shift_video':12,'shift_audio':3,'sampler_name':'dual_clock_euler','scheduler':'native_flow'}},
 '13':{'class_type':'BasicGuider','inputs':{'model':['12',0],'conditioning':['10',0]}},
 '14':{'class_type':'RandomNoise','inputs':{'noise_seed':202610290101}},
 '15':{'class_type':'SamplerCustomAdvanced','inputs':{'noise':['14',0],'guider':['13',0],'sampler':['12',1],'sigmas':['12',2],'latent_image':['7',1]}},
 '16':{'class_type':'LTXVSeparateAVLatent','inputs':{'av_latent':['15',0]}},
 '17':{'class_type':'VAEDecodeTiled','inputs':{'samples':['16',0],'vae':['3',0],'tile_size':256,'overlap':64,'temporal_size':16,'temporal_overlap':4}},
 '18':{'class_type':'SaveImage','inputs':{'images':['17',0],'filename_prefix':'street-reskin/hero001_body_pilot'}}}
folder=submit(g,'hero001-body-actions-minimax-v1',front=True)
(folder/'body-design.json').write_text(json.dumps({'heroId':1,'inputs':{'idle':mi,'attack':ma,'skill':ms},'actions':{'attack':{'sourceFrames':[0,61],'guideImpactFrame':28},'skill':{'sourceFrames':[62,123],'guideImpactFrame':92}},'nativeClockMustBeRetained':True,'manualVideoReview':'pending','runtimeIntegrated':False},ensure_ascii=False,indent=2),'utf8')
