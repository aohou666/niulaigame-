"""Pack all 5201 supplied idle frames for fewer decodes and shared GPU textures."""
from __future__ import annotations
import concurrent.futures,hashlib,json,math,time
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'local_game'
s=(GAME/'character-idle-data.js').read_text('utf8');data=json.loads(s.split('=',1)[1].strip().rstrip(';'))
def build(item):
 hid,cfg=item;x,y,w,h=cfg['crop'];folder=GAME/'assets/street/idle'/f'{int(hid):03d}';folder.mkdir(parents=True,exist_ok=True)
 result={};source_hash=hashlib.sha256();decoded=[]
 for name in cfg['files']:
  source=GAME/cfg['baseUrl']/name;source_hash.update(hashlib.sha256(source.read_bytes()).digest())
  with Image.open(source) as frame:
   frame=frame.convert('RGBA').crop((x,y,x+w,y+h));frame.putalpha(frame.getchannel('A').point(lambda a:0 if a<=8 else a));decoded.append(frame)
 for profile,edge in [('detail',384),('battle',192)]:
  scale=min(1,edge/max(w,h));fw=max(1,round(w*scale));fh=max(1,round(h*scale));tw=fw+4;th=fh+4
  cols=max(1,1024//tw);per_page=cols*max(1,2048//th);pages=[];frames=[]
  for start in range(0,len(decoded),per_page):
   subset=decoded[start:start+per_page];rows=math.ceil(len(subset)/cols);used_cols=min(cols,len(subset));page=Image.new('RGBA',(tw*used_cols,th*rows))
   for i,frame in enumerate(subset):
    px=(i%cols)*tw+2;py=(i//cols)*th+2
    resized=frame.resize((fw,fh),Image.Resampling.LANCZOS);page.paste(resized,(px,py))
    frames.append({'page':len(pages),'x':px,'y':py,'w':fw,'h':fh})
   target=folder/f'{profile}-{len(pages)}.webp';page.save(target,quality=92,method=4)
   pages.append({'url':target.relative_to(GAME).as_posix(),'width':page.width,'height':page.height,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
  result[profile]={'pages':pages,'frames':frames,'decodedBytes':sum(p['width']*p['height']*4 for p in pages)}
 return hid,{'profiles':result,'sourceSequenceSha256':source_hash.hexdigest(),'frameCount':len(decoded),'crop':cfg['crop']}
def main():
 start=time.monotonic()
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=dict(pool.map(build,data['heroes'].items()))
 payload={'version':'0.23.0','heroes':results}
 (GAME/'character-idle-atlas-data.js').write_text('window.CharacterIdleAtlasData='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n','utf8')
 report={'characters':len(results),'frames':sum(r['frameCount'] for r in results.values()),'seconds':round(time.monotonic()-start,2),'originalFramesModified':0,'profiles':{p:{'pages':sum(len(r['profiles'][p]['pages']) for r in results.values()),'compressedBytes':sum(f['bytes'] for r in results.values() for f in r['profiles'][p]['pages']),'maxDecodedCharacterBytes':max(r['profiles'][p]['decodedBytes'] for r in results.values())} for p in ['detail','battle']}}
 (ROOT/'art-migration/idle-atlas-build.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))
if __name__=='__main__':main()
