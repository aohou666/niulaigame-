"""Render original RGB with generated alpha, never infer visual approval."""
import argparse,json,math
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();folder=root/'art-migration/generation'/a.name;job=json.loads((folder/'job.json').read_text('utf8'))
designFile=next((folder/name for name in ['body-design.json','action-design.json','idle-design.json'] if (folder/name).exists()),None)
assert designFile, 'Missing explicit motion design scope'
design=json.loads(designFile.read_text('utf8'))
assert len(design['sourceFrameOrder'])==len(job.get('outputs',[]))>0, 'Incomplete matte sequence must not silently truncate review'
out=root/'outputs/street-reskin'/a.name;out.mkdir(exist_ok=True);images=[]
for raw,entry in zip(design['sourceFrameOrder'],job['outputs']):
 im=Image.open(root/raw).convert('RGB').convert('RGBA');im.putalpha(Image.open(root/entry['path']).getchannel('A'));images.append(im)
for label,indices,columns,tw,th in [('all-1',range(min(64,len(images))),8,136,136),('all-2',range(64,len(images)),8,136,136),('large',[round(i*(len(images)-1)/15) for i in range(16)],4,256,256)]:
 indices=list(indices)
 if not indices:continue
 canvas=Image.new('RGB',(columns*tw,math.ceil(len(indices)/columns)*th),'#647b7c');draw=ImageDraw.Draw(canvas)
 for i,n in enumerate(indices):
  im=images[n].copy();im.thumbnail((tw-4,th-22));x=i%columns*tw+(tw-im.width)//2;y=i//columns*th;canvas.paste(im,(x,y),im);draw.text((i%columns*tw+5,y+th-18),str(n),fill='white')
 canvas.save(out/(label+'.jpg'),quality=95)
print(out)
