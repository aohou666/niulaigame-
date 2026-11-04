"""Extract original combat evidence; write planning artifacts without changing game data."""
import json
import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'combat-action-plan-20261022'
OUT.mkdir(parents=True, exist_ok=True)

def load_js(path):
    return json.loads(path.read_text(encoding='utf-8-sig').split('=', 1)[1].strip().rstrip(';'))

def read_model(path):
    data = path.read_bytes()
    if data[:3] != bytes([219, 189, 30]):
        raise ValueError('Unknown model container')
    length = struct.unpack_from('<I', data, 12)[0]
    raw = data[16:16+length]
    if data[4] == 1:
        raw = zlib.decompress(raw, -15)
    if raw[:4] == b'DBDT':
        size = struct.unpack_from('<I', raw, 8)[0]
        model = json.loads(raw[12:12+size].decode('utf-8'))
        start = 12 + size
        offsets = model['offset']
        frames = struct.unpack_from('<'+'h'*(offsets[9]//2), raw, start+offsets[8])
        timelines = struct.unpack_from('<'+'H'*(offsets[11]//2), raw, start+offsets[10])
        extracted = []
        for arm in model.get('armature', []):
            fps = arm.get('frameRate', model.get('frameRate', 24))
            actions = arm.get('actions', [])
            for anim in arm.get('animation', []):
                events = []
                if 'action' in anim:
                    pos = anim['action']
                    for i in range(timelines[pos+2]):
                        off = anim['offset'][2] + timelines[pos+5+i]
                        frame = frames[off]
                        for j in range(frames[off+1]):
                            idx = frames[off+2+j]
                            action = actions[idx]
                            events.append({'frame0':frame,'timeMs':round(frame/fps*1000,3), **action})
                extracted.append({'armature':arm['name'],'name':anim['name'],'fps':fps,
                                  'durationFrames':anim['duration'],'durationMs':round(anim['duration']/fps*1000,3),
                                  'scale':anim.get('scale',1), 'events':events})
        model['_extractedTimelines'] = extracted
        return model
    return json.loads(raw.decode('utf-8'))

def extract():
    names = {'HeroLO', 'SkillBaseLO', 'SkillEffectLO', 'HeroModelOffsetLO'}
    tables = {k: [] for k in names}
    with (ROOT / 'outputs/game-config-summary/staging/records.ndjson').open(encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            if row['tableName'] in names:
                tables[row['tableName']].append(json.loads(row['json']))
    heroes = load_js(ROOT / 'local_game/character-reskin-data.js')['heroes']
    skills = {int(s['id']): s for s in tables['SkillBaseLO']}
    effects = {int(s['id']): s for s in tables['SkillEffectLO']}
    gskills = json.loads((ROOT / 'local_game/resource/config/g_skill_96a92798.json').read_text(encoding='utf-8-sig'))
    records = []
    models = {}
    for sid, art in heroes.items():
        group = [h for h in tables['HeroLO'] if int(h['subType']) == int(sid)]
        group.sort(key=lambda h: (-bool(h.get('storyDesc1') or h.get('storyDesc2') or h.get('storyDesc3')), int(h.get('realStarLevel') or 0) != 0, int(h.get('realStarLevel') or 0), int(h['code'])))
        base = group[0] if group else None
        if base:
            model = base['model']
            if model not in models:
                files = sorted((ROOT/'local_game/resource/assets/model').glob(model+'_*.bin'))
                files = [p for p in files if p.stem.rsplit('_',1)[0] == model]
                try:
                    models[model] = {'path': str(files[0].relative_to(ROOT)), 'data': read_model(files[0])}
                except Exception as e:
                    models[model] = {'error': str(e)}
        for slot in ['normalSkill', 'actSkill']:
            skill = skills.get(int(base[slot])) if base else None
            perf = gskills.get(skill.get('modelId'), {}) if skill else {}
            effect_ids = json.loads(skill.get('skillEffect') or '[]') if skill else []
            records.append({'heroId': int(sid), 'art': art, 'base': base, 'slot': slot, 'skill': skill,
                            'performance': perf, 'effects': [effects.get(int(i), {'id':i}) for i in effect_ids],
                            'passives': [skills.get(int(base[k])) for k in ['posSkill1','posSkill2','posSkill3'] if base and base.get(k)],
                            'variants': [skills.get(int(h[slot])) for h in group if h.get(slot)]})
    (OUT/'original-evidence.json').write_text(json.dumps({'records':records,'models':models},ensure_ascii=False,indent=2),encoding='utf-8')
    for r in records:
        s=r['skill'] or {}; p=r['performance']
        print(f"{r['heroId']:02} {r['art']['name']} / {r['base']['name'] if r['base'] else '?'} {'普攻' if r['slot']=='normalSkill' else '大招'} | {s.get('name')} | {s.get('desc')} | {s.get('modelId')} | fly={p.get('meFlyConfig')} | custom={p.get('customAct')} | effects={','.join(p.keys())}")
    print('MODELS',len(models), [(k, v.get('error')) for k,v in models.items() if 'error' in v])
    first=next((v['data'] for v in models.values() if 'data' in v), {})
    print('MODEL_SAMPLE',json.dumps(first,ensure_ascii=False)[:4000])

if __name__ == '__main__':
    extract()
