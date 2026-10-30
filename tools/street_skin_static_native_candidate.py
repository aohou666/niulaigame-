"""Compose native-sized static candidates entirely from new art and new text."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fit(image,size,margin=1):
 image=image.copy();box=image.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox();assert box;image=image.crop(box);image.thumbnail((size[0]-2*margin,size[1]-2*margin),Image.Resampling.LANCZOS);out=Image.new('RGBA',size);out.alpha_composite(image,((size[0]-image.width)//2,(size[1]-image.height)//2));return out
def nine_slice(image,size):
 out=Image.new('RGBA',size);xs=[0,14,121,135];ys=[0,12,56,82];xx=[0,14,size[0]-14,size[0]];yy=[0,12,size[1]-26,size[1]]
 for y in range(3):
  for x in range(3):
   tile=image.crop((xs[x],ys[y],xs[x+1],ys[y+1])).resize((xx[x+1]-xx[x],yy[y+1]-yy[y]),Image.Resampling.LANCZOS);out.paste(tile,(xx[x],yy[y]))
 return out
def caption(image,text,y,fontSize):
 font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',fontSize);d=ImageDraw.Draw(image);b=d.textbbox((0,0),text,font=font,stroke_width=1);d.text(((image.width-(b[2]-b[0]))/2-b[0],y-b[1]),text,font=font,fill='#fff3d3',stroke_width=1,stroke_fill='#23312b')
def main():
 out=ROOT/'art-migration/generation/skin100201-native-static-fit-v1';assert not out.exists();out.mkdir()
 assets=GAME/'assets/street/skins/100201/static-native-trial-v1';assets.mkdir(parents=True,exist_ok=True)
 avatarSource=ROOT/'art-migration/generation/skin100201-native-avatar-official-v1/official-source.png';halfSource=ROOT/'art-migration/generation/skin100201-native-half-official-v1/official-source.png';frameSource=ROOT/'art-migration/generation/skin100201-native-card-frame-official-v1/official-source.png';bodySource=ROOT/'art-migration/generation/skin100201-native-outfit-static-official-v2/official-source.png'
 avatar=Image.open(avatarSource).convert('RGBA');half=Image.open(halfSource).convert('RGBA');body=Image.open(bodySource).convert('RGBA');frame=Image.open(frameSource).convert('RGBA').resize((135,82),Image.Resampling.LANCZOS)
 card=Image.new('RGBA',(135,82));portrait=fit(avatar.crop((230,325,1150,1180)),(111,46));card.alpha_composite(portrait,(12,10));card.alpha_composite(frame);caption(card,'夜市杂耍掌柜',61,12)
 gallery=Image.new('RGBA',(169,228));gallery.alpha_composite(fit(body,(141,186)),(14,12));gallery.alpha_composite(nine_slice(frame,(169,228)));caption(gallery,'夜市杂耍掌柜',207,14)
 images={'head1_hero_002_04_png':fit(avatar,(111,111)),'head_hero_002_04_png':fit(avatar,(97,98)),'half_skin_002_1_png':fit(half,(221,130)),'wujiang_img_pifukasmy_png':card,'mjl_img_simayi_png':gallery}
 old=json.loads((GAME/'character-art-data.js').read_text('utf8').split('=',1)[1].strip().rstrip(';'));bindings={}
 for key,image in images.items():
  path=assets/(key+'.png');image.save(path)
  if key in old['heroes']['2']['bindings']:
   binding=dict(old['heroes']['2']['bindings'][key]);assert binding['skinCode']==100201;binding.update(url=path.relative_to(GAME).as_posix(),targetSha256=sha(path),review='candidate-native-static-fields',source=halfSource.relative_to(ROOT).as_posix() if key.startswith('half') else avatarSource.relative_to(ROOT).as_posix());binding['sourceSha256']=sha(ROOT/binding['source']);inputs=[ROOT/binding['source']]+([frameSource] if key.startswith('wujiang') else []);binding['sourceInputs']=[{'path':v.relative_to(ROOT).as_posix(),'sha256':sha(v)} for v in inputs];binding.pop('nativeRuntimeAuditPath',None);binding.pop('nativeRuntimeAuditSha256',None);bindings[key]=binding
 galleryPath=assets/'mjl_img_simayi_png.png';resources=[{'originalKey':'mjl_img_simayi_png','originalPath':'resource/assets/shuzhi/tujian/mjl_img_simayi_c038715d.png','targetKey':'street_skin100201_native_gallery_trial_png','targetPath':galleryPath.relative_to(GAME).as_posix(),'targetSha256':sha(galleryPath),'type':'image','size':[169,228],'originalSha256':sha(GAME/'resource/assets/shuzhi/tujian/mjl_img_simayi_c038715d.png'),'sourceInputs':[{'path':v.relative_to(ROOT).as_posix(),'sha256':sha(v)} for v in [bodySource,frameSource]],'skinCode':100201,'review':'candidate-only'}]
 candidate={'skinCode':100201,'bindings':bindings,'resources':resources,'text':{'name':'夜市杂耍掌柜','desc':'铜铃响过夜市，核桃与糖球轮番登场。可激活老八皮肤“夜市杂耍掌柜”。'},'runtimeIntegrated':False,'completeSkin':False,'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [avatarSource,halfSource,frameSource,bodySource]],'scope':'Four native static fields plus gallery card. Brand-new frame/typography; no old frame or baked text copied. Preview movie remains separately pending.'};(out/'candidate.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n','utf8')
 sheet=Image.new('RGB',(900,650),'#233238');draw=ImageDraw.Draw(sheet)
 for i,(key,image) in enumerate(images.items()):
  x=i%3*300;y=i//3*320;preview=image.resize((image.width*2,image.height*2),Image.Resampling.NEAREST) if image.height<150 else image;sheet.paste(preview,(x,y),preview);draw.text((x+2,y+270),key,fill='white')
 sheet.save(out/'native-size-preview.jpg');print(json.dumps({'staticBindings':len(bindings),'gallery':1,'runtimeIntegrated':False}))
if __name__=='__main__':main()
