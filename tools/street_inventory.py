"""Inventory every original art resource and every character without claiming replacement."""
from __future__ import annotations
import argparse, collections, hashlib, json, struct, time
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'local_game'
OUT = ROOT / 'art-migration'

def payload(name):
    text = (GAME / name).read_text('utf-8')
    return json.loads(text.split('=', 1)[1].strip().rstrip(';'))

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def category(path):
    p = path.lower()
    if '/character_idle/' in p: return 'character-idle'
    if p.startswith('reskin/'): return 'character-portrait'
    if '/model/' in p: return 'model-animation'
    if '/effect/' in p or '/effect_f/' in p or '/ui_effect/' in p: return 'effect-animation'
    if '/font/' in p or p.endswith(('.fnt','.ttf')): return 'font-text'
    if '/loading/' in p: return 'loading'
    if '/sound/' in p: return 'sound'
    if '/map/' in p or '/slg' in p: return 'map-building'
    if '/ui/' in p: return 'ui'
    return 'other'

def main():
    OUT.mkdir(exist_ok=True)
    manifest = json.loads((GAME/'resource/default.res_49784.json').read_text('utf-8'))
    refs = collections.defaultdict(list)
    for row in manifest['resources']:
        refs['resource/'+row['url']].append({'name':row['name'],'type':row['type']})
    files = set()
    for folder in ['resource','reskin','assets/character_idle']:
        files.update(p for p in (GAME/folder).rglob('*') if p.is_file())
    previous = {}
    if (OUT/'assets.jsonl').exists():
        previous = {r['path']:r for r in map(json.loads,(OUT/'assets.jsonl').read_text('utf-8').splitlines())}
    assets = []
    image_ext = {'.png','.jpg','.jpeg','.webp','.gif','.bmp'}
    included = image_ext | {'.bin','.dbbin','.json','.fnt','.ttf','.mp3','.wav','.ogg'}
    for p in sorted(files):
        if p.suffix.lower() not in included: continue
        rel = p.relative_to(GAME).as_posix()
        row = {'path':rel,'category':category(rel),'bytes':p.stat().st_size,'sha256':sha(p),'references':refs.get(rel,[])}
        if p.suffix.lower() in image_ext:
            try:
                with Image.open(p) as im:
                    row.update(width=im.width,height=im.height,mode=im.mode,alpha='A' in im.getbands())
            except Exception as e: row['error']=str(e)
        elif p.suffix.lower() in {'.bin','.dbbin'}:
            row['containerMagic']=p.read_bytes()[:16].hex()
        old = previous.get(rel,{})
        # Existing portraits and idle frames are inputs, not newly completed work.
        row['status']=old.get('status','existing-input' if row['category'].startswith('character-') else 'pending')
        for k in ['replacement','generation','runtimeVerification','visualReview']:
            if k in old: row[k]=old[k]
        assets.append(row)
    with (OUT/'assets.jsonl').open('w',encoding='utf-8') as f:
        for row in assets:f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
    heroes=payload('character-reskin-data.js')['heroes']; idles=payload('character-idle-data.js')['heroes']
    characters=[]
    for hid,h in heroes.items():
        idle=idles.get(hid)
        missing=[] if not idle else [n for n in idle['files'] if not (GAME/idle['baseUrl']/n).exists()]
        characters.append({'id':int(hid),'originalName':h['originalName'],'name':h['name'],'target':hid in idles,'portrait':h['portrait'],'portraitExists':bool(h['portrait']) and (GAME/h['portrait']).is_file(),'idleFrames':len(idle['files']) if idle else 0,'missingIdleFrames':missing,'actions':{'idle':'existing-input' if idle else 'original','attack':'original','hit':'original','skill':'original','move':'original','death':'original'},'story':'requires-review','skinVariants':'requires-inventory','avatar':'requires-review','complete':False})
    (OUT/'characters.json').write_text(json.dumps(characters,ensure_ascii=False,indent=2)+'\n','utf-8')
    missing=[{'path':p,'references':v} for p,v in refs.items() if not (GAME/p).exists()]
    summary={'timestampUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'assets':len(assets),'categories':dict(collections.Counter(r['category'] for r in assets)),'statuses':dict(collections.Counter(r['status'] for r in assets)),'manifestEntries':len(manifest['resources']),'missingManifestFiles':missing,'characterSlots':len(characters),'targetCharacters':sum(r['target'] for r in characters),'existingIdleFrames':sum(r['idleFrames'] for r in characters),'missingIdleFrames':sum(len(r['missingIdleFrames']) for r in characters),'completeCharacters':sum(r['complete'] for r in characters)}
    (OUT/'inventory-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='missingManifestFiles'},ensure_ascii=False))

if __name__=='__main__':main()
