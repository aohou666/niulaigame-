"""Validate explicit multi-hit source choreography against frozen native events.

This proves planning coverage only, never that a generated clip contains hits.
"""
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def validate(plan, audit):
    if not audit.get('complete'):
        raise ValueError('Complete native event audit required')
    records={(r['model'],r['action']):r for r in audit['records']}
    expected={key for key in records if key[0].startswith(f"hero_{plan['heroId']:03}_")}
    provided={(model,action) for model,actions in plan['models'].items() for action in actions}
    if provided != expected:
        raise ValueError('Every native model/action requires explicit coverage')
    for model,actions in plan['models'].items():
        for action,entry in actions.items():
            native=records[(model,action)]
            hits=sorted({e['frame0'] for e in native['events'] if e['name'] in ('pia','zd')})
            marks={int(k):v for k,v in entry['eventAnchors'].items()}
            if sorted(marks)!=hits:
                raise ValueError(f'{model}/{action}: native hit coverage mismatch')
            begin,end=entry['sourceFrames']
            if not 0<=begin<end<plan['length']:
                raise ValueError('Invalid source action interval')
            anchors=[marks[k] for k in hits]
            if any(not begin<x<end for x in anchors) or anchors!=sorted(set(anchors)):
                raise ValueError('Hits need distinct chronological interior source frames')
            resets=entry.get('recoveryFrames',[])
            if any(not any(left<r<right for r in resets) for left,right in zip(anchors,anchors[1:])):
                raise ValueError('Each repeated hit requires an intervening recovery pose')
    schedule=plan['guideSchedule']
    frames=[s['frame'] for s in schedule]
    if frames!=sorted(set(frames)) or frames[0]!=0 or frames[-1]!=plan['length']-1:
        raise ValueError('Guide schedule must be chronological with both endpoints')
    mapping={s['frame']:s['image'] for s in schedule}
    if any(k not in ('idle','attack','skill') for k in mapping.values()):
        raise ValueError('Unknown guide identity')
    for actions in plan['models'].values():
        for action,entry in actions.items():
            pose='attack' if action=='gongji' else 'skill'
            if any(mapping.get(v)!=pose for v in entry['eventAnchors'].values()):
                raise ValueError('Every planned hit must have the corresponding pose guide')
            if any(mapping.get(v)!='idle' for v in entry.get('recoveryFrames',[])):
                raise ValueError('Recovery must have an explicit idle guide')
    return {'pass':True,'scope':'Choreography coverage only; generated frame-by-frame review still required',
            'heroId':plan['heroId'],'modelActions':len(provided)}

def apply_choreography(graph, plan, rows):
    """Condition real model synthesis; never manufacture output frames."""
    for node in list(graph):
        if node in ('8','9','10') or int(node)>=21:
            del graph[node]
    previous='7'
    for index,guide in enumerate(plan['guideSchedule'][1:-1],100):
        key=str(index)
        graph[key]={'class_type':'MiniMaxH3AddGuide','inputs':{
            'positive':[previous,0],'latent':['7',1],
            'frame_idx':guide['frame'],'vae':['3',0],
            'image':[{'idle':'4','attack':'5','skill':'6'}[guide['image']],0]}}
        previous=key
    graph['13']['inputs']['conditioning']=[previous,0]
    graph['7']['inputs']['length']=plan['length']
    sequence='; '.join(f"frame {g['frame']}: {g['image']} posture" for g in plan['guideSchedule'])
    graph['7']['inputs']['prompt']=(
        'Locked-camera full-body studio rehearsal of the EXACT reference character. '
        'Tactile 2.5D semi-realistic semi-cartoon neighborhood style, matte black background. '
        'Same face, costume, horns, hands, feet and original props throughout. '
        'Entire body and props remain within safe margins. '+plan['physicalSequence']+
        ' Required chronological movement landmarks: '+sequence+'. '
        'Every repeated extension must have its OWN real preparation, extension and recovery. '
        'Animate continuously through intermediate joint positions, no held-pose cuts, dissolves or teleporting. '
        'Attack gesture: '+rows['attack']['bodyDesign']+'. Skill gesture: '+rows['skill']['bodyDesign']+'. '
        'Persistent objects and hand assignments: '+rows['attack']['weaponObservation']+'. '
        'Face screen RIGHT throughout. Feet stay grounded, no camera movement, new objects, '
        'flashes, particles or light trails. Natural cloth motion, constant illumination.')
    return graph

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);a=p.parse_args()
    print(json.dumps(validate(json.loads(a.plan.read_text('utf8')),
                             json.loads((ROOT/'art-migration/native-action-events.json').read_text('utf8')))))
