"""Map each reviewed generated UI control to an exact original resource key and size."""
import colorsys,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game';out=GAME/'assets/street/ui/controls';out.mkdir(parents=True,exist_ok=True)
manifest=json.loads((GAME/'resource/default.res_49784.json').read_text('utf8'));originals={r['name']:r for r in manifest['resources']}
source=GAME/'assets/street/ui/controls-source.png';im=Image.open(source).convert('RGBA');icons=[]
for i in range(8):
 tile=im.crop((round((i%4)*im.width/4),round((i//4)*im.height/2),round((i%4+1)*im.width/4),round((i//4+1)*im.height/2)))
 mask=tile.getchannel('A').point(lambda a:255 if a>96 else 0);box=mask.getbbox();assert box
 tile=tile.crop(box);alpha=tile.getchannel('A').point(lambda a:0 if a<12 else a);tile.putalpha(alpha);icons.append(tile)
buttonSource=GAME/'assets/street/ui/primary-button-source.png';button=Image.open(buttonSource).convert('RGBA');button=button.crop(button.getchannel('A').point(lambda a:255 if a>96 else 0).getbbox())
buttons={'common_btn_4_png':.12,'common_btn_5_png':.02,'common_btn_an_png':None,'common_btn_hong_png':.02,'common_btn_huang_png':.12,'common_btn_lan3_png':.52,'common_btn_qing_png':.46,'common_btn_zise_png':.77}
iconKeys={'common_btn_fanhui_png':0,'common_btn_guanbi_png':1,'common_btn_dagou_png':2,'beibao_img_gou_png':2,'common_btn_jiantou_png':3,'common_btn_shengji_png':3,'common_btn_tianjia_png':4,'common_btn_tianjia_reschange_bh523_png':4,'common_btn_shandian_png':5,'common_btn_shanchu_png':1,'chouka_btn_qiehuan_png':6,'common_btn_qiehuan_new_png':6,'wujiang_icon_xiangqing_png':7}
records=[];contact=Image.new('RGB',(1000,((len(buttons)+len(iconKeys)+3)//4)*170),'#55656a');draw=ImageDraw.Draw(contact)
for i,key in enumerate(list(buttons)+list(iconKeys)):
 row=originals[key];original=GAME/'resource'/row['url'];size=Image.open(original).size;target=Image.new('RGBA',size)
 if key in buttons:
  tile=button.copy();arr=np.asarray(tile).copy();rgb=arr[:,:,:3].astype(np.float32)/255;mx=rgb.max(2);mn=rgb.min(2);teal=(rgb[:,:,1]>rgb[:,:,0]*1.2)&(rgb[:,:,2]>rgb[:,:,0]*1.2)&(mx-mn>.08)
  hue=buttons[key]
  if hue is None:
   lum=rgb.mean(2);rgb[teal]=np.stack([lum*.65,lum*.8,lum*.82],2)[teal]
  else:
   tint=np.array(colorsys.hsv_to_rgb(hue,.45 if hue==.12 else .58,1));brightness=.55+.45*mx[teal];rgb[teal]=brightness[:,None]*tint[None,:]
  arr[:,:,:3]=np.clip(rgb*255,0,255).astype(np.uint8);tile=Image.fromarray(arr).resize(size,Image.Resampling.LANCZOS);target.alpha_composite(tile)
 else:
  tile=icons[iconKeys[key]].copy();tile.thumbnail((size[0]-2,size[1]-2),Image.Resampling.LANCZOS);target.alpha_composite(tile,((size[0]-tile.width)//2,(size[1]-tile.height)//2))
  if key=='common_btn_qiehuan_new_png':
   d=ImageDraw.Draw(target);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',15);d.text((size[0]/2,size[1]-1),'切换',font=font,anchor='mb',fill='#fff5dc',stroke_width=2,stroke_fill='#173b3a')
 path=out/(key+'.png');target.save(path)
 records.append({'originalKey':key,'originalPath':'resource/'+row['url'],'originalSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'targetKey':'street_ui_'+key,'targetPath':path.relative_to(GAME).as_posix(),'targetSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':size,'status':'prepared-unreviewed','generation':{'provider':'official-built-in-image_gen','source':('assets/street/ui/primary-button-source.png' if key in buttons else 'assets/street/ui/controls-source.png'),'variant':'semantic-color' if key in buttons else 'individual-control'}})
 x=(i%4)*250;y=(i//4)*170;preview=target.copy();preview.thumbnail((240,110));contact.paste(preview,(x+(250-preview.width)//2,y),preview);draw.text((x+5,y+115),key.replace('common_btn_',''),fill='white');draw.text((x+5,y+138),str(size),fill='white')
for r in records:r['generation']['sourceSha256']=hashlib.sha256((GAME/r['generation']['source']).read_bytes()).hexdigest();r['generation']['prompt']='art-migration/prompts/primary-button.txt' if r['originalKey'] in buttons else 'art-migration/prompts/controls.txt'
datafile=GAME/'street-art-data.js';data=json.loads(datafile.read_text('utf8').split('=',1)[1].strip().rstrip(';'));data['version']='0.26.0';data['resources']=[r for r in data['resources'] if r['originalKey'] not in list(buttons)+list(iconKeys)]+records;datafile.write_text('window.StreetArtData='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n','utf8')
contact.save(ROOT/'outputs/street-reskin/common-buttons-replacement.jpg',quality=95);print(json.dumps({'controls':len(records),'bytes':sum((GAME/r['targetPath']).stat().st_size for r in records)}))
